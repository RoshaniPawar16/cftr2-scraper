# Phase 1 Input Sources

| file | sha256 (full) | description |
|---|---|---|
| data/AlphaMissense_hg38.tsv.gz | 0516cfd71c0767ac8f9c469252d429000e94e02c008b6e3a46d4b4646fcd3475 | AlphaMissense scores (Zenodo 8208688), filtered to CFTR (P13569) via cftr_alphamissense.tsv |
| data/cftr2_results_annotated.csv | f24c58ff4e28e376d90699c3c61d3cd54c91ac2ae7989bdd9db55d61ac82386f | CFTR2 Jan 2026 release merged with AM scores; source of binary labels and AM pathogenicity |
| data/All_Variants_VEP.Gene.vcf | cf6d19825364c63186a4780ffb8e11ecbfb0a44de2a5da8ab36cc1fa6dcf5283 | VEP-annotated VCF; source of SIFT and PolyPhen scores via CSQ field (indices 31, 32) |
| data/cftr_alphamissense.tsv | 337733b0be80af8ed7fd79779d3037c9cd3229df452bdfe71751e36e59f3e3bb | CFTR-filtered AlphaMissense scores from AlphaMissense_hg38.tsv.gz |

| results/phase1/inputs_cadd_raw.json | 54c2b7a8ac08299772612de283b4a3923b952d2c8a7b0f269935472f2db30501 | Raw CADD API responses before parsing |
