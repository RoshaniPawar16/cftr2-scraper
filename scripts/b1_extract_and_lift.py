#!/usr/bin/env python3
"""
B1 steps 2-5: Extract peaks, liftover by two independent routes,
REF/ALT orientation check against hg38 reference, SNV filter.

Citations (both required):
  Corvol et al. Nat Commun 6:8382 (2015). DOI: 10.1038/ncomms9382
  Panjwani N et al. NPJ Genom Med 3:8 (2018). DOI: 10.1038/s41525-018-0047-6
  Source data: github.com/danghunccf/CF-GWAS-dataMiningPaper commit eba42429

Outputs:
  results/gwas_modifiers/B1_lifted_hg38.csv.gz      five loci, all variants with liftover
  results/gwas_modifiers/B1_chr16_lifted_hg38.csv.gz  sixth locus, kept separate
  results/gwas_modifiers/B1_rejects.csv             route failures and disagreements
  results/gwas_modifiers/B1_ensembl_cache.json.gz   intermediate cache for route B

Usage:
  python scripts/b1_extract_and_lift.py
  python scripts/b1_extract_and_lift.py --skip-ensembl   # route A only (uses cache if present)
"""

import argparse
import csv
import gzip
import json
import sys
import time
from collections import Counter
from pathlib import Path

import concurrent.futures
import threading

try:
    import requests
except ImportError:
    sys.exit("requests not found: pip install requests")

try:
    from pyliftover import LiftOver
except ImportError:
    sys.exit("pyliftover not found: pip install pyliftover")

# ── paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
PEAKS = BASE / "data/gwas/GWAS_results/gwasImpute2_hg19_SAKNORM_all_meta_fixed_chrPeaks1mb.txt"
OUT_DIR = BASE / "results/gwas_modifiers"
OUT_FIVE = OUT_DIR / "B1_lifted_hg38.csv.gz"
OUT_CHR16 = OUT_DIR / "B1_chr16_lifted_hg38.csv.gz"
OUT_REJECTS = OUT_DIR / "B1_rejects.csv"
ENSEMBL_CACHE = OUT_DIR / "B1_ensembl_cache.json.gz"

# ── constants ──────────────────────────────────────────────────────────────────
SOURCE_COLS = [
    "CHR", "SNP", "BP", "REF", "ALT", "MAF", "k",
    "beta.fix", "z.fix", "p.fix", "beta.ran", "z.ran", "p.ran", "I2",
]

ADDED_COLS = [
    "locus",          # 3q29 / 5p15 / 6p21 / 11p13 / Xq23 / chr16_extra
    "is_snv",         # YES if len(REF)==1 and len(ALT)==1
    "rsid_type",      # clean_rs / multi_rs / no_rs
    "a_chr",          # route A: pyliftover hg38 chromosome
    "a_pos",          # route A: pyliftover hg38 position (1-based)
    "a_strand",       # route A: strand reported by pyliftover
    "a_ok",           # route A: YES / FAIL
    "b_chr",          # route B: Ensembl/dbSNP hg38 chromosome
    "b_pos",          # route B: Ensembl/dbSNP hg38 position (1-based)
    "b_ok",           # route B: YES / FAIL / NA
    "b_note",         # route B: failure reason or blank
    "routes_agree",   # YES / NO / NA
    "hg38_ref",       # reference allele at hg38 position (from Ensembl)
    "orientation",    # REF_ok / ALT_as_hg38ref / strand_flip / strand_flip_swap
                      # ambiguous / mismatch / non_snv / unknown
]

ALL_COLS = SOURCE_COLS + ADDED_COLS

LOCUS_NAMES = {
    "3": "3q29",
    "5": "5p15",
    "6": "6p21",
    "11": "11p13",
    "X": "Xq23",
}

# Complement translation table
_COMP = str.maketrans("ACGTacgt", "TGCAtgca")


# ── helpers ────────────────────────────────────────────────────────────────────

def classify_rsid(snp: str) -> str:
    if not snp.startswith("rs"):
        return "no_rs"
    if ";" in snp:
        return "multi_rs"
    return "clean_rs"


