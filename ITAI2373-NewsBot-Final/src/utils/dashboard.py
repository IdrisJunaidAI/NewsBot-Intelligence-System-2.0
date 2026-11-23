"""Aggregate, provenance-aware analytics for the NewsBot UI and report export.

These are summaries of the *loaded corpus*, not measurements of world news.
Never invent dates, publishers, or classification performance.
"""
from collections import Counter
import numpy as np
import pandas as pd


def _distribution(values, total):
    counts = Counter(str(v) for v in values)
    return [
        {"label": label, "count": int(count), "percentage": round(100 * count / max(total, 1), 1)}
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _topics(system, method):
    features = system.topics.features.get(method)
    if features is None:
        return []
    labels = np.asarray(features).argmax(axis=1).tolist()
    counts = Counter(int(i) for i in labels)
    words = system.topics.top_words(method, 6)
    return [
        {
            "id": int(topic["topic"]),
            "keywords": [str(word) for word in topic["words"]],
            "articles": int(counts.get(int(topic["topic"]), 0)),
        }
        for topic in words
    ]


def dashboard_snapshot(system):
    """Produce JSON-safe metrics from the fitted NewsBotSystem instance.

    Use with a per-model cache in the web application because sentiment
    evaluation across a full corpus is expensive on each request.
    """
    df = system.df
    if df is None or df.empty:
        raise RuntimeError("NewsBot corpus is not initialized")

    size = int(len(df))
    synthetic = "SYNTHETIC" in str(system.source).upper()
    categories = _distribution(df.category.tolist(), size)
    sentiments = _distribution((system.sentiment.analyze(t)["label"] for t in df.text), size)

    dated = df.loc[df.date.notna(), "date"]
    periods = dated.dt.strftime("%Y-%m").tolist() if len(dated) else []
    timeline = [
        {"period": period, "articles": int(count)}
        for period, count in sorted(Counter(periods).items())
    ]

    metrics = system.classifier.metrics or {}
    comparisons = [
        {
            "model": str(item["model"]),
            "cv_macro_f1": round(float(item["cv_macro_f1"]), 4),
            "cv_accuracy": round(float(item["cv_accuracy"]), 4),
        }
        for item in metrics.get("cv_comparison", [])
    ]
    return {
        "meta": {
            "corpus": "Synthetic demonstration" if synthetic else "User supplied training corpus",
            "source": str(system.source),
            "synthetic": synthetic,
            "articles": size,
            "category_count": len(categories),
            "dated_articles": len(periods),
            "source_coverage": int(df.source.notna().sum()) if "source" in df else 0,
            "search_method": str(system.search.method),
            "has_live_news": False,
            "disclaimer": (
                "All displayed values come from a synthetic teaching dataset. "
                "They do not measure real BBC news accuracy or current events."
                if synthetic else
                "Results summarize only the loaded file. This is not a live news feed. "
                "Model estimates require independent verification."
            ),
        },
        "categories": categories,
        "sentiments": sentiments,
        "topics": {
            "LDA": _topics(system, "LDA"),
            "NMF": _topics(system, "NMF"),
        },
        "timeline": timeline,
        "evaluation": {
            "model": "Logistic Regression with TF IDF",
            "holdout_accuracy": (round(float(metrics["logistic_heldout_accuracy"]), 4)
                                 if "logistic_heldout_accuracy" in metrics else None),
            "holdout_macro_f1": (round(float(metrics["logistic_heldout_macro_f1"]), 4)
                                 if "logistic_heldout_macro_f1" in metrics else None),
            "holdout_count": int(metrics.get("holdout_n", 0)),
            "source": str(metrics.get("source", system.source)),
            "cross_validation": comparisons,
            "interpretation": (
                "Teaching data only; these scores must not be presented as real BBC model performance."
                if synthetic else
                "Internal held out estimates on the provided dataset; not external validation."
            ),
        },
        "chart_notes": {
            "categories": "Number of records by stored news label",
            "sentiments": "VADER text tone on loaded articles, not verified public sentiment",
            "topics": "Each article is assigned to its strongest statistical topic; labels are model keywords",
            "timeline": "Recorded article dates, not publishing frequency for the entire news ecosystem",
        },
    }
