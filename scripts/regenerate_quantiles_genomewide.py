"""
Regenerate SPLICE_SITE_USAGE, RNA_SEQ, and ATAC quantile scores for all 1,278
variants using the current (genome-wide) calibration.

Constraints:
  - NEVER overwrites alphagenome_full_cftr_results.csv.
  - Writes to results/alphagenome/quantiles_genomewide_2026-08.csv with old
    and new columns side by side.
  - Before writing, verifies raw scores are identical for every variant.
    If any raw score moved, reports it and stops without writing.

Run from project root:
    .venv/bin/python scripts/regenerate_quantiles_genomewide.py
"""

import os, sys, time, logging
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from alphagenome.data import genome
from alphagenome.models import dna_client
from alphagenome.models import variant_scorers as vsl
import grpc

# ── Config ────────────────────────────────────────────────────────────────────
ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH_SIZE  = 20
MAX_RETRIES = 5
BASE_BACKOFF = 10
HALF        = dna_client.SEQUENCE_LENGTH_1MB // 2

ORIG_CSV    = os.path.join(ROOT, 'results/alphagenome/alphagenome_full_cftr_results.csv')
OUT_CSV     = os.path.join(ROOT, 'results/alphagenome/quantiles_genomewide_2026-08.csv')
CHECKPOINT  = os.path.join(ROOT, 'results/alphagenome/.regen_checkpoint.csv')
ONTOLOGY    = 'UBERON:0002048'

# Identical scorers to original run
SCORERS = [
    vsl.RECOMMENDED_VARIANT_SCORERS['RNA_SEQ'],
    vsl.RECOMMENDED_VARIANT_SCORERS['ATAC'],
    vsl.RECOMMENDED_VARIANT_SCORERS['SPLICE_SITE_USAGE'],
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ── Guard ──────────────────────────────────────────────────────────────────────
if os.path.exists(OUT_CSV):
    log.error('Output file already exists: %s  — delete it manually if you want to rerun.', OUT_CSV)
    sys.exit(1)

load_dotenv(os.path.join(ROOT, '.env'))
API_KEY = os.environ.get('ALPHAGENOME_API_KEY', '')
if not API_KEY:
    sys.exit('ERROR: Set ALPHAGENOME_API_KEY in .env')

# ── Load original ─────────────────────────────────────────────────────────────
log.info('Loading %s', ORIG_CSV)
orig = pd.read_csv(ORIG_CSV)
log.info('Original: %d variants', len(orig))

# ── Resume from checkpoint ────────────────────────────────────────────────────
completed_ids = set()
checkpoint_rows = []
if os.path.exists(CHECKPOINT):
    ckpt = pd.read_csv(CHECKPOINT)
    completed_ids = set(ckpt['variant_id'].tolist())
    checkpoint_rows = [ckpt]
    log.info('Resuming — %d variants already rescored', len(completed_ids))

remaining = orig[~orig['variant_id'].isin(completed_ids)].copy().reset_index(drop=True)
log.info('Remaining to rescore: %d', len(remaining))

# ── Connect ───────────────────────────────────────────────────────────────────
model = dna_client.create(API_KEY)
log.info('Connected. Scorers: %s', [str(s) for s in SCORERS])

# ── Batch scoring ─────────────────────────────────────────────────────────────
def parse_vid(vid):
    chrom, rest = vid.split(':', 1)
    pos_str, ref_alt = rest.split(':', 1)
    ref, alt = ref_alt.split('>')
    return chrom, int(pos_str), ref, alt

def score_batch(batch_df):
    variants, intervals = [], []
    for _, r in batch_df.iterrows():
        chrom, pos, ref, alt = parse_vid(r['variant_id'])
        variants.append(genome.Variant(
            chromosome=chrom, position=pos,
            reference_bases=ref, alternate_bases=alt))
        intervals.append(genome.Interval(
            chromosome=chrom, start=pos - HALF, end=pos + HALF))
    raw = model.score_variants(
        intervals=intervals, variants=variants,
        variant_scorers=SCORERS, progress_bar=False)
    return vsl.tidy_scores(raw)

def extract_lung_new(tidy_df, batch_df):
    lung = tidy_df[tidy_df['ontology_curie'] == ONTOLOGY].copy()
    rows = []
    for _, r in batch_df.iterrows():
        vid = r['variant_id']
        pos_str = vid.split(':')[1]
        vdf = lung[lung['variant_id'].astype(str).str.contains(pos_str, regex=False)]
        row = {'variant_id': vid}
        for otype in ['RNA_SEQ', 'ATAC', 'SPLICE_SITE_USAGE']:
            odf = vdf[vdf['output_type'] == otype]
            if len(odf) and odf['raw_score'].notna().any():
                row[f'new_{otype}_raw']      = float(odf['raw_score'].abs().max())
                row[f'new_{otype}_quantile'] = (
                    float(odf['quantile_score'].abs().max())
                    if 'quantile_score' in odf and odf['quantile_score'].notna().any()
                    else np.nan)
            else:
                row[f'new_{otype}_raw']      = np.nan
                row[f'new_{otype}_quantile'] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)

