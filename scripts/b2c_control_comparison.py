"""
B2c: ATAC L2_DIFF control comparison at all five CF GWAS modifier loci.

For each locus, GW-significant variants (p < 5e-8) are compared against
an equal number of matched control variants drawn from non-GW-sig clean
SNVs in the same locus window. Matching is stratified by distance to the
nearest annotated gene at each locus (four quantile bins, Ensembl REST
hg38 coordinates). No control position is within 1 kb of any GW-sig
variant, and no position is used twice.

GW-sig ATAC scores are loaded from B2_scored_variants.csv (not re-scored).
Control ATAC scores are computed here.

Locus tissues (ATAC):
  3q29  → UBERON:0006920  esophagus mucosa
  5p15  → UBERON:0002048  lung
  6p21  → CL:0000236      B lymphocyte
  11p13 → UBERON:0002048  lung
  Xq23  → UBERON:0002048  lung

Exclusion: 10 variants in B1_gnomad_absent_nonsex_loci.csv are absent
from the GW-sig set (see B2c run report). All are REF_ok / clean_rs;
exclusion is by gnomAD absence (artefact), not orientation.

Test: Mann-Whitney U (two-sided) + rank-biserial effect size per locus.
Positive rank-biserial means GW-sig > control.

Usage:
    .venv/bin/python scripts/b2c_control_comparison.py
    .venv/bin/python scripts/b2c_control_comparison.py --dry-run

Outputs:
    results/gwas_modifiers/B2c_control_scores.csv  — one row per control variant
    results/gwas_modifiers/B2c_summary.csv          — per-locus statistics
"""

import argparse
import datetime
import os
import sys
import time

import numpy as np
import pandas as pd
import requests
from scipy import stats
from dotenv import load_dotenv

import alphagenome as _ag
AG_VERSION = getattr(_ag, "__version__", "unknown")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))
API_KEY = os.environ.get("ALPHAGENOME_API_KEY", "")
if not API_KEY:
    sys.exit("ERROR: Set ALPHAGENOME_API_KEY in .env")

from alphagenome.data import genome
from alphagenome.models import dna_client
from alphagenome.models.variant_scorers import (
    CenterMaskScorer, AggregationType, tidy_scores,
)
from alphagenome.models.dna_output import OutputType
import grpc

OUT_DIR       = os.path.join(ROOT, "results/gwas_modifiers")
B1_GZ         = os.path.join(OUT_DIR, "B1_lifted_hg38.csv.gz")
ABSENT_CSV    = os.path.join(OUT_DIR, "B1_gnomad_absent_nonsex_loci.csv")
SCORED_CSV    = os.path.join(OUT_DIR, "B2_scored_variants.csv")
CTRL_OUT_CSV  = os.path.join(OUT_DIR, "B2c_control_scores.csv")
SUMM_OUT_CSV  = os.path.join(OUT_DIR, "B2c_summary.csv")
CKPT_CSV      = os.path.join(OUT_DIR, ".B2c_control_ckpt.csv")

HALF      = dna_client.SEQUENCE_LENGTH_1MB // 2
EXCL_RADIUS = 1_000   # bp; control must be ≥1 kb from every GW-sig position
N_BINS    = 4         # distance quantile bins for stratified matching
RNG_SEED  = 42

LOCUS_CONFIG = {
    "3q29":  {"tissue": "UBERON:0006920", "genes": ["MUC4", "MUC20"]},
    "5p15":  {"tissue": "UBERON:0002048", "genes": ["SLC9A3"]},
    "6p21":  {"tissue": "CL:0000236",     "genes": ["HLA-DRA"]},
    "11p13": {"tissue": "UBERON:0002048", "genes": ["EHF", "APIP"]},
    "Xq23":  {"tissue": "UBERON:0002048", "genes": ["AGTR2", "SLC6A14"]},
}

ATAC_SCORER = CenterMaskScorer(
    requested_output=OutputType.ATAC,
    width=501,
    aggregation_type=AggregationType.L2_DIFF,
)


# ── Gene boundary lookup ───────────────────────────────────────────────────────

