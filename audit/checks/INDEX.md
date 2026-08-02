# Audit Check Index

**Branch:** integrity-audit-2026-07  
**Period:** 29 July – 2 August 2026  
**Total checks:** 21 (numbered 4, 10–21; checks 1–3 and 5–9 are in `audit/AUDIT_REPORT.md`)  

Reports are complete as written. Do not edit them retroactively; add a
dated note at the foot of the relevant file if a finding changes.

---

| Check | File | Date | Subject | Principal finding |
|---|---|---|---|---|
| 4 | [CHECK_4_REPORT.md](CHECK_4_REPORT.md) | 2026-08-02 | Population frequency field identity and VCF provenance | CSQ field 34 = AF_TGP (1000 Genomes), not gnomAD. The input VCF is a ClinVar annotation file, not a patient cohort. Both misdescrptions appear throughout the repository. |
| 10 | [CHECK_10_REPORT.md](CHECK_10_REPORT.md) | 2026-08-02 | Phase 1 benchmark duplicates | 33 duplicate rows from a one-to-many merge on protein variant name inflate n=259 to n=292. AUC 0.946 → 0.9549, AP 0.990 → 0.9924 on the deduplicated cohort. |
| 11 | [CHECK_11_REPORT.md](CHECK_11_REPORT.md) | 2026-08-02 | Synonymous codon-pair analysis: within-group AlphaGenome concordance | AlphaGenome splice and ATAC are significantly more concordant within same-amino-acid groups than proximity-matched controls (p < 0.0001). The within-group constraint is real and exceeds proximity effects. |
| 12+13 | [CHECK_12_13_REPORT.md](CHECK_12_13_REPORT.md) | 2026-08-02 | 693 discordant variants; threshold sensitivity | Observed 693 against ~717 expected under independence; the discordant group is at chance. The count drops from 693 to 324 with one threshold step, confirming strong threshold dependence. |
| 14 | [CHECK_14_REPORT.md](CHECK_14_REPORT.md) | 2026-08-02 | Per-bin predict_variant analysis; codon-pair divergence | H620Q T>G vs T>A showed per-bin divergence up to 13.92 log2FC. (Retracted in Check 15: numerical artefact of log2 at near-zero coding positions.) |
| 15 | [CHECK_15_REPORT.md](CHECK_15_REPORT.md) | 2026-08-02 | GeneMaskSplicingScorer quantization; Check 14b retraction; center-mask rescore | Raw scores have 87 unique values (multiples of 1/256); scorer returns gene-body max, not variant effect. Check 14b per-bin divergence is a log2(near-zero) artefact. Center-mask rescore confirms codon-pair synonymy. |
| 16 | [CHECK_16_REPORT.md](CHECK_16_REPORT.md) | 2026-08-02 | CM L2D scorer on experimental benchmark; distance stratification | CM L2D: 0/12 false positives at top-20% threshold vs 8/12 for GM quantile. All three AlphaGenome scorers AUROC 0.833–0.856 with overlapping CIs at n=23. 41% of cohort lies beyond SpliceAI ±50 nt window. |
| 17 | [CHECK_17_REPORT.md](CHECK_17_REPORT.md) | 2026-08-02 | Priority-7 variant selection; 12-variant positive control | Priority-7 selected on 1000 Genomes singletons (all seven singletons or doubletons in 2,504 persons). 12-variant positive control not elevated on any AlphaGenome metric; p > 0.05 across all tests; CI spanning full range. Both retracted. |
| 18 | [CHECK_18_REPORT.md](CHECK_18_REPORT.md) | 2026-08-02 | Operating point correction; concordant-set definition; SpliceAI coverage | GM threshold clears 58.4% of cohort; CM top-5% clears 5.2%. Comparison at original thresholds was not operating-point-matched. CM splice 501 top 5% AND SpliceAI > 0.2 (27 variants, OR=35.7) established as primary concordant-set definition. |
| 19 | [CHECK_19_REPORT.md](CHECK_19_REPORT.md) | 2026-08-02 | Experimental benchmark at matched operating points; SpliceAI coverage on 23 variants | At matched sensitivity, AUROC overlapping for all three AlphaGenome scorers (0.833–0.856, CIs ~±0.18). SpliceAI scored only 2/23 experimental variants; AUROC 0.432 is a coverage artefact. No scorer choice is justifiable from this data. |

| 20 | *No separate report file* | 2026-08-02 | Literature verification; AlphaGenome quantile background and calibration change | (a) AlphaGenome FAQ confirms quantile background is common variants (MAF > 0.01, gnomAD v3), not all human variation — phrase corrected throughout. (b) Calibration changed from chr22-only to genome-wide on 18 June 2026; project run (28 May) used chr22 background. (c) Two rescoring runs 6 minutes apart agree exactly; backend changed between May and August, cause undocumented. (d) Quantization claim corrected: 87 unique values are in the raw column; quantile column has 290. Corrections applied to `docs/` and `audit/checks/CHECK_15_REPORT.md`, `CHECK_18_REPORT.md`, `CHECK_19_REPORT.md`. |
| 21 | *No separate report file* | 2026-08-02 | Quantile regeneration; raw score change investigation; determinism test | Full 1,278-variant rescore under genome-wide calibration written to `results/alphagenome/quantiles_genomewide_2026-08.csv` with `raw_changed` flag. 75 variants have different raw scores between May and August runs; cause not determinable (no changelog). Two runs 6 minutes apart agree exactly (backend is not non-deterministic over short intervals); 7-day stability untested (rerun due 2026-08-09). Key metrics on unaffected-1,203 subset: % above 0.95 rises from 57.7% to 62.8% under genome-wide calibration; 693→704; 18→18; 58→62. |

---

## Checks not in this directory

Checks 1–3 and 5–9 were conducted as part of the initial audit sweep
and are recorded in `audit/AUDIT_REPORT.md` and `audit/CLAIMS_LEDGER.csv`
rather than as standalone reports. Their subjects:

- **Checks 1–3:** CFTR2 scraper output validation, variant counts, CFTR2 snapshot date (confirmed 30 January 2026)
- **Checks 5–9:** DeLong recomputation with covariance term (all pairwise comparisons more significant); SpliceAI zero reclassification; notebook OOS sweep; cohort provenance; McDonald et al. re-binarisation

Check 20 (AlphaGenome quantile source verification; calibration change; quantile regeneration; determinism test; quantization claim correction) is recorded in the conversation transcript and its corrections are applied directly to `docs/` and `audit/checks/CHECK_15_REPORT.md`. No separate CHECK_20_REPORT.md was written.