def check_orientation(src_ref: str, src_alt: str, hg38_ref: str) -> str:
    """Compare source REF/ALT against the hg38 reference allele.

    Categories:
      REF_ok           source REF == hg38 reference (standard)
      ALT_as_hg38ref   source ALT == hg38 reference (alleles swapped; beta sign reverses)
      strand_flip      source REF == complement(hg38 ref); coding unchanged, beta sign same
      strand_flip_swap source ALT == complement(hg38 ref); both flipped and swapped
      ambiguous        A/T or C/G SNP — strand indeterminate without MAF matching
      mismatch         none of the above
      non_snv          any allele has length != 1
      unknown          hg38_ref is empty
    """
    if not hg38_ref:
        return "unknown"
    if len(src_ref) != 1 or len(src_alt) != 1 or len(hg38_ref) != 1:
        return "non_snv"
    r = src_ref.upper()
    a = src_alt.upper()
    h = hg38_ref.upper()
    rc = r.translate(_COMP)
    ac = a.translate(_COMP)
    palindromic = (r == ac)  # A/T or C/G pair
    if r == h:
        return "REF_ok_palindromic" if palindromic else "REF_ok"
    if a == h:
        return "ALT_as_hg38ref_palindromic" if palindromic else "ALT_as_hg38ref"
    if rc == h:
        return "strand_flip"
    if ac == h:
        return "strand_flip_swap"
    return "mismatch"


# ── step 1: load peaks ─────────────────────────────────────────────────────────

def load_peaks() -> list[dict]:
    rows = []
    with open(PEAKS) as f:
        header = f.readline().strip().split("\t")
        if header != SOURCE_COLS:
            sys.exit(f"Unexpected header: {header}")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            row = dict(zip(SOURCE_COLS, parts))
            row["locus"] = LOCUS_NAMES.get(row["CHR"], "chr16_extra")
            row["rsid_type"] = classify_rsid(row["SNP"])
            row["is_snv"] = "YES" if len(row["REF"]) == 1 and len(row["ALT"]) == 1 else "NO"
            rows.append(row)
    return rows


# ── step 2: route A — pyliftover ───────────────────────────────────────────────

def route_a(rows: list[dict], lo: LiftOver) -> None:
    for row in rows:
        chrom = "chrX" if row["CHR"] == "X" else f"chr{row['CHR']}"
        pos_0 = int(row["BP"]) - 1          # pyliftover is 0-based
        result = lo.convert_coordinate(chrom, pos_0)
        if result:
            ch38, p38_0, strand, _ = result[0]
            row["a_chr"] = ch38
            row["a_pos"] = str(p38_0 + 1)  # return to 1-based
            row["a_strand"] = strand
            row["a_ok"] = "YES"
        else:
            row["a_chr"] = row["a_pos"] = row["a_strand"] = ""
            row["a_ok"] = "FAIL"


# ── step 3: route B — Ensembl / dbSNP batch lookup ────────────────────────────

def _parse_ensembl_batch(data: dict) -> dict:
    """Extract hg38 position and reference allele from Ensembl variation response."""
    out = {}
    for rsid, info in data.items():
        if not isinstance(info, dict):
            out[rsid] = None
            continue
        grch38 = [m for m in info.get("mappings", [])
                  if m.get("assembly_name") == "GRCh38"]
        if not grch38:
            out[rsid] = None
            continue
        m = grch38[0]
        allele_str = m.get("allele_string", "")
        hg38_ref = allele_str.split("/")[0] if "/" in allele_str else ""
        region = str(m.get("seq_region_name", ""))
        out[rsid] = {
            "chr": f"chr{region}" if region and not region.startswith("chr") else region,
            "pos": m.get("start"),   # 1-based per Ensembl REST API docs
            "hg38_ref": hg38_ref,
        }
    return out


def _fetch_one_batch(batch: list[str], batch_i: int) -> dict:
    url = "https://rest.ensembl.org/variation/homo_sapiens"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    for attempt in range(5):
        try:
            resp = requests.post(
                url,
                headers=headers,
                data=json.dumps({"ids": batch}),
                timeout=90,
            )
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 60))
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return _parse_ensembl_batch(resp.json())
        except requests.RequestException:
            if attempt == 4:
                return {rsid: None for rsid in batch}
            time.sleep(5 * (attempt + 1))
    return {rsid: None for rsid in batch}


def batch_ensembl(rsids: list[str], chunk: int = 200, workers: int = 10) -> dict:
    """POST to Ensembl variation endpoint, parallelised across batches.

    Returns dict: rsid -> {'chr': str, 'pos': int, 'hg38_ref': str} or None.
    Positions are 1-based (Ensembl start field).
    """
    batches = [rsids[i : i + chunk] for i in range(0, len(rsids), chunk)]
    n = len(batches)
    results: dict = {}
    done_lock = threading.Lock()
    done_count = [0]

    def run(args):
        batch_i, batch = args
        result = _fetch_one_batch(batch, batch_i)
        with done_lock:
            results.update(result)
            done_count[0] += 1
            if done_count[0] % 20 == 0 or done_count[0] == n:
                pct = 100 * done_count[0] / n
                print(f"    {done_count[0]}/{n} batches ({pct:.0f}%)", flush=True)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(run, enumerate(batches)))

    return results


