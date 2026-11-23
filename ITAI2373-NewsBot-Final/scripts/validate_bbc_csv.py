"""Audit an instructor-approved BBC News Train.csv without distributing its content.

Run this before training. The JSON report contains statistics and a SHA256
fingerprint, never the raw article texts. No network or API access required.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from src.data_processing.data_validator import load_news_csv

BBC_CATEGORIES = {"business", "entertainment", "politics", "sport", "technology"}


def audit_dataset(filename):
    path = Path(filename)
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")
    raw = pd.read_csv(path)
    cleaned = load_news_csv(path)
    category_counts = {str(k): int(v) for k, v in cleaned.category.value_counts().items()}
    found = set(category_counts)
    messages = []
    if not BBC_CATEGORIES.issubset(found):
        missing = sorted(BBC_CATEGORIES - found)
        messages.append(f"Expected BBC labels missing: {', '.join(missing)}")
    if not category_counts or min(category_counts.values()) < 4:
        messages.append("At least two classes and four articles per class are required for training")
    if len(cleaned) < len(raw):
        messages.append("Rows were excluded during cleaning or duplicate removal")
    data = {
        "input_name": path.name,
        "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "raw_rows": int(len(raw)),
        "retained_rows": int(len(cleaned)),
        "removed_rows": int(len(raw) - len(cleaned)),
        "category_counts": category_counts,
        "classes": sorted(found),
        "all_five_bbc_categories": BBC_CATEGORIES.issubset(found),
        "dated_articles": int(cleaned.date.notna().sum()),
        "source_metadata_count": int(cleaned.source.notna().sum()),
        "messages": messages,
        "note": "Dataset audit only. No model training or accuracy claims are made.",
    }
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", help="Path to an instructor-approved BBC News Train.csv")
    parser.add_argument("--output", default="data/results/bbc_preflight.json")
    args = parser.parse_args()
    report = audit_dataset(args.csv)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if len(report["classes"]) < 2 or min(report["category_counts"].values(), default=0) < 4:
        raise SystemExit("Dataset does not satisfy the minimum classification prerequisites")


if __name__ == "__main__":
    main()