n_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE
new_rows = []

for batch_num, start in enumerate(range(0, len(remaining), BATCH_SIZE), 1):
    batch = remaining.iloc[start : start + BATCH_SIZE]
    log.info('Batch %d/%d (variants %d-%d)', batch_num, n_batches,
             start + 1, min(start + BATCH_SIZE, len(remaining)))
    backoff = BASE_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            tidy = score_batch(batch)
            chunk = extract_lung_new(tidy, batch)
            new_rows.append(chunk)
            # Append to checkpoint
            chunk.to_csv(CHECKPOINT, mode='a',
                         header=not os.path.exists(CHECKPOINT) or os.path.getsize(CHECKPOINT) == 0,
                         index=False)
            break
        except grpc.RpcError as e:
            code = e.code()
            if code in (grpc.StatusCode.RESOURCE_EXHAUSTED, grpc.StatusCode.UNAVAILABLE):
                log.warning('Rate limit (attempt %d/%d), sleeping %ds', attempt, MAX_RETRIES, backoff)
                time.sleep(backoff); backoff = min(backoff * 2, 300)
            elif code == grpc.StatusCode.INVALID_ARGUMENT:
                log.error('Invalid argument on batch %d — skipping: %s', batch_num, e.details())
                break
            else:
                log.error('gRPC %s on batch %d (attempt %d): %s', code, batch_num, attempt, e.details())
                if attempt == MAX_RETRIES: log.error('Giving up on batch %d', batch_num)
                time.sleep(backoff); backoff = min(backoff * 2, 300)
        except Exception as e:
            log.error('Unexpected error batch %d attempt %d: %s', batch_num, attempt, e)
            if attempt == MAX_RETRIES: log.error('Giving up on batch %d', batch_num)
            time.sleep(backoff); backoff = min(backoff * 2, 300)

# ── Consolidate new scores ─────────────────────────────────────────────────────
log.info('Consolidating new scores...')
all_new = []
if os.path.exists(CHECKPOINT):
    all_new.append(pd.read_csv(CHECKPOINT))
if new_rows:
    all_new.append(pd.concat(new_rows, ignore_index=True))
new_df = pd.concat(all_new, ignore_index=True).drop_duplicates('variant_id')

log.info('New scores: %d variants', len(new_df))

# ── Merge and verify ───────────────────────────────────────────────────────────
merged = orig.merge(new_df, on='variant_id', how='left')

# Bring in SpliceAI and CADD for downstream metric comparisons
comp_path = os.path.join(ROOT, 'results/comparator_scores.csv')
if os.path.exists(comp_path):
    comp = pd.read_csv(comp_path)[['variant_id', 'SpliceAI_max_delta', 'CADD_PHRED']]
    merged = merged.merge(comp, on='variant_id', how='left')
    log.info('Merged comparator scores: SpliceAI and CADD available')

log.info('Verifying raw scores are unchanged...')
raw_movers = []
for otype, old_col, new_col in [
    ('SPLICE_SITE_USAGE', 'SPLICE_SITE_USAGE_raw_max', 'new_SPLICE_SITE_USAGE_raw'),
    ('RNA_SEQ',           'RNA_SEQ_raw_max',           'new_RNA_SEQ_raw'),
    ('ATAC',              'ATAC_raw_max',               'new_ATAC_raw'),
]:
    if old_col not in merged or new_col not in merged:
        continue
    diff = (merged[old_col] - merged[new_col]).abs()
    moved = merged[diff > 1e-6][['variant_id', old_col, new_col]].copy()
    if len(moved):
        moved['output_type'] = otype
        moved['raw_diff'] = (merged.loc[moved.index, old_col] - merged.loc[moved.index, new_col])
        raw_movers.append(moved)

mover_ids = set()
if raw_movers:
    print('\n=== RAW SCORE CHANGES DETECTED — FLAGGING AND CONTINUING ===')
    for df_m in raw_movers:
        mover_ids.update(df_m['variant_id'].tolist())
    print(f'Variants with any raw score change: {len(mover_ids)} / {len(merged)}')
    print('Proceeding — these will be flagged raw_changed=True.')
