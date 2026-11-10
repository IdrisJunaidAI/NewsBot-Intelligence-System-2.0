"""Feature extraction helpers for lexical news modeling."""
from sklearn.feature_extraction.text import TfidfVectorizer

def make_tfidf(max_features=12000):
    return TfidfVectorizer(stop_words='english',ngram_range=(1,2),max_features=max_features,sublinear_tf=True)
