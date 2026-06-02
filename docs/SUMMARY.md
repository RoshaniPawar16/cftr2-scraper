# CFTR Variant Pathogenicity Analysis -- Summary

## Background

A VEP-annotated VCF with 3,220 CFTR gene variants needed clinical annotations. CFTR2 is the authoritative database for variant classification in cystic fibrosis. It is built from data across 122,935 patients.

Only 656 variants matched CFTR2. 80% had no clinical classification. That gap is the starting point for this analysis.

## What we did

We applied AlphaMissense, a pathogenicity predictor from Google DeepMind, to the full variant set. AlphaMissense was built from protein structure and evolutionary data, with no knowledge of CFTR2 classifications. That independence makes it useful as an external signal.

Before applying it to unknown variants, we validated it against the 292 variants that do have CFTR2 labels. It achieved AUC 0.946. We then benchmarked it against three standard predictors: CADD, PolyPhen, and SIFT. AlphaMissense outperformed all three. We also tested whether combining predictors in an ensemble could beat AlphaMissense alone -- it could not.

## Key findings

**7 priority candidates**

Of 705 unclassified variants flagged as likely pathogenic, 7 have population frequency support from gnomAD. All 7 are unresolved in ClinVar. 5 are uncertain significance, 2 have conflicting classifications from different labs. AlphaMissense calls all 7 likely pathogenic. These are the strongest candidates for functional follow-up.

**Varying clinical consequence group**

72 variants in CFTR2 are classified as varying clinical consequence, meaning CFTR2 itself is uncertain. AlphaMissense called 41 of those 72 likely pathogenic. Those 41 variants cluster heavily in the membrane-spanning domains (MSD1 and MSD2), which form the chloride channel pore. 73% of the likely pathogenic calls fall in these two domains. The regulatory domain had zero. This reflects where structural disruption is most consequential.

Arg117His, a well-known mild variant associated with CBAVD rather than classic CF, scored 0.299 (likely benign). That is consistent with clinical knowledge and validates the model's sensitivity to functional context.

**Nonsense variants**

311 variants were nonsense mutations and could not be scored by AlphaMissense. Of those, 225 matched CFTR2 as CF-causing, consistent with the expectation that premature stop codons truncate the protein and cause disease. Two exceptions: Ser1455Ter and Gln1476Ter, which truncate only the last 25 and 4 residues respectively. Their classification as varying clinical consequence is biologically justified.

## What this shows

AlphaMissense is a credible tool for prioritising unclassified CFTR variants. It agrees with ground truth at AUC 0.946 and outperforms all three standard baselines. Combining it with other predictors does not help -- the ensemble is worse, confirming AlphaMissense already captures what the others offer. The 7 priority candidates and the domain clustering of uncertain variants are findings that warrant experimental follow-up.

## Limitations

- Validation set is imbalanced. 253 CF-causing vs 39 Non CF-causing. AUC is robust to this but the F1 on Non CF-causing variants should be interpreted carefully.
- Population frequency data was available for only 117 of 3,220 variants. Most are too rare for gnomAD.
- AlphaMissense scores missense variants only. Nonsense, frameshift and splicing variants are outside its scope.
- One VCF from one cohort. Findings should be validated on a larger dataset before clinical use.

## Full documentation

See `docs/REPORT.md` for the full academic paper with methods, results, and references.
