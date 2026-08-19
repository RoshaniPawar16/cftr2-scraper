"""
ACMG-LLM Orthogonality Experiment
===================================
Tests whether AlphaMissense and LLM-based ACMG/AMP criterion reasoning fail on
orthogonal subsets of the 292 CFTR2-labelled variants.

Setup:
    pip install anthropic python-dotenv pandas
    # Set ANTHROPIC_API_KEY in .env

Usage:
    python scripts/acmg_llm_experiment.py              # full 292-variant run
    python scripts/acmg_llm_experiment.py --dry-run 5  # smoke-test with 5 variants
    python scripts/acmg_llm_experiment.py --skip-consistency
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

try:
    import anthropic
except ImportError:
    sys.exit(
        "anthropic SDK not installed.\n"
        "Run: pip install anthropic\n"
        "Then retry."
    )

# ── paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PHASE1_DIR = PROJECT_ROOT / "results" / "phase1"

ANNOTATED_CSV = DATA_DIR / "cftr2_results_annotated.csv"
CADD_CSV = PHASE1_DIR / "inputs_cadd_scores.csv"
PPSIFT_CSV = PHASE1_DIR / "inputs_polyphen_sift.csv"

OUTPUT_DIR = PROJECT_ROOT / "results" / "acmg_llm"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = OUTPUT_DIR / "per_variant_log.jsonl"
SUMMARY_FILE = OUTPUT_DIR / "experiment_summary.json"

# ── constants ─────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"   # supports temperature=0; claude-opus-5 rejects it
TEMPERATURE = 0
AM_THRESHOLD = 0.564

DOMAINS: list[tuple[str, int, int]] = [
    ("MSD1", 1, 394),
    ("NBD1", 395, 646),
    ("R-domain", 647, 835),
    ("MSD2", 836, 1172),
    ("NBD2", 1173, 1480),
]

# ── domain extraction ─────────────────────────────────────────────────────────

def get_domain(variant: str) -> str:
    """Map a three-letter variant string to its CFTR functional domain."""
    m = re.search(r"\d+", variant)
    if not m:
        return "unknown"
    pos = int(m.group())
    for name, start, end in DOMAINS:
        if start <= pos <= end:
            return name
    return "outside_known_domains"


# ── data loading ──────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    """Load and inner-join the three input CSVs; return labelled variant DataFrame."""
    ann = pd.read_csv(ANNOTATED_CSV)
    cadd = pd.read_csv(CADD_CSV)[["variant", "cadd_phred"]].drop_duplicates("variant")
    ppsift = pd.read_csv(PPSIFT_CSV)

    labelled = ann[ann["determination_2026"].isin(["CF-causing", "Non CF-causing"])].copy()
    df = labelled.merge(cadd, on="variant", how="left")
    df = df.merge(ppsift, on="variant", how="left")
    df["domain"] = df["variant"].apply(get_domain)

    if len(df) != 292:
        print(f"WARNING: Expected 292 labelled variants, got {len(df)}", file=sys.stderr)

    return df.reset_index(drop=True)


# ── prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a clinical variant-classification assistant applying the ACMG/AMP 2015\n"
    "guidelines (Richards et al., Genet Med 2015) to CFTR missense variants.\n"
    "\n"
    "You may ONLY use the evidence provided inside <variant_data> tags. Do not use\n"
    "outside knowledge about the specific variant, and do not guess values that are\n"
    "not provided. If evidence for a criterion is absent, mark it \"not_evaluable\".\n"
    "\n"
    "Evaluate ONLY these five criteria:\n"
    "- PM1: variant in a mutational hotspot or well-established functional domain\n"
    "  (for CFTR: membrane-spanning domains MSD1/MSD2 and nucleotide-binding\n"
    "  domains NBD1/NBD2 are critical; the R-domain is intrinsically disordered\n"
    "  and more tolerant).\n"
    "- PM2: absent from population databases, or at extremely low frequency\n"
    "  (gnomAD AF < 0.0001 supports PM2 for an autosomal recessive disorder).\n"
    "- PP3: computational evidence supports a deleterious effect. Per ClinGen SVI\n"
    "  calibration (Pejaver et al. 2022), apply PP3 at SUPPORTING strength when\n"
    "  tools moderately agree, or at MODERATE strength (PP3_Moderate) when\n"
    "  multiple tools strongly and concordantly indicate deleterious effect.\n"
    "- BP4: multiple computational tools support a benign effect.\n"
    "- BS3: well-established functional studies show no damaging effect\n"
    "  (only if functional data is provided).\n"
    "\n"
    "Reason step by step inside <reasoning> tags FIRST, criterion by criterion.\n"
    "Then output ONLY a JSON object inside <answer> tags with this exact schema:\n"
    "{\n"
    "  \"criteria\": {\n"
    "    \"PM1\": \"met\" | \"not_met\" | \"not_evaluable\",\n"
    "    \"PM2\": \"met\" | \"not_met\" | \"not_evaluable\",\n"
    "    \"PP3\": \"met_supporting\" | \"met_moderate\" | \"not_met\" | \"not_evaluable\",\n"
    "    \"BP4\": \"met\" | \"not_met\" | \"not_evaluable\",\n"
    "    \"BS3\": \"met\" | \"not_met\" | \"not_evaluable\"\n"
    "  },\n"
    "  \"classification\": \"pathogenic\" | \"likely_pathogenic\" | \"vus\" |\n"
    "                    \"likely_benign\" | \"benign\",\n"
    "  \"confidence\": \"high\" | \"moderate\" | \"low\",\n"
    "  \"deciding_evidence\": \"<one sentence naming the decisive criterion>\"\n"
    "}\n"
    "Apply the ACMG combining rules to the criteria you marked \"met\" to reach the\n"
    "classification. If met criteria are insufficient to reach any class, output \"vus\".\n"
    "Treat PP3 marked met_moderate as moderate-strength evidence in the combining rules."
)

USER_TEMPLATE = """\
<variant_data>
  <gene>CFTR</gene>
  <protein_change>{name}</protein_change>
  <domain>{domain}</domain>
  <alphamissense_score>{am}</alphamissense_score>
  <cadd_phred>{cadd}</cadd_phred>
  <polyphen>{pp}</polyphen>
  <sift>{sift}</sift>
  <gnomad_af>{af}</gnomad_af>
  <functional_assay>not_available</functional_assay>
