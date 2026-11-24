"""Bounded batch article NLP analysis for the optional Flask web application."""
MAX_BATCH_ARTICLES = 5
MAX_ARTICLE_CHARACTERS = 5000
MAX_TOTAL_CHARACTERS = 15000


def analyze_articles(system, articles):
    """Analyze 2..5 independently supplied excerpts without storing raw inputs.

    All input is validated before invoking the model. The returned summaries may
    contain source sentences from the user input; the originals are not persisted.
    """
    if not isinstance(articles, list) or not 2 <= len(articles) <= MAX_BATCH_ARTICLES:
        raise ValueError("Provide 2 to 5 article excerpts in a JSON list")
    if any(not isinstance(text, str) for text in articles):
        raise ValueError("All article excerpts must be text")
    normalized = [text.strip() for text in articles]
    if any(len(text) < 30 or len(text) > MAX_ARTICLE_CHARACTERS for text in normalized):
        raise ValueError("Each article must have between 30 and 5000 characters")
    if sum(map(len, normalized)) > MAX_TOTAL_CHARACTERS:
        raise ValueError("Total article text must not exceed 15000 characters")
    results = []
    for index, text in enumerate(normalized, start=1):
        analysis = system.analyze(text)
        category = analysis.get("classification") or {}
        sentiment = analysis.get("sentiment") or {}
        language = analysis.get("language") or {}
        summary = analysis.get("summary") or {}
        results.append({
            "article_number": index,
            "category": category.get("category"),
            "model_probability": category.get("model_probability"),
            "sentiment": sentiment.get("label"),
            "language": language.get("language"),
            "summary": str(summary.get("summary") or "")[:1500],
            "needs_human_review": bool(analysis.get("needs_human_review")),
            "language_limitation": analysis.get("language_limitation"),
            "classifier_source": analysis.get("model_source"),
        })
    return {
        "processed": len(results),
        "results": results,
        "disclaimer": (
            "BBC-trained classification is intended for English. Topic search uses "
            "a separate synthetic collection. Probabilities are not calibrated certainty. "
            "Submitted excerpts are not stored by the application."
        ),
        "source": "User submitted text, classified with the configured model",
    }