def fetch_gene_boundaries(gene_names: list[str]) -> dict[str, tuple[str, int, int]]:
    """
    Query Ensembl REST (GRCh38) for each gene's chromosome, start, and end.

    Returns {gene_name: (chrom_with_chr_prefix, start, end)}.
    """
    out: dict[str, tuple[str, int, int]] = {}
    for gene in gene_names:
        url = (
            f"https://rest.ensembl.org/lookup/symbol/homo_sapiens/{gene}"
            f"?content-type=application/json&expand=0"
        )
        for attempt in range(4):
            try:
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                d = r.json()
                chrom = d["seq_region_name"]
                if not chrom.startswith("chr"):
                    chrom = "chr" + chrom
                out[gene] = (chrom, int(d["start"]), int(d["end"]))
                break
            except Exception as exc:
                if attempt == 3:
                    raise RuntimeError(
                        f"Ensembl REST failed for {gene}: {exc}"
                    ) from exc
                time.sleep(2 ** attempt)
        time.sleep(0.35)  # Ensembl rate limit: ≤15 req/s
    return out


def dist_to_nearest_gene(
    pos: int,
    chrom: str,
    gene_bounds: list[tuple[str, int, int]],
) -> int:
    """
    Distance in bp from pos to the nearest gene body in gene_bounds.

    Returns 0 if pos falls within any gene body.
    Returns -1 if gene_bounds is empty or no gene is on the same chromosome.
    """
    min_dist = float("inf")
    for gc, gs, ge in gene_bounds:
        if chrom != gc:
            continue
        if gs <= pos <= ge:
            return 0
        min_dist = min(min_dist, abs(pos - gs), abs(pos - ge))
    return int(min_dist) if min_dist != float("inf") else -1


# ── Control sampling ───────────────────────────────────────────────────────────