</variant_data>

Classify this variant."""

PARAPHRASED_USER_TEMPLATE = """\
Please evaluate the following variant using the ACMG/AMP criteria in your \
system instructions.

<variant_data>
  <gene>CFTR</gene>
  <protein_change>{name}</protein_change>
  <domain>{domain}</domain>
  <alphamissense_score>{am}</alphamissense_score>
  <cadd_phred>{cadd}</cadd_phred>
  <polyphen>{pp}</polyphen>
  <sift>{sift}</sift>
  <gnomad_af>{af}</gnomad_af>
  <functional_assay>not_available</functional_assay>
</variant_data>

What is the ACMG/AMP classification for this variant?"""


def _fmt_row(row) -> dict[str, str]:
    """Format a DataFrame row into template-substitution dict."""

    def _val(x, fmt: str = "{}") -> str:
        if pd.isna(x):
            return "not_available"
        return fmt.format(x)

    return {
        "name": row.variant,
        "domain": row.domain,
        "am": _val(row.am_pathogenicity),
        "cadd": _val(row.cadd_phred),
        "pp": _val(row.polyphen_raw),
        "sift": _val(row.sift_raw),
        "af": _val(row.allele_frequency, "{:.6g}"),
    }


# ── API call ──────────────────────────────────────────────────────────────────

def call_llm(client: anthropic.Anthropic, user_message: str, retries: int = 3) -> tuple[str, str]:
    """Call Claude; return (response_text, stop_reason). Retries on rate-limit errors."""
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=3000,
                temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text, response.stop_reason
        except anthropic.RateLimitError:
            wait = 60 * (attempt + 1)
            print(f"  Rate limit; waiting {wait}s…", file=sys.stderr)
            time.sleep(wait)
        except anthropic.APIError as exc:
            print(f"  API error (attempt {attempt + 1}): {exc}", file=sys.stderr)
            if attempt == retries - 1:
                raise
            time.sleep(5)
    raise RuntimeError("All retries exhausted")


def parse_answer(raw: str) -> dict:
    """Extract and parse JSON from the <answer> block in the response."""
    m = re.search(r"<answer>\s*(.*?)\s*</answer>", raw, re.DOTALL)
    if not m:
        return {"parse_error": "no <answer> block found", "raw_excerpt": raw[:400]}
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        return {"parse_error": str(exc), "raw_excerpt": m.group(1)[:400]}


def _to_binary(classification: str | None) -> str | None:
    """Collapse 5-tier ACMG classification to CF-causing / Non-CF-causing."""
    if classification in ("pathogenic", "likely_pathogenic"):
        return "CF-causing"
    if classification in ("vus", "likely_benign", "benign"):
        return "Non-CF-causing"
    return None


# ── classification run ────────────────────────────────────────────────────────

def run_experiment(
    df: pd.DataFrame,
    client: anthropic.Anthropic,
    dry_run: int | None,
) -> list[dict]:
    """Classify all (or dry_run) variants; stream each record to LOG_FILE."""
    subset = df if dry_run is None else df.head(dry_run)
    results: list[dict] = []

    with open(LOG_FILE, "w") as fh:
        for i, row in enumerate(subset.itertuples(index=False), start=1):
            user_msg = USER_TEMPLATE.format(**_fmt_row(row))
            print(f"[{i}/{len(subset)}] {row.variant}…", end=" ", flush=True)

            raw, stop_reason = call_llm(client, user_msg)
            answer = parse_answer(raw)

            if stop_reason == "max_tokens" and "parse_error" in answer:
                answer["parse_error"] = "truncated"

            def _safe(x):
                return None if pd.isna(x) else x

            llm_classification = answer.get("classification")
            llm_binary = _to_binary(llm_classification)

            record: dict = {
                "variant": row.variant,
                "legacy_name": row.legacy_name,
                "domain": row.domain,
                "allele_frequency": _safe(row.allele_frequency),
                "am_pathogenicity": _safe(row.am_pathogenicity),
                "am_class": row.am_class,
                "determination_2026": row.determination_2026,
                "cadd_phred": _safe(row.cadd_phred),
                "polyphen_raw": row.polyphen_raw if not pd.isna(row.polyphen_raw) else None,
                "sift_raw": row.sift_raw if not pd.isna(row.sift_raw) else None,
                "stop_reason": stop_reason,
                "llm_raw": raw,
                "llm_answer": answer,
                "llm_classification": llm_classification,
                "llm_binary": llm_binary,
                "parse_error": "parse_error" in answer,
            }
            fh.write(json.dumps(record) + "\n")
            fh.flush()

            llm_pred = llm_binary or "PARSE_ERROR"
            match = "✓" if _norm(llm_pred) == _norm(row.determination_2026) else "✗"
            print(f"{llm_pred} (truth: {row.determination_2026}) {match}")
            results.append(record)

    return results


# ── set analysis ──────────────────────────────────────────────────────────────

def _norm(label: str | None) -> str | None:
    """Canonical form for label comparison: lowercase, drop hyphens and spaces.

    'CF-causing', 'CF causing', 'cf-causing' → 'cfcausing'
    'Non-CF-causing', 'Non CF-causing'       → 'noncfcausing'
    """
    if label is None:
        return None
    return re.sub(r"[-\s]", "", label).lower()


def jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity coefficient between two sets."""
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def set_analysis(results: list[dict]) -> dict:
    """Compute |A|, |B|, |A∩B|, Jaccard, and 2 named examples per direction."""
    truth: dict[str, str] = {r["variant"]: r["determination_2026"] for r in results}

    am_pred: dict[str, str] = {}
    llm_pred: dict[str, str | None] = {}

    for r in results:
        v = r["variant"]
        am_score = r["am_pathogenicity"] or 0.0
        am_pred[v] = "CF-causing" if am_score >= AM_THRESHOLD else "Non-CF-causing"
        lp = r.get("llm_binary")
        llm_pred[v] = lp if _norm(lp) in ("cfcausing", "noncfcausing") else None

    set_a = {v for v, p in am_pred.items() if _norm(p) != _norm(truth[v])}
    set_b = {v for v, p in llm_pred.items() if p is not None and _norm(p) != _norm(truth[v])}

    def _detail(variant: str) -> dict:
        rec = next((r for r in results if r["variant"] == variant), {})
        return {
            "variant": variant,
            "truth": truth[variant],
            "am_pred": am_pred.get(variant),
            "llm_pred": llm_pred.get(variant),
            "llm_tier": rec.get("llm_tier"),
            "criteria": rec.get("llm_answer", {}).get("criteria"),
        }

    a_not_b = sorted(set_a - set_b)
    b_not_a = sorted(set_b - set_a)

    n_parse_failures = sum(1 for r in results if r.get("parse_error"))
    n_truncations = sum(1 for r in results if r.get("stop_reason") == "max_tokens")

    return {
        "n_variants": len(results),
        "n_parse_failures": n_parse_failures,
        "n_truncations": n_truncations,
        "n_scored": len(results) - n_parse_failures,
        "n_set_a_am_failures": len(set_a),
        "n_set_b_llm_failures": len(set_b),
        "n_intersection": len(set_a & set_b),
        "jaccard_ab": round(jaccard(set_a, set_b), 4),
        "named_a_not_b": [_detail(v) for v in a_not_b[:2]],
        "named_b_not_a": [_detail(v) for v in b_not_a[:2]],
    }