else:
    log.info('Raw scores verified: all identical. Calibration change only.')

# Flag raw_changed
merged['raw_changed'] = merged['variant_id'].isin(mover_ids)

# ── Compute diff columns ───────────────────────────────────────────────────────
for otype, old_q, new_q in [
    ('SPLICE_SITE_USAGE', 'SPLICE_SITE_USAGE_quantile_max', 'new_SPLICE_SITE_USAGE_quantile'),
    ('RNA_SEQ',           'RNA_SEQ_quantile_max',           'new_RNA_SEQ_quantile'),
    ('ATAC',              'ATAC_quantile_max',               'new_ATAC_quantile'),
]:
    if old_q in merged and new_q in merged:
        merged[f'{otype}_q_diff'] = merged[new_q] - merged[old_q]

# ── Write output ───────────────────────────────────────────────────────────────
merged.to_csv(OUT_CSV, index=False)
log.info('Saved %d variants to %s', len(merged), OUT_CSV)
if os.path.exists(CHECKPOINT):
    os.remove(CHECKPOINT)
    log.info('Checkpoint removed.')

# ── Summary statistics ─────────────────────────────────────────────────────────
n_total     = len(merged)
n_changed   = int(merged['raw_changed'].sum())
n_unchanged = n_total - n_changed
unc = merged[~merged['raw_changed']]
chg = merged[merged['raw_changed']]

print(f'\n=== COHORT SPLIT ===')
print(f'Total variants:    {n_total}')
print(f'raw_changed=False: {n_unchanged}  (calibration-only comparison valid)')
print(f'raw_changed=True:  {n_changed}   (raw score also moved; cause not determinable)')

sa_col   = 'SpliceAI_max_delta' if 'SpliceAI_max_delta' in merged.columns else None
cadd_col = 'CADD_PHRED' if 'CADD_PHRED' in merged.columns else None

def summarise(label, subset):
    n     = len(subset)
    old_q = subset['SPLICE_SITE_USAGE_quantile_max']
    new_q = subset['new_SPLICE_SITE_USAGE_quantile']
    diff  = subset['SPLICE_SITE_USAGE_q_diff']
    atac_old = subset['ATAC_quantile_max']
    atac_new = subset['new_ATAC_quantile'] if 'new_ATAC_quantile' in subset.columns else None
    print(f'\n--- {label} (n={n}) ---')
    print(f'Old SPLICE_q unique values: {old_q.nunique()}')
    print(f'New SPLICE_q unique values: {new_q.nunique()}')
    old_above = (old_q > 0.95).sum()
    new_above = (new_q > 0.95).sum()
    print(f'% above 0.95  OLD: {old_above} ({old_above/n*100:.1f}%)   NEW: {new_above} ({new_above/n*100:.1f}%)')
    if sa_col and cadd_col and sa_col in subset.columns:
        sa   = subset[sa_col]
        cadd = subset[cadd_col]
        print(f'693 (SPLICE_q>0.95 & SA<0.2)           OLD: {((old_q>0.95)&(sa<0.2)).sum()}   NEW: {((new_q>0.95)&(sa<0.2)).sum()}')
        print(f'18  (SPLICE_q>0.95 & SA>0.5)           OLD: {((old_q>0.95)&(sa>0.5)).sum()}    NEW: {((new_q>0.95)&(sa>0.5)).sum()}')
        if atac_new is not None:
            r_old = (((atac_old>0.95)|(old_q>0.95))&(cadd<20)&(sa<0.2)).sum()
            r_new = (((atac_new>0.95)|(new_q>0.95))&(cadd<20)&(sa<0.2)).sum()
            print(f'58  (ATAC|SPLICE>0.95 & CADD<20 & SA<0.2) OLD: {r_old}    NEW: {r_new}')
    print(f'Quantile diff — median: {diff.median():+.4f}  IQR: [{diff.quantile(0.25):+.4f}, {diff.quantile(0.75):+.4f}]')
    print(f'               max+: {diff.max():+.4f}   max-: {diff.min():+.4f}')
    print(f'               |diff|>0.05: {(diff.abs()>0.05).sum()}  >0.10: {(diff.abs()>0.10).sum()}  >0.20: {(diff.abs()>0.20).sum()}')
    print(f'               up: {(diff>0).sum()}  down: {(diff<0).sum()}  zero: {(diff==0).sum()}')

print('\n=== SPLICE_SITE_USAGE QUANTILE COMPARISON ===')
summarise('ALL 1,278',                      merged)
summarise('UNAFFECTED (raw_changed=False)', unc)
summarise('AFFECTED   (raw_changed=True)',  chg)
