# Comparator Analysis: AlphaGenome vs CADD v1.7 vs SpliceAI

**Dataset:** 1,278 ambiguous-class CFTR missense variants (AlphaMissense score 0.34–0.564)
**Genome build:** hg38  |  **Tissue:** Lung (UBERON:0002048)
**AlphaGenome version:** v0.6.1  |  **CADD version:** v1.7 (GRCh38)  |  **SpliceAI version:** v1.3 (precomputed, Ensembl VEP plugin)

---

## 1. Score Availability

| Tool | Variants scored | Coverage |
|------|----------------|----------|
| AlphaGenome ATAC quantile   | 1,278 | 100% |
| AlphaGenome SPLICE quantile | 1,278 | 100% |
| CADD PHRED                  | 1,278 | 100% |
| SpliceAI max delta          | 1,278 | 100% |

---

## 2. Score Distributions

| Tool | n | Mean | p25 | p50 | p75 | p95 |
|------|---|------|-----|-----|-----|-----|
| CADD PHRED           | 1,278 | 24.5  | 23.1  | 24.9  | 26.4  | 28.6  |
| SpliceAI max delta   | 1,278 | 0.037 | 0.000 | 0.000 | 0.020 | 0.161 |
| AlphaGenome ATAC q   | 1,278 | 0.618 | 0.412 | 0.668 | 0.837 | 0.963 |
| AlphaGenome SPLICE q | 1,278 | 0.927 | 0.908 | 0.957 | 0.992 | 0.999 |

---

## 3. Classification Thresholds

| Tool | Threshold | Count | Fraction |
|------|-----------|------:|--------:|
| CADD PHRED ≥ 20 (top 1% most deleterious)   | ≥ 20  | 1,164 | 91.1% |
| CADD PHRED ≥ 30 (top 0.1%)                  | ≥ 30  |    40 |  3.1% |
| SpliceAI delta > 0.2 (potentially altering)  | > 0.2 |    52 |  4.1% |
| SpliceAI delta > 0.5 (high confidence)       | > 0.5 |    19 |  1.5% |
| AlphaGenome ATAC or SPLICE q > 0.95          | > 0.95|   778 | 60.9% |

**Note on CADD discrimination:** 91.1% of all 1,278 ambiguous variants have CADD PHRED ≥ 20. Because CADD flags nearly the entire class as deleterious, it cannot discriminate within the ambiguous group. The CADD < 20 threshold used to define the AlphaGenome rescue group therefore captures only the 8.9% of variants CADD considers genuinely low-impact.

---

## 4. Rescue Groups

### 4.1 AlphaGenome Rescue

**Definition:** (ATAC quantile > 0.95 OR SPLICE quantile > 0.95) AND CADD PHRED < 20 AND SpliceAI delta < 0.2

**Count: 58 variants** (4.5% of all 1,278)

These variants carry strong DNA regulatory or splicing signals in AlphaGenome that are not flagged by either CADD or SpliceAI. If these signals reflect real biology, they represent variants that current clinical in silico tools would classify as low-risk but which AlphaGenome suggests merit functional follow-up.

**Top 10 by ATAC quantile** (deduplicated by protein variant; multiple genomic variants encoding the same amino acid substitution are collapsed to the highest-scoring entry):

| Rank | Variant | AM Score | ATAC q | SPLICE q | CADD PHRED | SpliceAI |
|------|---------|:--------:|:------:|:--------:|:----------:|:--------:|
|  1 | F1413I | 0.487 | 0.999 | 0.996 | 19.2 | 0.000 |
|  2 | Q1411H | 0.357 | 0.999 | 0.960 |  9.2 | 0.000 |
|  3 | Q1412P | 0.548 | 0.995 | 0.960 | 17.1 | 0.000 |
|  4 | H950P  | 0.485 | 0.988 | 0.991 | 19.0 | 0.000 |
|  5 | H954P  | 0.367 | 0.985 | 0.992 | 19.6 | 0.000 |
|  6 | N965K  | 0.422 | 0.977 | 0.996 | 19.7 | 0.080 |
|  7 | I215F  | 0.477 | 0.963 | 0.940 | 18.1 | 0.000 |
|  8 | T940I  | 0.351 | 0.958 | 0.964 | 19.7 | 0.010 |
|  9 | G970C  | 0.491 | 0.933 | 1.000 | 19.8 | 0.860 |
| 10 | I1366L | 0.418 | 0.938 | 1.000 | 19.8 | 0.000 |

### 4.2 Multi-Tool Confirmed

