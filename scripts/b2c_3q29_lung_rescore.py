"""
B2c addendum: rescore 24 3q29 controls in lung (UBERON:0002048) ATAC.

Original B2c used esophagus (UBERON:0006920) for 3q29, which has zero ATAC
tracks, making the comparison impossible. This script scores the same 24
control SNPs in lung and runs the Mann-Whitney against the 24 GW-sig lung
ATAC scores already in B2_scored_variants.csv.

Note: control sampling for 3q29 used flat (non-stratified) sampling because
all 24 GW-sig variants have identical distance-to-nearest-gene (0 bp — all
fall within MUC4/MUC20). Stratification was degenerate; flat sampling from
the eligible pool was used instead. This is recorded as
sampling_method='flat_degenerate' in the output.

Usage:
    .venv/bin/python scripts/b2c_3q29_lung_rescore.py
"""

import datetime
import os
import sys
import time

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from scipy import stats

import alphagenome as _ag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))
API_KEY = os.environ.get("ALPHAGENOME_API_KEY", "")
if not API_KEY:
    sys.exit("ERROR: Set ALPHAGENOME_API_KEY in .env")

AG_VERSION = getattr(_ag, "__version__", "unknown")

from alphagenome.data import genome
from alphagenome.models import dna_client
from alphagenome.models.variant_scorers import (
    CenterMaskScorer, AggregationType, tidy_scores,
)
from alphagenome.models.dna_output import OutputType
import grpc

OUT_DIR      = os.path.join(ROOT, "results/gwas_modifiers")
CTRL_CSV     = os.path.join(OUT_DIR, "B2c_control_scores.csv")
SCORED_CSV   = os.path.join(OUT_DIR, "B2_scored_variants.csv")
CKPT_CSV     = os.path.join(OUT_DIR, ".B2c_3q29_lung_ckpt.csv")
OUT_CSV      = os.path.join(OUT_DIR, "B2c_3q29_lung_scores.csv")

TISSUE = "UBERON:0002048"
HALF   = dna_client.SEQUENCE_LENGTH_1MB // 2

ATAC_SCORER = CenterMaskScorer(
    requested_output=OutputType.ATAC,
    width=501,
    aggregation_type=AggregationType.L2_DIFF,
)


def score_variant(model, chrom: str, pos: int, ref: str, alt: str) -> float:
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
        (tidy["ontology_curie"] == TISSUE) &
        (tidy["output_type"] == "ATAC")
    ]
    if rows.empty or rows["raw_score"].isna().all():
        return float("nan")
    return float(rows["raw_score"].abs().max())


def rank_biserial(u_stat: float, n1: int, n2: int) -> float:
    return (2 * u_stat / (n1 * n2)) - 1


