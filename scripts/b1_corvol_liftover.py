"""
Task B1: hg19 → hg38 liftover for the five CF GWAS modifier loci from Corvol et al. 2015.

Source: Corvol et al. "Genome-wide association meta-analysis identifies five modifier
loci of lung disease severity in cystic fibrosis." Nat Commun 6:8382, 2015.
DOI: 10.1038/ncomms9382, PMID: 26417704, PMC4589222.

Coordinates are taken from Table 2 of the paper (hg19, 1-based).
dbSNP verification: NCBI Variation API returns 0-based positions; +1 gives exact
match to all five paper coordinates, confirming the source table is reliable.

Output: results/gwas_modifiers/B1_corvol_liftover.csv
"""

import csv
import sys
from pathlib import Path

try:
    from pyliftover import LiftOver
except ImportError:
    sys.exit("pyliftover not found. Install with: pip install pyliftover")

LOCI = [
    # (rsid, locus_gene, chr_hg19, pos_hg19_1based)
    # Source: Corvol 2015 Table 2
    ("rs3103933",   "MUC4/MUC20",     "chr3",  195485440),
    ("rs57221529",  "SLC9A3",         "chr5",     586624),
    ("rs116003090", "HLA-DRA",        "chr6",   32434850),
    ("rs10742326",  "EHF/APIP",       "chr11",  34810010),
    ("rs5952223",   "AGTR2/SLC6A14",  "chrX",  115386565),
]

OUT = Path(__file__).parent.parent / "results" / "gwas_modifiers" / "B1_corvol_liftover.csv"
DOI = "10.1038/ncomms9382"


def run() -> None:
    print("Loading hg19→hg38 chain file...")
    lo = LiftOver("hg19", "hg38")
    print("Chain file ready.\n")

    rows = []
    for rsid, gene, chrom, pos_1based in LOCI:
        result = lo.convert_coordinate(chrom, pos_1based - 1)
        if result:
            chrom38, pos38_0based, strand, _score = result[0]
            rows.append({
                "rsid": rsid,
                "locus_gene": gene,
                "chr_hg19": chrom,
                "pos_hg19": pos_1based,
                "chr_hg38": chrom38,
                "pos_hg38": pos38_0based + 1,
                "strand": strand,
                "liftover_ok": "YES",
                "source_table": "Table2",
                "paper_doi": DOI,
            })
            print(f"  {rsid}  {gene:<16}  {chrom}:{pos_1based:>12,}  →  {chrom38}:{pos38_0based + 1:>12,}  {strand}")
        else:
            rows.append({
                "rsid": rsid,
                "locus_gene": gene,
                "chr_hg19": chrom,
                "pos_hg19": pos_1based,
                "chr_hg38": "NO_RESULT",
                "pos_hg38": "",
                "strand": ".",
                "liftover_ok": "FAIL",
                "source_table": "Table2",
                "paper_doi": DOI,
            })
            print(f"  {rsid}  {gene:<16}  LIFTOVER FAILED")

    fields = ["rsid", "locus_gene", "chr_hg19", "pos_hg19",
              "chr_hg38", "pos_hg38", "strand", "liftover_ok",
              "source_table", "paper_doi"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    ok = sum(1 for r in rows if r["liftover_ok"] == "YES")
    print(f"\n{ok}/{len(rows)} loci lifted successfully → {OUT}")


if __name__ == "__main__":
    run()
