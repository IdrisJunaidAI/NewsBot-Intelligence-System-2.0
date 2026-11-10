"""Transparent rule-based intent routing; vocabulary can be audited and extended."""
import re

def recognize_intent(query):
    q=query.lower()
    if re.search(r'\b(summarize|summary|brief|tl;dr)\b',q):return 'summarize'
    if re.search(r'\b(topic|trends?|themes?)\b',q):return 'topics'
    if re.search(r'\b(sentiment|positive|negative|neutral|tone)\b',q):return 'sentiment_filter'
    if re.search(r'\b(how many|count|number of)\b',q):return 'count'
    return 'search'