def attach_route_b(rows: list[dict], ensembl_map: dict) -> None:
    """Write route B columns and compare to route A."""
    for row in rows:
        rsid_type = row["rsid_type"]
        rsid = row["SNP"]

        if rsid_type != "clean_rs":
            row["b_chr"] = row["b_pos"] = ""
            row["b_ok"] = "NA"
            row["b_note"] = f"no_lookup ({rsid_type})"
            row["routes_agree"] = "NA"
            row["hg38_ref"] = ""
            row["orientation"] = "unknown"
            continue

        if not ensembl_map:
            # Cache not populated yet (skip_ensembl mode)
            row["b_chr"] = row["b_pos"] = ""
            row["b_ok"] = "NA"
            row["b_note"] = "skipped"
            row["routes_agree"] = "NA"
            row["hg38_ref"] = ""
            row["orientation"] = "unknown"
            continue

        info = ensembl_map.get(rsid)
        if info is None:
            row["b_chr"] = row["b_pos"] = ""
            row["b_ok"] = "FAIL"
            row["b_note"] = "not_in_ensembl"
            row["routes_agree"] = "NA"
            row["hg38_ref"] = ""
            row["orientation"] = "unknown"
            continue

        b_chr = info["chr"]
        b_pos = info["pos"]
        hg38_ref = info.get("hg38_ref", "")

        row["b_chr"] = b_chr
        row["b_pos"] = str(b_pos) if b_pos is not None else ""
        row["b_ok"] = "YES"
        row["b_note"] = ""
        row["hg38_ref"] = hg38_ref
        row["orientation"] = check_orientation(row["REF"], row["ALT"], hg38_ref)

        # Compare routes
        if row["a_ok"] != "YES" or b_pos is None:
            row["routes_agree"] = "NA"
        elif row["a_chr"] == b_chr and int(row["a_pos"]) == b_pos:
            row["routes_agree"] = "YES"
        else:
            row["routes_agree"] = "NO"


# ── step 4: write outputs ─────────────────────────────────────────────────────

