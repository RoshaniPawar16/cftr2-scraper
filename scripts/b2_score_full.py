"""
B2 full scoring: 548 GW-significant GWAS modifier SNVs across five loci.

Scorer: CenterMaskScorer(SPLICE_SITE_USAGE, 501, L2_DIFF)
        CenterMaskScorer(ATAC, 501, L2_DIFF)          — non-esophagus tissues
        CenterMaskScorer(CHIP_HISTONE, 2001, L2_DIFF) — all tissues; primary for esophagus

Tissues per locus:
  3q29   → UBERON:0006920 (esophagus mucosa) + UBERON:0002048 (lung)
  5p15   → UBERON:0002048 (lung)
  6p21   → CL:0000236 (B lymphocyte)
  11p13  → UBERON:0002048 (lung)
  Xq23   → UBERON:0002048 (lung)

Output: results/gwas_modifiers/B2_scored_variants.csv
        One row per (variant × tissue). 3q29 produces two rows per variant.

Splice gate: join from B2_splice_distances.csv.
ALT_as_hg38ref: alleles are swapped to hg38 convention before API call.
Checkpoint: resumes from last completed (snp, tissue) pair if interrupted.

Usage:
    .venv/bin/python scripts/b2_score_full.py
    .venv/bin/python scripts/b2_score_full.py --dry-run  # print variant list, exit
"""

import argparse, os, sys, time, datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from alphagenome.data import genome
from alphagenome.models import dna_client
from alphagenome.models.variant_scorers import (
    CenterMaskScorer, AggregationType, tidy_scores,
)
from alphagenome.models.dna_output import OutputType
import grpc
import alphagenome as _ag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AG_VERSION = getattr(_ag, "__version__", "unknown")
load_dotenv(os.path.join(ROOT, ".env"))
API_KEY = os.environ.get("ALPHAGENOME_API_KEY", "")
if not API_KEY:
    sys.exit("ERROR: Set ALPHAGENOME_API_KEY in .env")

OUT_DIR    = os.path.join(ROOT, "results/gwas_modifiers")
OUT_CSV    = os.path.join(OUT_DIR, "B2_scored_variants.csv")
CKPT_CSV   = os.path.join(OUT_DIR, ".B2_scored_variants_ckpt.csv")
B1_GZ      = os.path.join(OUT_DIR, "B1_lifted_hg38.csv.gz")
RESCUED_CSV= os.path.join(OUT_DIR, "B1_rescued_routeB_only.csv")
ABSENT_CSV = os.path.join(OUT_DIR, "B1_gnomad_absent_nonsex_loci.csv")
SPLICE_CSV = os.path.join(OUT_DIR, "B2_splice_distances.csv")

HALF = dna_client.SEQUENCE_LENGTH_1MB // 2
AG_CALIBRATION = "genomewide_post_2026-06-18"

SCORERS = [
    CenterMaskScorer(OutputType.SPLICE_SITE_USAGE, 501,  AggregationType.L2_DIFF),
    CenterMaskScorer(OutputType.ATAC,              501,  AggregationType.L2_DIFF),
    CenterMaskScorer(OutputType.CHIP_HISTONE,      2001, AggregationType.L2_DIFF),
]

LOCUS_TISSUES = {
    "3q29":  ["UBERON:0006920", "UBERON:0002048"],
    "5p15":  ["UBERON:0002048"],
    "6p21":  ["CL:0000236"],
    "11p13": ["UBERON:0002048"],
    "Xq23":  ["UBERON:0002048"],
}


def load_scoring_set():
    """Return DataFrame of 548 variants with api_ref/api_alt already normalised to hg38."""
    ab = pd.read_csv(ABSENT_CSV)
    artefact_snps = set(ab["snp"])

    df = pd.read_csv(B1_GZ, low_memory=False, keep_default_na=False)
    clean = df[
        (df["is_snv"] == "YES") &
        (df["a_ok"] == "YES") &
        (df["routes_agree"].isin(["YES", "NA"]) | df["routes_agree"].isna())
    ].copy()
    gws = clean[clean["p.fix"] < 5e-8].copy()
    gws = gws[~gws["SNP"].isin(artefact_snps)].copy()

    rescued = pd.read_csv(RESCUED_CSV)
    resc_gws = rescued[rescued["p.fix"] < 5e-8].copy()

    all_gws = pd.concat([gws, resc_gws], ignore_index=True)

    # Compute hg38-convention alleles (swap for ALT_as_hg38ref)
    def api_alleles(row):
        if "ALT_as_hg38ref" in str(row.get("orientation", "")):
            return row["ALT"], row["REF"]
        return row["REF"], row["ALT"]

    all_gws[["api_ref", "api_alt"]] = all_gws.apply(
        lambda r: pd.Series(api_alleles(r)), axis=1
    )

    # Chromosome string with 'chr' prefix
    def chrom_str(c):
        c = str(c)
        return "chrX" if c == "X" else (f"chr{c}" if not c.startswith("chr") else c)

    all_gws["chrom_hg38"] = all_gws["CHR"].apply(chrom_str)
    all_gws["pos_hg38_int"] = all_gws["a_pos"].astype(int)

    return all_gws.reset_index(drop=True)


