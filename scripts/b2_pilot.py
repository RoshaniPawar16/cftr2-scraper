"""
B2 pilot: score 10 GW-significant GWAS modifier SNVs (2 per locus) with
CenterMaskScorer L2_DIFF for splice and ATAC, one at each proposed tissue.

Includes one ALT_as_hg38ref variant (rs12858227, Xq23) to confirm
failure-mode-3 guard: score must be non-trivially different from zero.

Usage:
    .venv/bin/python scripts/b2_pilot.py
    .venv/bin/python scripts/b2_pilot.py --run2   # determinism check (10+ min later)

Outputs:
    results/gwas_modifiers/B2_pilot_run1.csv
    results/gwas_modifiers/B2_pilot_run2.csv  (--run2)
    results/gwas_modifiers/B2_pilot_determinism.csv  (written by --run2)
"""

import argparse
import os
import sys
import time
import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from alphagenome.data import genome
from alphagenome.models import dna_client
from alphagenome.models.variant_scorers import CenterMaskScorer, AggregationType
from alphagenome.models.dna_output import OutputType
import grpc
import alphagenome as _ag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AG_VERSION = getattr(_ag, "__version__", "unknown")
load_dotenv(os.path.join(ROOT, ".env"))
API_KEY = os.environ.get("ALPHAGENOME_API_KEY", "")
if not API_KEY:
    sys.exit("ERROR: Set ALPHAGENOME_API_KEY in .env")

OUT_DIR = os.path.join(ROOT, "results/gwas_modifiers")
os.makedirs(OUT_DIR, exist_ok=True)

HALF = dna_client.SEQUENCE_LENGTH_1MB // 2

SPLICE_SCORER = CenterMaskScorer(
    requested_output=OutputType.SPLICE_SITE_USAGE,
    width=501,
    aggregation_type=AggregationType.L2_DIFF,
)
ATAC_SCORER = CenterMaskScorer(
    requested_output=OutputType.ATAC,
    width=501,
    aggregation_type=AggregationType.L2_DIFF,
)
SCORERS = [SPLICE_SCORER, ATAC_SCORER]

# 10 pilot variants: 2 per locus
# orientation_b1 recorded for documentation; api_ref/api_alt are hg38-normalised
# (ALT_as_hg38ref variants have source REF and ALT swapped here)
PILOT = [
    # locus, snp, chrom, pos_hg38, api_ref, api_alt, orientation_b1, tissue
    ("3q29",  "rs863582",   "chr3", 195751823, "G", "A", "REF_ok",          "UBERON:0006920"),
    ("3q29",  "rs2641716",  "chr3", 195760320, "A", "G", "REF_ok",          "UBERON:0002048"),
    ("5p15",  "rs7723049",  "chr5",    524657, "A", "G", "REF_ok",          "UBERON:0002048"),
    ("5p15",  "rs12515615", "chr5",    520148, "G", "A", "REF_ok",          "UBERON:0002048"),
    ("6p21",  "rs9391874",  "chr6",  32468903, "A", "G", "REF_ok",          "CL:0000236"),
    ("6p21",  "rs28789995", "chr6",  32468956, "A", "C", "REF_ok",          "CL:0000236"),
    ("11p13", "rs10742326", "chr11", 34788463, "G", "A", "REF_ok",          "UBERON:0002048"),
    ("11p13", "rs11032851", "chr11", 34764433, "C", "T", "REF_ok",          "UBERON:0002048"),
    # ALT_as_hg38ref: source REF=T source ALT=C hg38_ref=C → api_ref=C api_alt=T
    ("Xq23",  "rs12858227", "chrX", 116195873, "C", "T", "ALT_as_hg38ref", "UBERON:0002048"),
    ("Xq23",  "rs5950589",  "chrX", 116184631, "T", "C", "REF_ok",          "UBERON:0002048"),
]


