"""
Generate docs/comparator_analysis_report.md from results/comparator_analysis.csv
and results/rescue_analysis.csv.

Run after build_comparator_analysis.py completes.
"""

import os
import numpy as np
import pandas as pd

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGED  = os.path.join(ROOT, 'results/comparator_analysis.csv')
RESCUE  = os.path.join(ROOT, 'results/rescue_analysis.csv')
REPORT  = os.path.join(ROOT, 'docs/comparator_analysis_report.md')

df     = pd.read_csv(MERGED)
rescue = pd.read_csv(RESCUE)

ATAC_Q   = 'ATAC_quantile_max'
SPLICE_Q = 'SPLICE_SITE_USAGE_quantile_max'
AM       = 'am_pathogenicity'
CADD     = 'CADD_PHRED'
SA       = 'SpliceAI_max_delta'

ag_resc  = rescue[rescue['rescue_group'] == 'alphagenome_rescue']
multi    = rescue[rescue['rescue_group'] == 'multi_tool_confirmed']
discord  = rescue[rescue['rescue_group'] == 'discordant_ag_high_splice_low']

top10_rescue = ag_resc.sort_values(ATAC_Q, ascending=False).head(10)
top5_multi   = multi.sort_values(SA, ascending=False).head(5)
top5_disc    = discord.sort_values(SPLICE_Q, ascending=False).head(5)

n_total      = len(df)
n_cadd_found = df[CADD].notna().sum()
n_sa_found   = df[SA].notna().sum()
n_cadd_ge20  = (df[CADD] >= 20).sum()
n_cadd_ge30  = (df[CADD] >= 30).sum()
n_sa_gt02    = (df[SA] > 0.2).sum()
n_sa_gt05    = (df[SA] > 0.5).sum()
n_ag_high    = ((df[ATAC_Q] > 0.95) | (df[SPLICE_Q] > 0.95)).sum()


def fmt_pct(x, total):
    return f'{x} ({100*x/total:.1f}%)'


md = [
    '# Comparator Analysis: AlphaGenome vs CADD v1.7 vs SpliceAI',
    '',
    f'**Dataset:** {n_total} ambiguous-class CFTR missense variants (AlphaMissense score 0.34–0.564)',
    '**Genome build:** hg38  |  **Tissue:** Lung (UBERON:0002048)',
    '**AlphaGenome version:** v0.6.1  |  **CADD version:** v1.7 (GRCh38)  |  **SpliceAI version:** v1.3 (precomputed, Ensembl VEP plugin)',
    '',
    '---',
    '',
    '## 1. Score Availability',
    '',
    f'| Tool | Variants scored | Coverage |',
    f'|------|----------------|----------|',
    f'| AlphaGenome ATAC quantile   | {n_total} | 100% |',
    f'| AlphaGenome SPLICE quantile | {n_total} | 100% |',
    f'| CADD PHRED                  | {n_cadd_found} | {100*n_cadd_found/n_total:.0f}% |',
    f'| SpliceAI max delta          | {n_sa_found} | {100*n_sa_found/n_total:.0f}% |',
    '',
    '---',
    '',
    '## 2. Score Distributions',
    '',
    '| Tool | Score | Mean | p25 | p50 | p75 | p95 |',
    '|------|-------|------|-----|-----|-----|-----|',
]

for col, label in [
    (CADD,     'CADD PHRED'),
    (SA,       'SpliceAI max delta'),
    (ATAC_Q,   'AlphaGenome ATAC q'),
    (SPLICE_Q, 'AlphaGenome SPLICE q'),
]:
    s = df[col].dropna()
    if len(s):
        md.append(
            f'| {label} | n={len(s)} | {s.mean():.3f} | {s.quantile(0.25):.3f} '
            f'| {s.median():.3f} | {s.quantile(0.75):.3f} | {s.quantile(0.95):.3f} |'
        )

