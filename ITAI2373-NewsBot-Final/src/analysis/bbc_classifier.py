"""Portable BBC classifier from transparent, non-executable model weights.

The JSON.GZ contains TF IDF vocabulary/IDF and linear classifier coefficients,
but NO raw BBC article texts, and does not execute arbitrary Python objects.
An official BBC Kaggle test ground truth was NOT supplied; validation metrics
refer solely to an isolated labeled BBC Train 80/20 holdout.
"""
import gzip
import json
from pathlib import Path

import numpy as np
from scipy.special import softmax
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize


class BBCWeightedClassifier:
    """Predict categories using a released TF IDF Logistic Regression weight table."""

    def __init__(self, file_path):
        path = Path(file_path)
        with gzip.open(path, 'rt', encoding='utf-8') as handle:
            data = json.load(handle)
        if data.get('format') != 'newsbot-safe-tfidf-linear-v1':
            raise ValueError('Unsupported BBC classifier weights format')
        tfidf = data['tfidf']
        terms = tfidf['tokens']
        if not terms or len(terms) != len(tfidf['idf']) or len(set(terms)) != len(terms):
            raise ValueError('Malformed TF IDF vocabulary')
        if tfidf['ngram_range'] != [1, 2] or not tfidf['sublinear_tf']:
            raise ValueError('Unsupported TF IDF transformer settings')
        self.vectorizer = CountVectorizer(
            vocabulary={token: i for i, token in enumerate(terms)},
            ngram_range=(1, 2), stop_words='english', dtype=np.float64)
        self.idf = np.asarray(tfidf['idf'], dtype=np.float64)
        params = data['logistic_regression']
        self.classes_ = np.asarray(params['classes'], dtype=str)
        self.coef = np.asarray(params['coef'], dtype=np.float64)
        self.intercept = np.asarray(params['intercept'], dtype=np.float64)
        if self.coef.shape != (len(self.classes_), len(terms)) or self.intercept.shape != (len(self.classes_),):
            raise ValueError('Malformed classifier weight dimensions')
        self.provenance = data['provenance']

    def _features(self, texts):
        features = self.vectorizer.transform(texts)
        features.data = 1.0 + np.log(features.data)
        features.data *= self.idf[features.indices]
        return normalize(features, norm='l2', copy=False)

    def predict_proba(self, texts):
        features = self._features(texts)
        return softmax(features @ self.coef.T + self.intercept, axis=1)

    def predict(self, text):
        """NewsBotSystem-compatible prediction object for a single article."""
        if not isinstance(text, str) or len(text.strip()) < 30:
            raise ValueError('Please enter an article of at least 30 characters')
        probs = self.predict_proba([text])[0]
        idx = int(np.argmax(probs))
        return {
            'category': str(self.classes_[idx]),
            'model_probability': float(probs[idx]),
            'probabilities': {str(c): round(float(p), 4) for c, p in zip(self.classes_, probs)},
            'model': 'BBC news TF IDF Logistic Regression',
            'source': 'BBC News Train.csv: 1440 unique labeled articles',
            'note': 'Probabilities are uncalibrated. Historical BBC training articles, not real-time news.'
        }