def load_splice_flags():
    spl = pd.read_csv(SPLICE_CSV)
    spl["splice_near_transcript"] = spl["splice_near_transcript"].map(
        {True: True, False: False, "True": True, "False": False}
    )
    return spl.set_index("SNP")[["dist_to_nearest_splice", "splice_near_transcript"]]


def extract_scores(tidy_df, ontology):
    """Extract L2_DIFF raw and quantile scores for one tissue from tidy output."""
    rows = tidy_df[tidy_df["ontology_curie"] == ontology]

    def _get(output_type):
        subset = rows[rows["output_type"] == output_type]
        if subset.empty or subset["raw_score"].isna().all():
            return np.nan, np.nan, 0
        raw_val = float(subset["raw_score"].abs().max())
        q_col   = "quantile_score"
        q_val   = float(subset[q_col].abs().max()) if q_col in subset and subset[q_col].notna().any() else np.nan
        n_tracks = int(subset["raw_score"].notna().sum())
        return raw_val, q_val, n_tracks

    spl_raw, spl_q, spl_n   = _get("SPLICE_SITE_USAGE")
    atac_raw, atac_q, atac_n = _get("ATAC")
    hist_raw, hist_q, hist_n  = _get("CHIP_HISTONE")

    return {
        "ag_splice_l2d_raw":    spl_raw,
        "ag_splice_l2d_q":      spl_q,
        "ag_splice_n_tracks":   spl_n,
        "ag_atac_l2d_raw":      atac_raw,
        "ag_atac_l2d_q":        atac_q,
        "ag_atac_n_tracks":     atac_n,
        "ag_histone_l2d_raw":   hist_raw,
        "ag_histone_l2d_q":     hist_q,
        "ag_histone_n_tracks":  hist_n,
    }


def score_one(model, chrom, pos, api_ref, api_alt):
    """Single API call. Returns (tidy_df, wall_sec)."""
    variant  = genome.Variant(chromosome=chrom, position=pos,
                              reference_bases=api_ref, alternate_bases=api_alt)
    interval = genome.Interval(chromosome=chrom, start=pos-HALF, end=pos+HALF)
    t0 = time.monotonic()
    raw = model.score_variants(
        intervals=[interval], variants=[variant],
        variant_scorers=SCORERS, progress_bar=False,
    )
    elapsed = time.monotonic() - t0
    return tidy_scores(raw), elapsed