# ── consistency check ─────────────────────────────────────────────────────────

def run_consistency_check(
    df: pd.DataFrame,
    client: anthropic.Anthropic,
    n: int = 20,
    seed: int = 42,
) -> dict:
    """Re-run n random variants with paraphrased prompt; report agreement rate."""
    original_log: dict[str, str | None] = {}
    if LOG_FILE.exists():
        with open(LOG_FILE) as fh:
            for line in fh:
                rec = json.loads(line)
                original_log[rec["variant"]] = rec.get("llm_binary")

    sample = df.sample(min(n, len(df)), random_state=seed)
    agreements = 0
    checked = 0
    detail: list[dict] = []

    for row in sample.itertuples(index=False):
        original_pred = original_log.get(row.variant)
        if original_pred is None:
            continue

        user_msg = PARAPHRASED_USER_TEMPLATE.format(**_fmt_row(row))
        print(f"  Consistency {row.variant}…", end=" ", flush=True)

        raw, _ = call_llm(client, user_msg)
        answer = parse_answer(raw)
        new_pred = _to_binary(answer.get("classification"))
        agree = _norm(new_pred) == _norm(original_pred)

        if agree:
            agreements += 1
        checked += 1

        print(f"orig={original_pred} rephrased={new_pred} {'✓' if agree else '✗'}")
        detail.append({
            "variant": row.variant,
            "original_pred": original_pred,
            "rephrased_pred": new_pred,
            "agree": agree,
        })

    return {
        "n_checked": checked,
        "n_agree": agreements,
        "agreement_rate": round(agreements / checked, 4) if checked else None,
        "detail": detail,
    }


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """Run the ACMG-LLM orthogonality experiment end to end."""
    parser = argparse.ArgumentParser(
        description="ACMG-LLM Orthogonality Experiment (292 CFTR2 variants)"
    )
    parser.add_argument(
        "--dry-run", type=int, default=None, metavar="N",
        help="Process only the first N variants (for smoke-testing)"
    )
    parser.add_argument(
        "--skip-consistency", action="store_true",
        help="Skip the 20-variant consistency check"
    )
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "ANTHROPIC_API_KEY not found.\n"
            "Add it to your .env file and retry."
        )

    client = anthropic.Anthropic(api_key=api_key)

    print("Loading data…")
    df = load_data()
    print(f"  {len(df)} labelled variants ready.\n")

    print(f"Running LLM classification ({MODEL}, temperature={TEMPERATURE})…")
    if args.dry_run:
        print(f"  DRY RUN: processing first {args.dry_run} variants only.")
    results = run_experiment(df, client, args.dry_run)
    print(f"\nLog written → {LOG_FILE}")

    print("\nRunning set analysis…")
    analysis = set_analysis(results)

    consistency: dict | None = None
    if not args.skip_consistency and args.dry_run is None:
        print("\nRunning consistency check (20 random variants, paraphrased prompt)…")
        consistency = run_consistency_check(df, client)
    elif args.skip_consistency:
        print("\nConsistency check skipped (--skip-consistency).")
    else:
        print("\nConsistency check skipped (dry-run mode).")

    summary = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "am_threshold": AM_THRESHOLD,
        "set_analysis": analysis,
        "consistency_check": consistency,
    }

    with open(SUMMARY_FILE, "w") as fh:
        json.dump(summary, fh, indent=2)

    # ── print report ─────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 60}")
    a = analysis
    print(f"  Variants evaluated : {a['n_variants']}")
    print(f"  Parse failures     : {a['n_parse_failures']}  (excluded from Set B)")
    print(f"    of which truncated: {a['n_truncations']}")
    print(f"  Variants scored    : {a['n_scored']}")
    print(f"  |A| AM failures    : {a['n_set_a_am_failures']}")
    print(f"  |B| LLM failures   : {a['n_set_b_llm_failures']}")
    print(f"  |A ∩ B|            : {a['n_intersection']}")
    print(f"  Jaccard(A, B)      : {a['jaccard_ab']}")
    if consistency:
        rate = consistency["agreement_rate"]
        n = consistency["n_checked"]
        print(f"  Consistency (n={n}) : {rate:.1%}")

    print(f"\n  A \\ B — AM fails, LLM correct (orthogonal direction 1):")
    for ex in a["named_a_not_b"]:
        print(f"    {ex['variant']:20s}  truth={ex['truth']}  AM={ex['am_pred']}  LLM={ex['llm_pred']}")
        if ex.get("criteria"):
            applied = [k for k, v in ex["criteria"].items() if v == "met" or str(v).startswith("met_")]
            print(f"      criteria applied: {applied}")

    print(f"\n  B \\ A — LLM fails, AM correct (orthogonal direction 2):")
    for ex in a["named_b_not_a"]:
        print(f"    {ex['variant']:20s}  truth={ex['truth']}  AM={ex['am_pred']}  LLM={ex['llm_pred']}")
        if ex.get("criteria"):
            applied = [k for k, v in ex["criteria"].items() if v == "met" or str(v).startswith("met_")]
            print(f"      criteria applied: {applied}")

    print(f"\nFull summary → {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