def sample_matched_controls(
    candidates: pd.DataFrame,
    gws_variants: pd.DataFrame,
    n: int,
    excl_radius: int = EXCL_RADIUS,
    n_bins: int = N_BINS,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """
    Sample n control variants matched to gws_variants by distance-to-gene.

    Matching is stratified: the GW-sig distance distribution is divided
    into n_bins quantile bins and controls are sampled proportionally from
    each bin. If a bin is under-represented in the candidate pool, the
    deficit is filled from the next-nearest bins (no silent truncation).

    Parameters
    ----------
    candidates : pd.DataFrame
        Non-GW-sig clean SNVs in the locus window. Must have columns:
        SNP, chrom_hg38, a_pos, api_ref, api_alt, orientation,
        dist_to_nearest_gene.
    gws_variants : pd.DataFrame
        GW-sig variants. Must have dist_to_nearest_gene column.
    n : int
        Number of controls to sample (should equal len(gws_variants)).
    excl_radius : int
        Controls within this many bp of any GW-sig position are excluded.
    n_bins : int
        Number of quantile bins for stratified distance matching.
    rng : np.random.Generator | None
        Random generator for reproducibility.

    Returns
    -------
    pd.DataFrame of n sampled control variants (or fewer if the pool is
    too small; the caller should check and log the shortfall).
    """
    if rng is None:
        rng = np.random.default_rng(seed=RNG_SEED)

    # --- Exclusion zone -------------------------------------------------
    gws_pos_arr = np.array(
        sorted(gws_variants["a_pos"].dropna().astype(int))
    )
    cand_pos_arr = candidates["a_pos"].values.astype(int)
    # Vectorised: min distance from each candidate to any GW-sig position
    diffs = np.abs(cand_pos_arr[:, None] - gws_pos_arr[None, :])
    min_diffs = diffs.min(axis=1)
    eligible = candidates[min_diffs >= excl_radius].copy()

    if eligible.empty:
        return pd.DataFrame(columns=candidates.columns)

    # --- Quantile bins from GW-sig distances ----------------------------
    gws_dists = gws_variants["dist_to_nearest_gene"].values.astype(float)
    # Use unique percentile edges to avoid degenerate bins (e.g. all zeros)
    bin_edges = np.unique(
        np.quantile(gws_dists, np.linspace(0, 1, n_bins + 1))
    )
    # Widen first and last edges to include all values
    bin_edges[0]  -= 1
    bin_edges[-1] += 1

    def assign_bins(arr: np.ndarray) -> np.ndarray:
        return np.clip(np.digitize(arr, bin_edges) - 1, 0, len(bin_edges) - 2)

    gws_bin_ids   = assign_bins(gws_dists)
    elig_dist_arr = eligible["dist_to_nearest_gene"].values.astype(float)
    eligible      = eligible.copy()
    eligible["_bin"] = assign_bins(elig_dist_arr)

    gws_bin_counts = (
        pd.Series(gws_bin_ids)
        .value_counts()
        .sort_index()
        .to_dict()
    )

    # --- Stratified sampling --------------------------------------------
    n_unique_bins = len(bin_edges) - 1
    selected_parts: list[pd.DataFrame] = []
    remaining_eligible = eligible.copy()
    shortfall = 0

    for b in range(n_unique_bins):
        n_want = gws_bin_counts.get(b, 0)
        if n_want == 0:
            continue
        pool = remaining_eligible[remaining_eligible["_bin"] == b]
        n_take = min(n_want, len(pool))
        if n_take > 0:
            chosen = pool.sample(
                n=n_take, replace=False,
                random_state=int(rng.integers(2**31)),
            )
            selected_parts.append(chosen)
            remaining_eligible = remaining_eligible.drop(index=chosen.index)
        if n_take < n_want:
            shortfall += n_want - n_take

    # Fill any shortfall from what's left in the eligible pool
    if shortfall > 0 and not remaining_eligible.empty:
        n_fill = min(shortfall, len(remaining_eligible))
        extra = remaining_eligible.sample(
            n=n_fill, replace=False,
            random_state=int(rng.integers(2**31)),
        )
        selected_parts.append(extra)

    if not selected_parts:
        return pd.DataFrame(columns=candidates.columns)

    result = pd.concat(selected_parts).drop(columns=["_bin"])
    return result.head(n)


# ── B1 data loading ────────────────────────────────────────────────────────────

def load_b1_clean() -> pd.DataFrame:
    """Load B1 clean SNVs with hg38 positions and hg38-convention alleles."""
    absent_snps = set(pd.read_csv(ABSENT_CSV)["snp"])

    df = pd.read_csv(B1_GZ, low_memory=False)
    clean = df[
        (df["is_snv"] == "YES") &
        (df["a_ok"] == "YES") &
        (df["routes_agree"].isin(["YES", "NA"]) | df["routes_agree"].isna())
    ].copy()

    def chrom_str(c: object) -> str:
        c = str(c)
        return "chrX" if c == "X" else (f"chr{c}" if not c.startswith("chr") else c)

    clean["chrom_hg38"]   = clean["CHR"].apply(chrom_str)
    clean["a_pos"]        = clean["a_pos"].astype(float)

    # hg38-convention alleles (swap for ALT_as_hg38ref)
    def api_alleles(row: pd.Series) -> tuple[str, str]:
        if "ALT_as_hg38ref" in str(row.get("orientation", "")):
            return row["ALT"], row["REF"]
        return row["REF"], row["ALT"]

    alleles              = clean.apply(api_alleles, axis=1)
    clean["api_ref"]     = [a[0] for a in alleles]
    clean["api_alt"]     = [a[1] for a in alleles]

    # Exclude gnomAD-absent artefacts
    clean = clean[~clean["SNP"].isin(absent_snps)].copy()

    return clean


def load_gws_scores() -> pd.DataFrame:
    """
    Load existing GW-sig ATAC scores from B2_scored_variants.csv.

    For 3q29 (two tissues), keeps only UBERON:0006920 (esophagus) rows.
    """
    df = pd.read_csv(SCORED_CSV)
    df = df[df["error"].isna()].copy() if "error" in df.columns else df.copy()

    # 3q29: keep esophagus rows only; fall back to lung if none present
    q29_esoph = df[(df["locus"] == "3q29") & (df["ag_tissue"] == "UBERON:0006920")]
    q29_lung  = df[(df["locus"] == "3q29") & (df["ag_tissue"] == "UBERON:0002048")]

    if len(q29_esoph) == 0 and len(q29_lung) > 0:
        print("WARNING: 3q29 esophagus rows absent; using lung ATAC instead",
              file=sys.stderr)
        q29_use = q29_lung
    else:
        q29_use = q29_esoph

    other_loci = df[df["locus"] != "3q29"]
    scored = pd.concat([q29_use, other_loci], ignore_index=True)

    return scored[["snp", "locus", "chrom", "pos_hg38",
                   "api_ref", "api_alt", "orientation_b1",
                   "ag_tissue", "ag_atac_l2d_raw"]].copy()


# ── API scoring ────────────────────────────────────────────────────────────────

def score_variant(model, chrom: str, pos: int,
                  ref: str, alt: str, tissue: str) -> float:
    """Score one variant; returns raw ATAC L2_DIFF for tissue, or NaN."""
    variant  = genome.Variant(chromosome=chrom, position=pos,
                              reference_bases=ref, alternate_bases=alt)
    interval = genome.Interval(chromosome=chrom,
                               start=pos - HALF, end=pos + HALF)
    raw  = model.score_variants(
        intervals=[interval], variants=[variant],
        variant_scorers=[ATAC_SCORER], progress_bar=False,
    )
    tidy = tidy_scores(raw)
    rows = tidy[
        (tidy["ontology_curie"] == tissue) &
        (tidy["output_type"] == "ATAC")
    ]
    if rows.empty or rows["raw_score"].isna().all():
        return float("nan")
    return float(rows["raw_score"].abs().max())


def score_controls(
    model,
    ctrl_variants: list[dict],
    run_utc: str,
) -> list[dict]:
    """Score all control variants with checkpointing. Returns list of result dicts."""
    completed: dict[str, float] = {}
    ckpt_rows: list[dict] = []
    if os.path.exists(CKPT_CSV):
        ckpt = pd.read_csv(CKPT_CSV)
        completed = dict(zip(ckpt["ctrl_key"], ckpt["atac_l2d_raw"]))
        ckpt_rows = ckpt.to_dict("records")
        print(f"  Checkpoint: {len(completed)} controls already scored")

    remaining = [v for v in ctrl_variants if v["ctrl_key"] not in completed]
    total = len(remaining)
    new_count = 0

    for i, v in enumerate(remaining, 1):
        if i == 1 or i % 50 == 0:
            print(f"  [{i}/{total}] {v['chrom_hg38']}:{v['a_pos']} "
                  f"{v['api_ref']}>{v['api_alt']}  ({v['locus']})", flush=True)
        backoff = 15
        for attempt in range(6):
            try:
                score = score_variant(
                    model, v["chrom_hg38"], int(v["a_pos"]),
                    v["api_ref"], v["api_alt"], v["tissue"],
                )
                row = {**v, "atac_l2d_raw": score,
                       "run_date_utc": run_utc, "ag_version": AG_VERSION}
                ckpt_rows.append(row)
                new_count += 1
                if new_count % 30 == 0:
                    pd.DataFrame(ckpt_rows).to_csv(CKPT_CSV, index=False)
                break
            except grpc.RpcError as e:
                code = e.code()
                if code in (grpc.StatusCode.RESOURCE_EXHAUSTED,
                            grpc.StatusCode.UNAVAILABLE):
                    print(f"    rate-limit ({attempt+1}/6) — sleep {backoff}s",
                          flush=True)
                else:
                    print(f"    gRPC {code} — sleep {backoff}s", flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 2, 300)
            except Exception as exc:
                print(f"    ERROR: {exc}", flush=True)
                ckpt_rows.append({**v, "atac_l2d_raw": float("nan"),
                                  "run_date_utc": run_utc, "ag_version": AG_VERSION})
                break

    pd.DataFrame(ckpt_rows).to_csv(CKPT_CSV, index=False)
    return ckpt_rows


# ── Statistics ────────────────────────────────────────────────────────────────

def rank_biserial(u_stat: float, n1: int, n2: int) -> float:
    """
    Rank-biserial correlation from Mann-Whitney U (first-group statistic).
    Positive value → first group (GW-sig) tends to exceed second (control).
    """
    return (2 * u_stat / (n1 * n2)) - 1


def compute_locus_stats(
    gws_scores: np.ndarray,
    ctrl_scores: np.ndarray,
    locus: str,
) -> dict:
    gws_clean  = gws_scores[~np.isnan(gws_scores)]
    ctrl_clean = ctrl_scores[~np.isnan(ctrl_scores)]

    u_stat, p_val = stats.mannwhitneyu(gws_clean, ctrl_clean,
                                       alternative="two-sided")
    rb = rank_biserial(u_stat, len(gws_clean), len(ctrl_clean))

    return {
        "locus":               locus,
        "n_gws":               len(gws_clean),
        "gws_median":          float(np.median(gws_clean)),
        "gws_mean":            float(np.mean(gws_clean)),
        "gws_max":             float(np.max(gws_clean)),
        "n_ctrl":              len(ctrl_clean),
        "ctrl_median":         float(np.median(ctrl_clean)),
        "ctrl_mean":           float(np.mean(ctrl_clean)),
        "ctrl_max":            float(np.max(ctrl_clean)),
        "mannwhitney_U":       float(u_stat),
        "p_two_sided":         float(p_val),
        "rank_biserial":       float(rb),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true",
                    help="Show candidate counts and exit without scoring")
    args = ap.parse_args()

    RUN_UTC = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    rng = np.random.default_rng(seed=RNG_SEED)

    print("Loading B1 clean SNVs...")
    b1 = load_b1_clean()

    print("Loading GW-sig ATAC scores...")
    gws_all = load_gws_scores()

    # Fetch gene boundaries from Ensembl REST (GRCh38)
    all_genes = sorted({g for cfg in LOCUS_CONFIG.values() for g in cfg["genes"]})
    print(f"Querying Ensembl REST for {len(all_genes)} genes: {all_genes}")
    gene_bounds_raw = fetch_gene_boundaries(all_genes)
    print("Gene boundaries (GRCh38):")
    for g, (chrom, start, end) in gene_bounds_raw.items():
        print(f"  {g}: {chrom}:{start:,}–{end:,}")

    # Per-locus gene bounds as list of tuples for dist_to_nearest_gene()
    locus_gene_bounds: dict[str, list[tuple[str, int, int]]] = {
        locus: [gene_bounds_raw[g] for g in cfg["genes"]]
        for locus, cfg in LOCUS_CONFIG.items()
    }

    # Compute distance to nearest gene for all B1 clean SNVs
    print("\nComputing distance-to-nearest-gene for B1 variants...")
    for locus, bounds in locus_gene_bounds.items():
        mask = b1["locus"] == locus
        b1.loc[mask, "dist_to_nearest_gene"] = b1.loc[mask].apply(
            lambda r: dist_to_nearest_gene(int(r["a_pos"]), r["chrom_hg38"], bounds),
            axis=1,
        )

    # Compute distance for GW-sig variants too
    for locus, bounds in locus_gene_bounds.items():
        mask = gws_all["locus"] == locus
        gws_all.loc[mask, "dist_to_nearest_gene"] = gws_all.loc[mask].apply(
            lambda r: dist_to_nearest_gene(int(r["pos_hg38"]), r["chrom"], bounds),
            axis=1,
        )

    # --- Select controls per locus --------------------------------------
    all_ctrl_variants: list[dict] = []
    selection_log: list[dict] = []

    for locus, cfg in LOCUS_CONFIG.items():
        tissue = cfg["tissue"]
        gws_locus  = gws_all[gws_all["locus"] == locus].copy()
        b1_locus   = b1[b1["locus"] == locus].copy()
        gws_snps   = set(gws_locus["snp"])
        candidates = b1_locus[~b1_locus["SNP"].isin(gws_snps)].copy()

        n_gws = len(gws_locus)
        n_cand_before = len(candidates)

        selected = sample_matched_controls(
            candidates   = candidates,
            gws_variants = gws_locus.rename(columns={"pos_hg38": "a_pos"}),
            n            = n_gws,
            rng          = rng,
        )

        n_selected = len(selected)
        shortfall  = n_gws - n_selected

        selection_log.append({
            "locus":        locus,
            "n_gws":        n_gws,
            "candidates":   n_cand_before,
            "selected":     n_selected,
            "shortfall":    shortfall,
        })

        for _, row in selected.iterrows():
            all_ctrl_variants.append({
                "ctrl_key":  f"ctrl_{locus}_{row['SNP']}",
                "locus":     locus,
                "SNP":       row["SNP"],
                "chrom_hg38": row["chrom_hg38"],
                "a_pos":     row["a_pos"],
                "api_ref":   row["api_ref"],
                "api_alt":   row["api_alt"],
                "orientation_b1": row.get("orientation", ""),
                "tissue":    tissue,
                "dist_to_nearest_gene": row["dist_to_nearest_gene"],
            })

    print("\nControl selection summary:")
    for sl in selection_log:
        flag = f"  *** SHORTFALL {sl['shortfall']}" if sl["shortfall"] > 0 else ""
        print(f"  {sl['locus']}: {sl['n_gws']} GW-sig, "
              f"{sl['candidates']} candidates, "
              f"{sl['selected']} selected{flag}")

    if args.dry_run:
        print(f"\nTotal controls to score: {len(all_ctrl_variants)}")
        print("Dry run — exiting.")
        return

    # --- Score controls -------------------------------------------------
    print(f"\nConnecting to AlphaGenome API...")
    model = dna_client.create(API_KEY)
    print(f"Connected. Scoring {len(all_ctrl_variants)} control variants.\n")

    ctrl_results = score_controls(model, all_ctrl_variants, RUN_UTC)
    ctrl_df = pd.DataFrame(ctrl_results)
    ctrl_df.to_csv(CTRL_OUT_CSV, index=False)
    print(f"\nControl scores written to {CTRL_OUT_CSV}")

    if len(ctrl_df) == len(all_ctrl_variants) and os.path.exists(CKPT_CSV):
        os.remove(CKPT_CSV)
        print("Checkpoint removed.")

    # --- Per-locus statistics -------------------------------------------
    print("\n=== Per-locus statistics ===\n")
    summary_rows: list[dict] = []

    for locus, cfg in LOCUS_CONFIG.items():
        gws_locus  = gws_all[gws_all["locus"] == locus]
        ctrl_locus = ctrl_df[ctrl_df["locus"] == locus]

        gws_scores  = gws_locus["ag_atac_l2d_raw"].dropna().values
        ctrl_scores = ctrl_locus["atac_l2d_raw"].dropna().values

        if len(gws_scores) < 2 or len(ctrl_scores) < 2:
            print(f"  {locus}: insufficient data (gws={len(gws_scores)}, "
                  f"ctrl={len(ctrl_scores)}) — skipping test")
            continue

        row = compute_locus_stats(gws_scores, ctrl_scores, locus)
        summary_rows.append(row)

        direction = "GW-sig > ctrl" if row["rank_biserial"] > 0 else "ctrl > GW-sig"
        print(
            f"  {locus} ({cfg['tissue']}):\n"
            f"    GW-sig  n={row['n_gws']}  "
            f"median={row['gws_median']:.4f}  mean={row['gws_mean']:.4f}  "
            f"max={row['gws_max']:.4f}\n"
            f"    control n={row['n_ctrl']}  "
            f"median={row['ctrl_median']:.4f}  mean={row['ctrl_mean']:.4f}  "
            f"max={row['ctrl_max']:.4f}\n"
            f"    Mann-Whitney U={row['mannwhitney_U']:.0f}  "
            f"p={row['p_two_sided']:.4g}  "
            f"rank-biserial={row['rank_biserial']:+.3f}  ({direction})\n"
        )

    summ_df = pd.DataFrame(summary_rows)
    summ_df["run_date_utc"] = RUN_UTC
    summ_df["ag_version"]   = AG_VERSION
    summ_df.to_csv(SUMM_OUT_CSV, index=False)
    print(f"Summary written to {SUMM_OUT_CSV}")


if __name__ == "__main__":
    main()