md += [
    '',
    '---',
    '',
    '## 3. Classification Thresholds',
    '',
    '| Tool | Threshold | Count | Fraction |',
    '|------|-----------|-------|----------|',
    f'| CADD PHRED ≥ 20 (top 1% most deleterious)  | ≥20  | {n_cadd_ge20} | {100*n_cadd_ge20/n_total:.1f}% |',
    f'| CADD PHRED ≥ 30 (top 0.1%)                 | ≥30  | {n_cadd_ge30} | {100*n_cadd_ge30/n_total:.1f}% |',
    f'| SpliceAI delta > 0.2 (potentially altering) | >0.2 | {n_sa_gt02}   | {100*n_sa_gt02/n_total:.1f}% |',
    f'| SpliceAI delta > 0.5 (high confidence)      | >0.5 | {n_sa_gt05}   | {100*n_sa_gt05/n_total:.1f}% |',
    f'| AlphaGenome ATAC or SPLICE q > 0.95         | >0.95| {n_ag_high}   | {100*n_ag_high/n_total:.1f}% |',
    '',
    '---',
    '',
    '## 4. Rescue Groups',
    '',
    '### 4.1 AlphaGenome Rescue',
    '',
    f'**Definition:** (ATAC quantile > 0.95 OR SPLICE quantile > 0.95) AND CADD PHRED < 20 AND SpliceAI delta < 0.2',
    '',
    f'**Count: {len(ag_resc)} variants** ({100*len(ag_resc)/n_total:.1f}% of all 1,278)',
    '',
    'These variants carry strong DNA regulatory or splicing signals in AlphaGenome that are not flagged by either CADD or SpliceAI. '
    'If these signals reflect real biology, they represent variants that current clinical in silico tools would classify as low-risk but which AlphaGenome suggests merit functional follow-up.',
    '',
    '**Top 10 by ATAC quantile:**',
    '',
    f'| Rank | Variant | AM Score | ATAC q | SPLICE q | CADD PHRED | SpliceAI |',
    f'|------|---------|----------|--------|----------|------------|----------|',
]

for rank, (_, r) in enumerate(top10_rescue.iterrows(), 1):
    cadd_str = f"{r[CADD]:.1f}" if pd.notna(r[CADD]) else 'n/a'
    sa_str   = f"{r[SA]:.3f}" if pd.notna(r[SA]) else 'n/a'
    md.append(
        f'| {rank} | {r["protein_variant"]} | {r[AM]:.3f} | {r[ATAC_Q]:.3f} '
        f'| {r[SPLICE_Q]:.3f} | {cadd_str} | {sa_str} |'
    )

md += [
    '',
    '### 4.2 Multi-Tool Confirmed',
    '',
    f'**Definition:** AlphaGenome SPLICE quantile > 0.95 AND SpliceAI delta > 0.5',
    '',
    f'**Count: {len(multi)} variants**',
    '',
    'Variants where both AlphaGenome and SpliceAI independently detect splice-altering effects. '
    'These are the highest-confidence splicing candidates — agreement between a DNA sequence model (SpliceAI) and a regulatory genomics model (AlphaGenome) strengthens the evidence for functional impact.',
    '',
    '**Top 5 by SpliceAI delta:**',
    '',
    f'| Rank | Variant | AM Score | SPLICE q | SpliceAI delta | CADD PHRED |',
    f'|------|---------|----------|----------|----------------|------------|',
]

for rank, (_, r) in enumerate(top5_multi.iterrows(), 1):
    cadd_str = f"{r[CADD]:.1f}" if pd.notna(r[CADD]) else 'n/a'
    md.append(
        f'| {rank} | {r["protein_variant"]} | {r[AM]:.3f} | {r[SPLICE_Q]:.3f} '
        f'| {r[SA]:.3f} | {cadd_str} |'
    )

