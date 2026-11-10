"""Simple reproducibility and output-quality helpers."""

def retrieval_precision_at_k(retrieved_ids,relevant_ids,k=5):
    """Evaluation against manually labeled relevance judgments."""
    if k<1:raise ValueError('k must be positive')
    return sum(str(x) in set(map(str,relevant_ids)) for x in retrieved_ids[:k])/k

def summarization_sentence_coverage(summary,article):
    """Extractive source grounding heuristic, not a summary quality metric."""
    from src.language_models.summarizer import split_sentences
    s=split_sentences(summary)
    return sum(t in article for t in s)/len(s) if s else 0.