def score_one(model, locus, snp, chrom, pos, api_ref, api_alt, orientation, tissue):
    """Score a single variant at a single tissue. Returns a dict."""
    variant = genome.Variant(
        chromosome=chrom,
        position=pos,
        reference_bases=api_ref,
        alternate_bases=api_alt,
    )
    interval = genome.Interval(
        chromosome=chrom,
        start=pos - HALF,
        end=pos + HALF,
    )
    t0 = time.monotonic()
    raw = model.score_variants(
        intervals=[interval],
        variants=[variant],
        variant_scorers=SCORERS,
        progress_bar=False,
    )
    elapsed = time.monotonic() - t0

    from alphagenome.models.variant_scorers import tidy_scores
    tidy = tidy_scores(raw)
    tissue_rows = tidy[tidy["ontology_curie"] == tissue]

    def extract(output_type_str):
        rows = tissue_rows[tissue_rows["output_type"] == output_type_str]
        if rows.empty or rows["raw_score"].isna().all():
            return np.nan, np.nan
        raw_val = float(rows["raw_score"].abs().max())
        q_val = float(rows["quantile_score"].abs().max()) if "quantile_score" in rows.columns and rows["quantile_score"].notna().any() else np.nan
        return raw_val, q_val

    splice_raw, splice_q = extract("SPLICE_SITE_USAGE")
    atac_raw, atac_q     = extract("ATAC")

    return {
        "run_timestamp":   datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "locus":           locus,
        "snp":             snp,
        "chrom":           chrom,
        "pos_hg38":        pos,
        "api_ref":         api_ref,
        "api_alt":         api_alt,
        "orientation_b1":  orientation,
        "tissue":          tissue,
        "scorer_splice":   "CenterMaskScorer(SPLICE_SITE_USAGE,width=501,L2_DIFF)",
        "scorer_atac":     "CenterMaskScorer(ATAC,width=501,L2_DIFF)",
        "ag_calibration":  "genomewide_post_2026-06-18",
        "ag_version":      AG_VERSION,
        "splice_l2d_raw":  splice_raw,
        "splice_l2d_q":    splice_q,
        "atac_l2d_raw":    atac_raw,
        "atac_l2d_q":      atac_q,
        "wall_sec":        round(elapsed, 2),
        "n_tissue_rows":   len(tissue_rows),
    }


def run_pilot(model, label):
    rows = []
    for i, (locus, snp, chrom, pos, ref, alt, ori, tissue) in enumerate(PILOT, 1):
        print(f"  [{i}/10] {locus} {snp} {chrom}:{pos} {ref}>{alt} orientation={ori} tissue={tissue}", flush=True)
        for attempt in range(4):
            try:
                row = score_one(model, locus, snp, chrom, pos, ref, alt, ori, tissue)
                rows.append(row)
                print(f"         splice_l2d_raw={row['splice_l2d_raw']:.6f}  "
                      f"atac_l2d_raw={row['atac_l2d_raw']:.6f}  "
                      f"wall={row['wall_sec']}s", flush=True)
                break
            except grpc.RpcError as e:
                wait = 30 * (attempt + 1)
                print(f"         gRPC error {e.code()} — retry in {wait}s", flush=True)
                time.sleep(wait)
            except Exception as e:
                print(f"         ERROR: {e}", flush=True)
                rows.append({"locus": locus, "snp": snp, "error": str(e)})
                break
    return pd.DataFrame(rows)