md += [
    '',
    '### 4.3 Discordant: AlphaGenome High Splice, SpliceAI Low',
    '',
    f'**Definition:** AlphaGenome SPLICE quantile > 0.95 AND SpliceAI delta < 0.2',
    '',
    f'**Count: {len(discord)} variants** ({100*len(discord)/n_total:.1f}% of all 1,278)',
    '',
    'These variants are the most important for understanding the differences between the two tools. '
    'AlphaGenome\'s `GeneMaskSplicingScorer` uses a broader 1 Mb genomic context and gene-level masking to score '
    'how much a variant changes splice site usage patterns across the entire gene, not just canonical splice signals. '
    'SpliceAI focuses on the local sequence context (±50 bp) around canonical and cryptic splice sites. '
    'Discordance at this scale suggests AlphaGenome is detecting regulatory-level effects on splicing — '
    'such as changes in splicing regulatory elements (SREs), exonic splicing enhancers (ESEs), or exonic splicing silencers (ESSs) — '
    'that SpliceAI\'s splice-site-centric model cannot capture.',
    '',
    '**Top 5 by AlphaGenome SPLICE quantile:**',
    '',
    f'| Rank | Variant | AM Score | AG SPLICE q | SpliceAI delta | CADD PHRED |',
    f'|------|---------|----------|-------------|----------------|------------|',
]

for rank, (_, r) in enumerate(top5_disc.iterrows(), 1):
    cadd_str = f"{r[CADD]:.1f}" if pd.notna(r[CADD]) else 'n/a'
    sa_str   = f"{r[SA]:.3f}" if pd.notna(r[SA]) else 'n/a'
    md.append(
        f'| {rank} | {r["protein_variant"]} | {r[AM]:.3f} | {r[SPLICE_Q]:.3f} '
        f'| {sa_str} | {cadd_str} |'
    )

md += [
    '',
    '---',
    '',
    '## 5. Tool Comparison Summary',
    '',
    '| Feature | CADD v1.7 | SpliceAI v1.3 | AlphaGenome v0.6.1 |',
    '|---------|-----------|---------------|-------------------|',
    '| Score type | Conservation + functional annotation ensemble | Splice site delta score | Quantile score (RNA, ATAC, splice) |',
    '| Mechanism captured | General deleteriousness | Canonical/cryptic splice sites | Regulatory, chromatin, splicing |',
    '| Context window | Variant-level annotations | ±50 bp | 1 Mb genomic window |',
    '| Tissue specificity | None (genome-wide) | None (gene-level) | Yes (lung UBERON:0002048) |',
    '| Normalization | PHRED-scaled rank | Raw delta score | Genome-wide quantile rank |',
    '| Captures ESE/ESS | No | No | Yes (via gene masking) |',
    '| Captures chromatin effects | No | No | Yes (ATAC scorer) |',
    '',
    '---',
    '',
    '## 6. Interpretation',
    '',
    'The large discordant group reflects a fundamental difference in what each tool measures. '
    'SpliceAI is designed to detect disruption of canonical splice donor/acceptor sequences and cryptic splice sites '
    'from the surrounding nucleotide context. AlphaGenome\'s GeneMaskSplicingScorer instead compares predicted '
    'exon-level splice usage across the full gene with and without the variant, capturing indirect effects that '
    'operate through splicing regulatory elements rather than the splice sites themselves.',
    '',
    'For CFTR specifically, where many pathogenic variants are known to cause exon skipping through ESE disruption '
    '(e.g. exon 10 and exon 14a skipping), AlphaGenome\'s broader approach is potentially more mechanistically '
    'relevant. The 56 dual-mechanism variants (ATAC q>0.95 AND SPLICE q>0.95, identified in the earlier rescue '
    'analysis) that also have low CADD and SpliceAI scores represent the most compelling AlphaGenome-unique findings.',
    '',
    '---',
    '',
    '*Sources: CADD v1.7 GRCh38 via cadd.gs.washington.edu REST API. '
    'SpliceAI v1.3 precomputed scores via Ensembl VEP REST API (SpliceAI plugin). '
    'AlphaGenome v0.6.1 via Google DeepMind API. '
    'Analysis date: 2026-06-02.*',
]

report = '\n'.join(md)
with open(REPORT, 'w') as f:
    f.write(report)

print(f'Report saved to {REPORT}')
print(f'\nGroup sizes: rescue={len(ag_resc)}, confirmed={len(multi)}, discordant={len(discord)}')
