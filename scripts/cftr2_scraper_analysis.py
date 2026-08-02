"""
CFTR2 data processing — reproducible script version.

Executable replacement for notebooks/cftr2_scraper.ipynb.
That notebook is out-of-sequence and requires Selenium (browser automation)
for the web scraping steps. Those steps are not reproduced here: the
downloaded input file data/cftr2_variants.xlsx is assumed to exist on disk.

Inputs (must exist on disk):
  data/cftr2_variants.xlsx       — downloaded from cftr2.org, Jan 2026 release
  data/All_Variants_VEP.Gene.vcf — VEP-annotated VCF (3220 variants)

Outputs:
  results/phase1/cftr2_processed_labels.csv  — all VCF variants with CFTR2 labels

This script reproduces the logic of cftr2_scraper.ipynb cells 8–16
(reading from xlsx, matching to VCF variants, producing the labelled table).
The web scraping cells (Selenium, cell 3–4) are not included: they depend on
a browser driver and network access and are not part of the reproducible pipeline.
"""

import os, re, csv, logging
import pandas as pd

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX_PATH = os.path.join(ROOT, 'data', 'cftr2_variants.xlsx')
VCF_PATH  = os.path.join(ROOT, 'data', 'All_Variants_VEP.Gene.vcf')
OUT_DIR   = os.path.join(ROOT, 'results', 'phase1')
OUT_CSV   = os.path.join(ROOT, 'results', 'phase1', 'cftr2_processed_labels.csv')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)
os.makedirs(OUT_DIR, exist_ok=True)

# ── Read CFTR2 data ───────────────────────────────────────────────────────────
log.info('Reading %s', XLSX_PATH)
cftr2_df = pd.read_excel(XLSX_PATH, header=11)

# Standardise column names (the spreadsheet has 5 columns under these headers)
cftr2_df.columns = ['legacy_name', 'protein_name', 'cdna_name',
                     'determination_2026', 'allele_frequency'][:len(cftr2_df.columns)]
cftr2_df = cftr2_df.dropna(subset=['protein_name'])
log.info('CFTR2 rows loaded: %d', len(cftr2_df))

# ── Extract VCF variant protein names ────────────────────────────────────────
protein_pattern = re.compile(r'p\.([A-Z][a-z]{2}\d+[A-Z][a-z]{2})')
variants = []
seen = set()
with open(VCF_PATH, encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        m = protein_pattern.search(line)
        if m:
            pv = m.group(1)
            if pv not in seen:
                seen.add(pv)
                variants.append(pv)

log.info('Unique protein variants from VCF: %d', len(variants))

# ── Match VCF variants to CFTR2 by protein name ───────────────────────────────
# Add p. prefix for matching
cftr2_df['protein_name_clean'] = cftr2_df['protein_name'].str.strip()
result = pd.DataFrame({'variant': variants})
result['protein_name'] = 'p.' + result['variant']

result = result.merge(
    cftr2_df[['protein_name_clean', 'determination_2026', 'allele_frequency']],
    left_on='protein_name',
    right_on='protein_name_clean',
    how='left'
).drop(columns=['protein_name_clean'])

from collections import Counter
det_counts = Counter(result['determination_2026'].fillna('').astype(str))
matched = sum(v for k, v in det_counts.items() if k not in ('', 'nan'))
log.info('Matched to CFTR2: %d / %d', matched, len(variants))
log.info('Determination counts: %s', dict(det_counts))

result.to_csv(OUT_CSV, index=False)
log.info('Saved %s', OUT_CSV)

print('\n=== CFTR2 match summary ===')
print(f'VCF variants: {len(variants)}')
print(f'Matched to CFTR2: {matched}')
for k, v in sorted(det_counts.items()):
    if k and k != 'nan':
        print(f'  {k}: {v}')