**Definition:** AlphaGenome SPLICE quantile > 0.95 AND SpliceAI delta > 0.5

**Count: 18 variants**

Variants where both AlphaGenome and SpliceAI independently detect splice-altering effects. These are the highest-confidence splicing candidates — agreement between a DNA sequence model (SpliceAI) and a regulatory genomics model (AlphaGenome) strengthens the evidence for functional impact.

**Top 5 by SpliceAI delta:**

| Rank | Variant | AM Score | SPLICE q | SpliceAI delta | CADD PHRED |
|------|---------|----------|----------|----------------|------------|
| 1 | S1058G | 0.507 | 1.000 | 1.000 | 33.0 |
| 2 | A155G | 0.357 | 1.000 | 0.990 | 35.0 |
| 3 | I906S | 0.473 | 1.000 | 0.960 | 34.0 |
| 4 | G1047C | 0.342 | 1.000 | 0.960 | 34.0 |
| 5 | G970V | 0.440 | 0.999 | 0.950 | 27.9 |

### 4.3 Discordant: AlphaGenome High Splice, SpliceAI Low

**Definition:** AlphaGenome SPLICE quantile > 0.95 AND SpliceAI delta < 0.2

**Count: 693 variants** (54.2% of all 1,278)

These variants are the most important for understanding the differences between the two tools. AlphaGenome's `GeneMaskSplicingScorer` uses a broader 1 Mb genomic context and gene-level masking to score how much a variant changes splice site usage patterns across the entire gene, not just canonical splice signals. SpliceAI focuses on the local sequence context (±50 bp) around canonical and cryptic splice sites. Discordance at this scale suggests AlphaGenome is detecting regulatory-level effects on splicing — such as changes in splicing regulatory elements (SREs), exonic splicing enhancers (ESEs), or exonic splicing silencers (ESSs) — that SpliceAI's splice-site-centric model cannot capture.

**Top 5 by AlphaGenome SPLICE quantile:**

| Rank | Variant | AM Score | AG SPLICE q | SpliceAI delta | CADD PHRED |
|------|---------|----------|-------------|----------------|------------|
| 1 | H620Q | 0.417 | 1.000 | 0.000 | 21.5 |
| 2 | A455G | 0.398 | 1.000 | 0.000 | 25.9 |
| 3 | W79C | 0.475 | 1.000 | 0.050 | 26.3 |
| 4 | I906N | 0.354 | 1.000 | 0.040 | 24.9 |
| 5 | I906T | 0.389 | 1.000 | 0.030 | 22.7 |

---

## 5. Tool Comparison Summary

| Feature | CADD v1.7 | SpliceAI v1.3 | AlphaGenome v0.6.1 |
|---------|-----------|---------------|-------------------|
| Score type | Conservation + functional annotation ensemble | Splice site delta score | Quantile score (RNA, ATAC, splice) |
| Mechanism captured | General deleteriousness | Canonical/cryptic splice sites | Regulatory, chromatin, splicing |
| Context window | Variant-level annotations | ±50 bp | 1 Mb genomic window |
| Tissue specificity | None (genome-wide) | None (gene-level) | Yes (lung UBERON:0002048) |
| Normalization | PHRED-scaled rank | Raw delta score | Genome-wide quantile rank |
| Captures ESE/ESS | No | No | Yes (via gene masking) |
| Captures chromatin effects | No | No | Yes (ATAC scorer) |

---

## 6. Interpretation

The large discordant group reflects a fundamental difference in what each tool measures. SpliceAI is designed to detect disruption of canonical splice donor/acceptor sequences and cryptic splice sites from the surrounding nucleotide context. AlphaGenome's GeneMaskSplicingScorer instead compares predicted exon-level splice usage across the full gene with and without the variant, capturing indirect effects that operate through splicing regulatory elements rather than the splice sites themselves.

For CFTR specifically, where many pathogenic variants are known to cause exon skipping through ESE disruption (e.g. exon 10 and exon 14a skipping), AlphaGenome's broader approach is potentially more mechanistically relevant. The 56 dual-mechanism variants (ATAC q>0.95 AND SPLICE q>0.95, identified in the earlier rescue analysis) that also have low CADD and SpliceAI scores represent the most compelling AlphaGenome-unique findings.

---

*Sources: CADD v1.7 GRCh38 via cadd.gs.washington.edu REST API. SpliceAI v1.3 precomputed scores via Ensembl VEP REST API (SpliceAI plugin). AlphaGenome v0.6.1 via Google DeepMind API. Analysis date: 2026-06-02.*