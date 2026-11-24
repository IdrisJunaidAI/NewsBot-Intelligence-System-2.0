"""Auditable few-shot/low-data experiment summary from committed measured CSV.

No model training or BBC article texts are served at request time. Values originate
in the historical BBC experiment, not from synthetic web demo examples.
"""
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

RESULTS_PATH = Path(__file__).resolve().parents[2] / "data" / "results" / "fewshot_learning_curve.csv"
EXPECTED_SIZES = (5, 10, 25, 50, 100)


def learning_curve_report(path=RESULTS_PATH):
    """Summarize five measured seeds at five sample sizes; fail closed if malformed."""
    groups = defaultdict(list)
    with Path(path).open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        required = {
            "per_class_samples", "total_training_samples", "seed",
            "holdout_macro_f1", "holdout_accuracy"
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Few-shot evidence CSV is missing expected columns")
        for row in reader:
            samples = int(row["per_class_samples"])
            total = int(row["total_training_samples"])
            seed = int(row["seed"])
            macro_f1 = float(row["holdout_macro_f1"])
            accuracy = float(row["holdout_accuracy"])
            if samples not in EXPECTED_SIZES or total != 5 * samples:
                raise ValueError("Unexpected experimental sample counts")
            if not all(math.isfinite(x) and 0 <= x <= 1 for x in (macro_f1, accuracy)):
                raise ValueError("Invalid measured evaluation score")
            groups[samples].append({"seed": seed, "macro_f1": macro_f1, "accuracy": accuracy})
    if set(groups) != set(EXPECTED_SIZES):
        raise ValueError("Incomplete training size experiment")
    points = []
    for samples in EXPECTED_SIZES:
        records = groups[samples]
        seeds = [r["seed"] for r in records]
        if len(records) != 5 or len(set(seeds)) != 5:
            raise ValueError("Expected five distinct runs per training size")
        f1 = [r["macro_f1"] for r in records]
        accuracy = [r["accuracy"] for r in records]
        points.append({
            "per_class_samples": samples,
            "total_training_samples": samples * 5,
            "repetitions": len(records),
            "mean_macro_f1": round(statistics.mean(f1), 6),
            "sd_macro_f1": round(statistics.stdev(f1), 6),
            "mean_accuracy": round(statistics.mean(accuracy), 6),
            "sd_accuracy": round(statistics.stdev(accuracy), 6),
            "seeds": sorted(seeds),
        })
    return {
        "available": True,
        "study": "Low-data supervised text classification learning curve",
        "source": "Authentic historical BBC News Train labeled articles",
        "data_file": "data/results/fewshot_learning_curve.csv",
        "research_type": "Controlled reduced-training-sample experiment, not LLM prompt-based few-shot",
        "categories": 5,
        "heldout_articles": 288,
        "fixed_split_seed": 42,
        "points": points,
        "total_model_fits": sum(x["repetitions"] for x in points),
        "methods": "For each sample size, five independently sampled labeled subsets from the fixed BBC training split; TF IDF + Logistic Regression; scores on the same fixed holdout",
        "limits": (
            "The heldout subset is repeatedly inspected across many study conditions; "
            "the study is exploratory and cannot establish out-of-distribution, "
            "multilingual, live-news or LLM few-shot performance. "
            "Standard deviations describe across-seed variability, not a population confidence interval."
        ),
        "original_article_text_published": False,
    }
