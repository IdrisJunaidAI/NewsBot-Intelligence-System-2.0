"""Task-specific text normalization preserving original text for linguistic analysis."""
import html
import re

def clean_text(text):
    """Normalize markup, preserve negation, numbers, names and sentence punctuation."""
    if not isinstance(text,str):
        raise TypeError('Text must be a string')
    text = html.unescape(text)
    text = re.sub(r'<[^>]*>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def modeling_text(text):
    """Light cleaning; TF IDF vectorizer handles its own tokenization and case."""
    return clean_text(text)