def determinism_check(run1_path, run2_path):
    r1 = pd.read_csv(run1_path)
    r2 = pd.read_csv(run2_path)
    merged = r1.merge(r2, on="snp", suffixes=("_r1", "_r2"))
    merged["splice_raw_diff"] = (merged["splice_l2d_raw_r1"] - merged["splice_l2d_raw_r2"]).abs()
    merged["atac_raw_diff"]   = (merged["atac_l2d_raw_r1"]   - merged["atac_l2d_raw_r2"]).abs()
    # NaN in both runs = not available for this tissue; treat as agreement
    both_nan_splice = merged["splice_l2d_raw_r1"].isna() & merged["splice_l2d_raw_r2"].isna()
    both_nan_atac   = merged["atac_l2d_raw_r1"].isna()   & merged["atac_l2d_raw_r2"].isna()
    merged["splice_agree"] = (merged["splice_raw_diff"] < 1e-7) | both_nan_splice
    merged["atac_agree"]   = (merged["atac_raw_diff"]   < 1e-7) | both_nan_atac
    out_path = os.path.join(OUT_DIR, "B2_pilot_determinism.csv")
    merged[["snp", "locus_r1", "splice_l2d_raw_r1", "splice_l2d_raw_r2",
            "splice_raw_diff", "splice_agree",
            "atac_l2d_raw_r1", "atac_l2d_raw_r2",
            "atac_raw_diff", "atac_agree"]].to_csv(out_path, index=False)
    max_splice = merged["splice_raw_diff"].max()
    max_atac   = merged["atac_raw_diff"].max()
    passed     = merged["splice_agree"].all() and merged["atac_agree"].all()
    print(f"\nDeterminism check:")
    print(f"  Max |splice raw diff|: {max_splice:.2e}")
    print(f"  Max |atac raw diff|:   {max_atac:.2e}")
    print(f"  PASS: {passed}")
    if not passed:
        print("  STOP — raw scores disagree. Do not proceed with full run.")
        sys.exit(1)
    print(f"  Written to {out_path}")
    return passed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run2", action="store_true",
                    help="Score same 10 variants again for determinism check")
    args = ap.parse_args()

    print(f"Connecting to AlphaGenome API...", flush=True)
    model = dna_client.create(API_KEY)
    print("Connected.\n", flush=True)

    if args.run2:
        run2_path = os.path.join(OUT_DIR, "B2_pilot_run2.csv")
        print("=== B2 pilot run 2 (determinism check) ===\n", flush=True)
        df = run_pilot(model, "run2")
        df.to_csv(run2_path, index=False)
        print(f"\nRun 2 written to {run2_path}")
        run1_path = os.path.join(OUT_DIR, "B2_pilot_run1.csv")
        if os.path.exists(run1_path):
            determinism_check(run1_path, run2_path)
        else:
            print(f"WARNING: {run1_path} not found — cannot check determinism")
    else:
        run1_path = os.path.join(OUT_DIR, "B2_pilot_run1.csv")
        print("=== B2 pilot run 1 ===\n", flush=True)
        df = run_pilot(model, "run1")
        df.to_csv(run1_path, index=False)
        print(f"\nRun 1 written to {run1_path}")
        print("\nSummary:")
        print(df[["locus", "snp", "orientation_b1", "tissue",
                   "splice_l2d_raw", "atac_l2d_raw", "wall_sec"]].to_string(index=False))
        print(f"\nMean wall time: {df['wall_sec'].mean():.1f}s  "
              f"Max: {df['wall_sec'].max():.1f}s")
        alt_ref_row = df[df["orientation_b1"] == "ALT_as_hg38ref"]
        if not alt_ref_row.empty:
            sr = float(alt_ref_row["splice_l2d_raw"].iloc[0])
            ar = float(alt_ref_row["atac_l2d_raw"].iloc[0])
            print(f"\nFailure-mode-3 check (rs12858227, ALT_as_hg38ref):")
            print(f"  splice_l2d_raw = {sr:.6f}  atac_l2d_raw = {ar:.6f}")
            if sr > 1e-4 or ar > 1e-4:
                print("  PASS — scores non-trivially different from zero")
            else:
                print("  FAIL — scores near zero. Allele swap may not have been applied.")
        print(f"\nTo run determinism check (wait ≥10 min):")
        print(f"  .venv/bin/python scripts/b2_pilot.py --run2")


if __name__ == "__main__":
    main()