def write_outputs(rows: list[dict]) -> None:
    five_loci = [r for r in rows if r["locus"] != "chr16_extra"]
    chr16_rows = [r for r in rows if r["locus"] == "chr16_extra"]

    # Rejects: route A failure, route B failure, or disagreement
    rejects = []
    for row in five_loci:
        reasons = []
        if row["a_ok"] == "FAIL":
            reasons.append("route_a_fail")
        if row["b_ok"] == "FAIL":
            reasons.append("route_b_fail")
        if row["routes_agree"] == "NO":
            reasons.append("routes_disagree")
        if reasons:
            r = dict(row)
            r["reject_reason"] = ";".join(reasons)
            rejects.append(r)

    reject_cols = ALL_COLS + ["reject_reason"]
    with open(OUT_REJECTS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=reject_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rejects)

    with gzip.open(OUT_FIVE, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ALL_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(five_loci)

    with gzip.open(OUT_CHR16, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ALL_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(chr16_rows)

    return five_loci, chr16_rows, rejects


# ── summary ────────────────────────────────────────────────────────────────────

def print_summary(five_loci: list[dict], chr16_rows: list[dict], rejects: list[dict]) -> None:
    print("\n" + "=" * 60)
    print("B1 SUMMARY")
    print("=" * 60)

    # Counts per locus
    print(f"\nExtraction (from peaks file):")
    total_five = len(five_loci)
    for locus in ["3q29", "5p15", "6p21", "11p13", "Xq23"]:
        n = sum(1 for r in five_loci if r["locus"] == locus)
        print(f"  {locus}: {n:,}")
    print(f"  Five loci total: {total_five:,}")
    print(f"  Chr16 (kept separate): {len(chr16_rows):,}")

    # rsID types
    rt = Counter(r["rsid_type"] for r in five_loci)
    print(f"\nrsID types (5 loci):")
    print(f"  clean_rs: {rt['clean_rs']:,}")
    print(f"  multi_rs: {rt['multi_rs']:,}")
    print(f"  no_rs:    {rt['no_rs']:,}")

    # Route A
    a_ok = sum(1 for r in five_loci if r["a_ok"] == "YES")
    a_fail = sum(1 for r in five_loci if r["a_ok"] == "FAIL")
    print(f"\nRoute A (pyliftover):")
    print(f"  OK:   {a_ok:,}")
    print(f"  FAIL: {a_fail:,}")

    # Route B
    b_ok = sum(1 for r in five_loci if r["b_ok"] == "YES")
    b_fail = sum(1 for r in five_loci if r["b_ok"] == "FAIL")
    b_na = sum(1 for r in five_loci if r["b_ok"] == "NA")
    print(f"\nRoute B (Ensembl/dbSNP):")
    print(f"  OK:   {b_ok:,}")
    print(f"  FAIL: {b_fail:,}")
    print(f"  N/A (no clean rsID or skipped): {b_na:,}")

    # Agreement
    agree = sum(1 for r in five_loci if r["routes_agree"] == "YES")
    disagree = sum(1 for r in five_loci if r["routes_agree"] == "NO")
    agree_na = sum(1 for r in five_loci if r["routes_agree"] == "NA")
    print(f"\nRoute agreement (clean_rs with both routes OK):")
    print(f"  Agree:    {agree:,}")
    print(f"  Disagree: {disagree:,}")
    print(f"  N/A:      {agree_na:,}")

    # Rejects breakdown
    reason_counts: Counter = Counter()
    for r in rejects:
        for reason in r["reject_reason"].split(";"):
            reason_counts[reason] += 1
    print(f"\nRejects (5 loci) — {len(rejects):,} total:")
    for reason, cnt in reason_counts.most_common():
        print(f"  {reason}: {cnt:,}")

    # SNV / indel
    snv = sum(1 for r in five_loci if r["is_snv"] == "YES")
    indel = sum(1 for r in five_loci if r["is_snv"] == "NO")
    print(f"\nVariant type (5 loci):")
    print(f"  SNVs:   {snv:,}")
    print(f"  Indels: {indel:,}  (excluded from downstream scoring)")

    # Orientation (SNVs with Ensembl data)
    ori = Counter(r["orientation"] for r in five_loci
                  if r["is_snv"] == "YES" and r["b_ok"] == "YES")
    if ori:
        print(f"\nREF/ALT orientation vs hg38 (SNVs with Ensembl data, n={sum(ori.values()):,}):")
        for k, v in ori.most_common():
            print(f"  {k}: {v:,}")

    # Absence of HLA lead SNP
    print("\nNote: rs116003090 (HLA-DRA, Corvol lead SNP for 6p21 locus) is absent")
    print("  from this re-imputation. No summary statistics exist for it here.")

    print("\nOutputs:")
    print(f"  {OUT_FIVE}")
    print(f"  {OUT_CHR16}")
    print(f"  {OUT_REJECTS}")


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-ensembl", action="store_true",
                    help="Skip Ensembl lookup; use cache if present, otherwise route B N/A")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load
    print("Loading peaks file...", flush=True)
    rows = load_peaks()
    print(f"  {len(rows):,} rows loaded", flush=True)

    # 2. Route A
    print("\nRoute A: pyliftover hg19→hg38...", flush=True)
    lo = LiftOver("hg19", "hg38")
    route_a(rows, lo)
    a_ok = sum(1 for r in rows if r["a_ok"] == "YES")
    print(f"  {a_ok:,}/{len(rows):,} lifted", flush=True)

    # 3. Route B
    if ENSEMBL_CACHE.exists():
        print(f"\nRoute B: loading Ensembl cache from {ENSEMBL_CACHE}...", flush=True)
        with gzip.open(ENSEMBL_CACHE, "rt") as f:
            ensembl_map = json.load(f)
        print(f"  {len(ensembl_map):,} cached entries", flush=True)
    elif args.skip_ensembl:
        print("\nRoute B: skipped (--skip-ensembl, no cache present)", flush=True)
        ensembl_map = {}
    else:
        clean_rsids = [r["SNP"] for r in rows if r["rsid_type"] == "clean_rs"]
        print(f"\nRoute B: Ensembl batch lookup for {len(clean_rsids):,} clean rsIDs...",
              flush=True)
        ensembl_map = batch_ensembl(clean_rsids)
        with gzip.open(ENSEMBL_CACHE, "wt") as f:
            json.dump(ensembl_map, f)
        print(f"  Cached {len(ensembl_map):,} entries to {ENSEMBL_CACHE}", flush=True)

    # 4. Attach route B, compare, check orientation
    print("\nComparing routes and checking REF/ALT orientation...", flush=True)
    attach_route_b(rows, ensembl_map)

    # 5. Write outputs
    print("\nWriting outputs...", flush=True)
    five_loci, chr16_rows, rejects = write_outputs(rows)

    # 6. Summary
    print_summary(five_loci, chr16_rows, rejects)


if __name__ == "__main__":
    main()