def main() -> None:
    RUN_UTC = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    # Load 24 3q29 controls (identified by locus column)
    ctrl_df = pd.read_csv(CTRL_CSV, keep_default_na=False)
    ctrl_3q29 = ctrl_df[ctrl_df["locus"] == "3q29"].copy()
    print(f"Found {len(ctrl_3q29)} 3q29 control variants to score in lung.")

    # Checkpoint: resume if interrupted
    completed: dict[str, float] = {}
    ckpt_rows: list[dict] = []
    if os.path.exists(CKPT_CSV):
        ckpt = pd.read_csv(CKPT_CSV)
        completed = dict(zip(ckpt["ctrl_key"], ckpt["atac_l2d_raw_lung"]))
        ckpt_rows = ckpt.to_dict("records")
        print(f"  Checkpoint: {len(completed)} already scored")

    remaining = ctrl_3q29[~ctrl_3q29["ctrl_key"].isin(completed)].copy()
    total_remaining = len(remaining)
    print(f"Connecting to AlphaGenome API...")
    model = dna_client.create(API_KEY)
    print(f"Connected. Scoring {total_remaining} variants.\n")

    new_count = 0
    for i, (_, row) in enumerate(remaining.iterrows(), 1):
        print(f"  [{i}/{total_remaining}] {row['chrom_hg38']}:{int(row['a_pos'])} "
              f"{row['api_ref']}>{row['api_alt']}", flush=True)
        backoff = 15
        for attempt in range(6):
            try:
                score = score_variant(
                    model, row["chrom_hg38"], int(row["a_pos"]),
                    row["api_ref"], row["api_alt"],
                )
                result_row = {
                    "ctrl_key":         row["ctrl_key"],
                    "locus":            row["locus"],
                    "SNP":              row["SNP"],
                    "chrom_hg38":       row["chrom_hg38"],
                    "a_pos":            row["a_pos"],
                    "api_ref":          row["api_ref"],
                    "api_alt":          row["api_alt"],
                    "orientation_b1":   row["orientation_b1"],
                    "tissue_lung":      TISSUE,
                    "dist_to_nearest_gene": row["dist_to_nearest_gene"],
                    "atac_l2d_raw_lung": score,
                    "run_date_utc":     RUN_UTC,
                    "ag_version":       AG_VERSION,
                }
                ckpt_rows.append(result_row)
                new_count += 1
                if new_count % 5 == 0:
                    pd.DataFrame(ckpt_rows).to_csv(CKPT_CSV, index=False)
                break
            except grpc.RpcError as e:
                code = e.code()
                print(f"    gRPC {code} — sleep {backoff}s", flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 2, 300)
            except Exception as exc:
                print(f"    ERROR: {exc}", flush=True)
                ckpt_rows.append({
                    "ctrl_key": row["ctrl_key"], "locus": "3q29",
                    "SNP": row["SNP"], "chrom_hg38": row["chrom_hg38"],
                    "a_pos": row["a_pos"], "api_ref": row["api_ref"],
                    "api_alt": row["api_alt"],
                    "orientation_b1": row["orientation_b1"],
                    "tissue_lung": TISSUE,
                    "dist_to_nearest_gene": row["dist_to_nearest_gene"],
                    "atac_l2d_raw_lung": float("nan"),
                    "run_date_utc": RUN_UTC, "ag_version": AG_VERSION,
                })
                break

    pd.DataFrame(ckpt_rows).to_csv(CKPT_CSV, index=False)

    # Merge checkpoint with previously completed
    all_rows = ckpt_rows.copy()
    for k, v in completed.items():
        if not any(r["ctrl_key"] == k for r in all_rows):
            all_rows.append({"ctrl_key": k, "atac_l2d_raw_lung": v})

    result_df = pd.DataFrame(ckpt_rows)
    result_df.to_csv(OUT_CSV, index=False)
    print(f"\nLung control scores written to {OUT_CSV}")

    # Load GW-sig lung scores for 3q29
    scored = pd.read_csv(SCORED_CSV)
    gws_3q29 = scored[
        (scored["locus"] == "3q29") &
        (scored["ag_tissue"] == "UBERON:0002048")
    ].copy()
    gws_scores = gws_3q29["ag_atac_l2d_raw"].dropna().values
    ctrl_scores = result_df["atac_l2d_raw_lung"].dropna().values

    print(f"\n=== 3q29 lung ATAC: GW-sig vs control ===")
    print(f"  GW-sig  n={len(gws_scores)}  "
          f"median={np.median(gws_scores):.4f}  "
          f"mean={np.mean(gws_scores):.4f}  "
          f"max={np.max(gws_scores):.4f}")
    print(f"  control n={len(ctrl_scores)}  "
          f"median={np.median(ctrl_scores):.4f}  "
          f"mean={np.mean(ctrl_scores):.4f}  "
          f"max={np.max(ctrl_scores):.4f}")

    u_stat, p_val = stats.mannwhitneyu(gws_scores, ctrl_scores,
                                       alternative="two-sided")
    rb = rank_biserial(u_stat, len(gws_scores), len(ctrl_scores))
    direction = "GW-sig > ctrl" if rb > 0 else "ctrl > GW-sig"
    print(f"  Mann-Whitney U={u_stat:.0f}  p={p_val:.4g}  "
          f"rank-biserial={rb:+.4f}  ({direction})")
    print(f"  Sampling method: flat_degenerate (all GW-sig at dist=0)")

    if os.path.exists(CKPT_CSV) and len(result_df) >= len(ctrl_3q29):
        os.remove(CKPT_CSV)
        print("Checkpoint removed.")


if __name__ == "__main__":
    main()