def build_row(gws_row, tissue, tidy_df, wall_sec, splice_flags):
    snp = gws_row["SNP"]
    sf  = splice_flags.loc[snp] if snp in splice_flags.index else {}
    scores = extract_scores(tidy_df, tissue)
    row = {
        "snp":                  snp,
        "locus":                gws_row["locus"],
        "chrom":                gws_row["chrom_hg38"],
        "pos_hg38":             gws_row["pos_hg38_int"],
        "api_ref":              gws_row["api_ref"],
        "api_alt":              gws_row["api_alt"],
        "orientation_b1":       gws_row["orientation"],
        "maf_source":           gws_row["MAF"],
        "p_fix":                gws_row["p.fix"],
        "ag_tissue":            tissue,
        "ag_run_date":          datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ag_calibration":       AG_CALIBRATION,
        "ag_version":           AG_VERSION,
        "ag_scorer_splice":     "CenterMaskScorer(SPLICE_SITE_USAGE,501,L2_DIFF)",
        "ag_scorer_chromatin":  ("CenterMaskScorer(CHIP_HISTONE,2001,L2_DIFF)"
                                 if tissue == "UBERON:0006920"
                                 else "CenterMaskScorer(ATAC,501,L2_DIFF)"),
        "wall_sec":             round(wall_sec, 2),
        "dist_to_nearest_splice": sf.get("dist_to_nearest_splice", np.nan)
                                  if hasattr(sf, "get") else sf,
        "splice_near_transcript": (splice_flags.loc[snp, "splice_near_transcript"]
                                   if snp in splice_flags.index else np.nan),
        "gnomad_absent_artefact": False,
        "imputation_quality_available": False,
    }
    row.update(scores)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Loading scoring set...", flush=True)
    all_gws    = load_scoring_set()
    splice_flags = load_splice_flags()
    print(f"  {len(all_gws)} GW-significant variants loaded", flush=True)

    # Expand to (variant × tissue) pairs
    pairs = []
    for _, row in all_gws.iterrows():
        for tissue in LOCUS_TISSUES.get(row["locus"], []):
            pairs.append((row, tissue))
    print(f"  {len(pairs)} (variant × tissue) pairs to score", flush=True)

    if args.dry_run:
        print("\nDry run — first 10 pairs:")
        for row, tissue in pairs[:10]:
            print(f"  {row['locus']:8s} {row['SNP']:15s} {row['chrom_hg38']}:{row['pos_hg38_int']} "
                  f"{row['api_ref']}>{row['api_alt']} ori={row['orientation']} tissue={tissue}")
        print(f"  ... ({len(pairs)} total)")
        return

    # Load checkpoint
    completed = set()
    ckpt_rows = []
    if os.path.exists(CKPT_CSV):
        ckpt = pd.read_csv(CKPT_CSV)
        completed = set(zip(ckpt["snp"], ckpt["ag_tissue"]))
        ckpt_rows = ckpt.to_dict("records")
        print(f"  Resuming — {len(completed)} pairs already completed", flush=True)

    remaining = [(r, t) for r, t in pairs if (r["SNP"], t) not in completed]
    print(f"  {len(remaining)} pairs remaining\n", flush=True)

    if not remaining:
        print("All pairs already scored. Building final output.")
    else:
        print("Connecting to AlphaGenome API...", flush=True)
        model = dna_client.create(API_KEY)
        print("Connected.\n", flush=True)

    new_rows = []
    for i, (gws_row, tissue) in enumerate(remaining, 1):
        snp  = gws_row["SNP"]
        chrom = gws_row["chrom_hg38"]
        pos   = gws_row["pos_hg38_int"]
        ref   = gws_row["api_ref"]
        alt   = gws_row["api_alt"]

        if i % 50 == 0 or i == 1:
            print(f"  [{i}/{len(remaining)}] {gws_row['locus']} {snp} {chrom}:{pos} "
                  f"{ref}>{alt} tissue={tissue}", flush=True)

        backoff = 15
        for attempt in range(6):
            try:
                tidy_df, wall_sec = score_one(model, chrom, pos, ref, alt)
                row = build_row(gws_row, tissue, tidy_df, wall_sec, splice_flags)
                new_rows.append(row)
                ckpt_rows.append(row)
                # Checkpoint every 20 new rows
                if len(new_rows) % 20 == 0:
                    pd.DataFrame(ckpt_rows).to_csv(CKPT_CSV, index=False)
                break
            except grpc.RpcError as e:
                code = e.code()
                if code in (grpc.StatusCode.RESOURCE_EXHAUSTED, grpc.StatusCode.UNAVAILABLE):
                    print(f"         rate-limit (attempt {attempt+1}/6) — sleep {backoff}s", flush=True)
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 300)
                else:
                    print(f"         gRPC {code} — sleep {backoff}s", flush=True)
                    if attempt == 5:
                        new_rows.append({"snp": snp, "ag_tissue": tissue,
                                         "locus": gws_row["locus"], "error": str(e)})
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 120)
            except Exception as e:
                print(f"         ERROR: {e}", flush=True)
                new_rows.append({"snp": snp, "ag_tissue": tissue,
                                 "locus": gws_row["locus"], "error": str(e)})
                break

    # Final checkpoint flush
    if new_rows:
        pd.DataFrame(ckpt_rows).to_csv(CKPT_CSV, index=False)

    # Consolidate
    all_rows = ckpt_rows
    final_df = pd.DataFrame(all_rows)
    if "error" not in final_df.columns:
        final_df["error"] = np.nan

    errors = final_df["error"].notna().sum()
    scored = final_df["error"].isna().sum()
    print(f"\nConsolidated: {scored} scored, {errors} errors")

    final_df = final_df.drop_duplicates(subset=["snp", "ag_tissue"])
    final_df.to_csv(OUT_CSV, index=False)
    print(f"Written to {OUT_CSV}")

    # Remove checkpoint on clean completion
    if errors == 0 and os.path.exists(CKPT_CSV):
        os.remove(CKPT_CSV)
        print("Checkpoint removed.")

    # Summary
    print("\n=== Summary ===")
    clean_df = final_df[final_df["error"].isna()].copy()
    for col in ["ag_splice_l2d_raw", "ag_atac_l2d_raw", "ag_histone_l2d_raw"]:
        if col in clean_df.columns:
            vals = clean_df[col].dropna()
            if len(vals):
                print(f"{col}: n={len(vals)} mean={vals.mean():.4f} "
                      f"p95={vals.quantile(0.95):.4f} max={vals.max():.4f}")
    print("\nSplice gate summary:")
    for locus, grp in clean_df.groupby("locus"):
        near = int((grp["splice_near_transcript"] == True).sum())
        print(f"  {locus}: {near}/{len(grp)} variants near splice site (≤500bp)")


if __name__ == "__main__":
    main()
