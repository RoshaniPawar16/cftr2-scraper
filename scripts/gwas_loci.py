"""
CF GWAS modifier locus coordinate registry (hg38).

Defines the five lung-disease severity modifier loci from:
  Corvol et al. Nat Commun 6:8382 (2015). DOI: 10.1038/ncomms9382.
  PMID: 26417704. PMC4589222.

Each locus is centred on the lead-SNP hg38 position from the B1 liftover:
  results/gwas_modifiers/B1_corvol_liftover.csv (row citations below).
  Liftover source: scripts/b1_corvol_liftover.py (UCSC hg19ToHg38 chain,
  cross-checked via Ensembl REST API).

Window: ±1 Mb around each lead SNP, matching the window used to extract
the input GWAS summary statistics (gwasImpute2_hg19_SAKNORM_all_meta_fixed_
chrPeaks1mb.txt; see data/gwas/GWAS_results/ and audit/gwas_provenance.md).

IMPORTANT — scope note
  All 1,278 variants in the existing AlphaGenome pipeline
  (results/alphagenome/l2diff_scores.csv, quantiles_genomewide_2026-08.csv)
  are on chromosome 7 (the CFTR locus). The five modifier loci defined here
  are on chr3, chr5, chr6, chr11, and chrX. This is a new, non-overlapping
  variant set, not a re-analysis of the CFTR cohort.

Tissue default: UBERON:0002048 (lung), per project constraint. Exception:
  6p21 uses CL:0000236 (B lymphocytes) because HLA class II genes are not
  expressed in airway epithelium; see docs/option_b_draft.md, Tissue section.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Locus:
    """One CF GWAS modifier locus."""

    name: str
    """Short identifier used in output filenames."""

    chrom: str
    """UCSC chromosome name, hg38 (e.g. 'chr3')."""

    lead_rsid: str
    """Lead SNP rsID from Corvol et al. Table 2."""

    lead_pos_hg38: int
    """1-based lead-SNP position in hg38 (from B1_corvol_liftover.csv)."""

    window_start_hg38: int
    """1-based window start = max(1, lead_pos_hg38 - 1_000_000)."""

    window_end_hg38: int
    """1-based window end = lead_pos_hg38 + 1_000_000."""

    gene_label: str
    """Gene(s) at the locus per Corvol Table 1."""

    cytogenetic_band: str
    """Cytogenetic band per Corvol Table 1."""

    ag_tissue: str
    """AlphaGenome tissue ontology ID for this locus."""

    source_csv_row: int
    """Row in results/gwas_modifiers/B1_corvol_liftover.csv (1-indexed, header = row 1)."""

    notes: str = ""


# ---------------------------------------------------------------------------
# Five CF modifier loci
# Lead-SNP hg38 positions: B1_corvol_liftover.csv rows 2–6.
# ---------------------------------------------------------------------------

LOCI: list[Locus] = [
    Locus(
        name="3q29",
        chrom="chr3",
        lead_rsid="rs3103933",
        lead_pos_hg38=195_758_569,  # B1_corvol_liftover.csv row 2; hg19: chr3:195,485,440
        window_start_hg38=194_758_569,
        window_end_hg38=196_758_569,
        gene_label="MUC4/MUC20",
        cytogenetic_band="3q29",
        ag_tissue="UBERON:0002048",  # lung
        source_csv_row=2,
        notes=(
            "47 variants in the MUC4 VNTR region (chr3:195,181,736–195,264,241 hg19) "
            "failed Route A liftover due to chain gaps; see B1_REPORT.md Step 3."
        ),
    ),
    Locus(
        name="5p15",
        chrom="chr5",
        lead_rsid="rs57221529",
        lead_pos_hg38=586_509,  # B1_corvol_liftover.csv row 3; hg19: chr5:586,624
        window_start_hg38=1,  # capped: 586,509 - 1,000,000 < 0
        window_end_hg38=1_586_509,
        gene_label="SLC9A3",
        cytogenetic_band="5p15",
        ag_tissue="UBERON:0002048",  # lung
        source_csv_row=3,
        notes=(
            "13 SNVs near chr5 telomere (chr5:18,146–44,430 hg19) failed Route A liftover. "
            "8 GWS variants absent from gnomAD v3 and v4 were excluded as likely artefacts; "
            "see results/gwas_modifiers/B1_gnomad_absent_nonsex_loci.csv."
        ),
    ),
    Locus(
        name="6p21",
        chrom="chr6",
        lead_rsid="rs116003090",
        lead_pos_hg38=32_467_073,  # B1_corvol_liftover.csv row 4; hg19: chr6:32,434,850
        window_start_hg38=31_467_073,
        window_end_hg38=33_467_073,
        gene_label="HLA-DRA",
        cytogenetic_band="6p21",
        # Deliberate departure from lung tissue: HLA class II genes are expressed
        # on professional antigen-presenting cells, not airway epithelium.
        # See docs/option_b_draft.md, Tissue assignment section.
        ag_tissue="CL:0000236",  # B lymphocytes
        source_csv_row=4,
        notes=(
            "rs116003090 is absent from the re-imputation summary statistics "
            "(gwasImpute2 dataset); no p-value for this lead SNP is available from "
            "these files. Corvol Table 2 values are from the original analysis only. "
            "2 GWS variants (rs28366348, rs28366349) excluded as gnomAD-absent artefacts."
        ),
    ),
    Locus(
        name="11p13",
        chrom="chr11",
        lead_rsid="rs10742326",
        lead_pos_hg38=34_788_463,  # B1_corvol_liftover.csv row 5; hg19: chr11:34,810,010
        window_start_hg38=33_788_463,
        window_end_hg38=35_788_463,
        gene_label="EHF/APIP",
        cytogenetic_band="11p12-13",
        ag_tissue="UBERON:0002048",  # lung
        source_csv_row=5,
        notes=(
            "12 DHS elements from Stolzenburg et al. (2017; Nucleic Acids Res 45:8773; "
            "GSE52179) were tiled in B2b; two luciferase-confirmed strong enhancers "
            "(chr11.2516, chr11.2521) fall within this locus."
        ),
    ),
    Locus(
        name="Xq23",
        chrom="chrX",
        lead_rsid="rs5952223",
        lead_pos_hg38=116_255_308,  # B1_corvol_liftover.csv row 6; hg19: chrX:115,386,565
        window_start_hg38=115_255_308,
        window_end_hg38=117_255_308,
        gene_label="AGTR2/SLC6A14",
        cytogenetic_band="Xq22-23",
        ag_tissue="UBERON:0002048",  # lung
        source_csv_row=6,
        notes=(
            "138 SNVs + 8 indels in AGTR2/SLC6A14 region (chrX:114,561,730–116,310,686 hg19) "
            "failed Route A liftover due to structural differences between hg19 and hg38 "
            "assemblies in this region. PAR status: this locus is outside PAR1/PAR2."
        ),
    ),
]

LOCI_BY_NAME: dict[str, Locus] = {locus.name: locus for locus in LOCI}


# ---------------------------------------------------------------------------
# B3 variant compilation — DRAFT (do not execute)
# ---------------------------------------------------------------------------
# TODO (pending supervisor decision on inclusion criteria):
#
# Step 1 — ClinVar retrieval
#   For each locus in LOCI, query ClinVar for variants within
#   [window_start_hg38, window_end_hg38] on locus.chrom.
#   API: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
#   (genome query by chr:start-stop, assembly GRCh38).
#
#   Candidate inclusion criteria (CHOOSE ONE — supervisor decision required):
#     Option 1: ClinVar VUS only (clinical_significance = "Uncertain significance")
#     Option 2: All ClinVar submissions (P/LP/VUS/LB/B)
#
# Step 2 — gnomAD retrieval
#   For each locus, query gnomAD v4.1 for rare variants within the window.
#   API: https://gnomad.broadinstitute.org/api (GraphQL)
#
#   Candidate inclusion criteria (CHOOSE ONE — supervisor decision required):
#     Option A: gnomAD rare SNVs only (AF < 0.01 in all populations)
#     Option B: gnomAD rare SNVs + indels (AF < 0.01)
#     Option C: gnomAD variants absent from ClinVar (novel candidates only)
#
# Step 3 — merge and deduplicate by chrom + pos_hg38 + ref + alt.
#
# Step 4 — filter to SNVs only (len(ref) == 1 and len(alt) == 1) for
#   compatibility with CenterMaskScorer. Record indels separately.
#
# Step 5 — write to results/gwas_modifiers/B3_variants_{locus_name}.csv
#   with columns: rsid, chrom, pos_hg38, ref, alt, source (clinvar|gnomad|both),
#   clinvar_sig, gnomad_af, locus.
#
# OUTPUT NOTE: This will produce a new variant set (chr3/chr5/chr6/chr11/chrX).
#   The 1,278 existing scored variants (results/alphagenome/l2diff_scores.csv,
#   results/alphagenome/quantiles_genomewide_2026-08.csv) are all chr7/CFTR and
#   must NOT be merged with B3 output. They are separate pipelines.


def main() -> None:
    """Print locus summary for quick inspection."""
    header = f"{'Name':<8} {'Chrom':<6} {'Lead SNP':<14} {'Lead pos hg38':>15} {'Window hg38':>30} {'Tissue'}"
    print(header)
    print("-" * len(header))
    for locus in LOCI:
        window = f"{locus.chrom}:{locus.window_start_hg38:,}–{locus.window_end_hg38:,}"
        print(
            f"{locus.name:<8} {locus.chrom:<6} {locus.lead_rsid:<14} "
            f"{locus.lead_pos_hg38:>15,} {window:>30} {locus.ag_tissue}"
        )


if __name__ == "__main__":
    main()
