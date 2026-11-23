"""Three traceable retrieval methods: lexical TF IDF, LSA, or multilingual vectors.

LSA is classic latent semantic indexing, NOT a multilingual transformer.
Only the optional sentence encoder provides shared-vector cross-language search.
"""
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

MODEL_ID = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'


class SemanticSearch:
    def __init__(self, use_embeddings=False, encoder=None):
        self.use_embeddings = use_embeddings
        self.encoder = encoder
        self.df = None
        self.method = 'not indexed'
        self.lsa_available = False
        self.embedding_failure = None

    def fit(self, df):
        self.df = df.reset_index(drop=True).copy()
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=14000)
        self.lexical_vectors = self.vectorizer.fit_transform(self.df.text)
        self.lsa_available = False
        n = min(32, self.lexical_vectors.shape[0]-1, self.lexical_vectors.shape[1]-1)
        if n >= 2:
            self.reducer = TruncatedSVD(n_components=n, random_state=42)
            self.lsa_vectors = normalize(self.reducer.fit_transform(self.lexical_vectors))
            self.lsa_available = True
        self.method = 'LSA latent semantic indexing (TF IDF + truncated SVD), not multilingual embeddings' if self.lsa_available else 'TF IDF lexical fallback (NOT semantic or cross-lingual)'
        if self.use_embeddings:
            try:
                if self.encoder is None:
                    from sentence_transformers import SentenceTransformer
                    self.encoder = SentenceTransformer(MODEL_ID)
                vectors = np.asarray(self.encoder.encode(self.df.text.tolist(), normalize_embeddings=True), dtype=float)
                if vectors.shape[0] != len(self.df) or vectors.ndim != 2:
                    raise ValueError('Embedding encoder returned the wrong matrix shape')
                self.dense_vectors = normalize(vectors)
                self.method = 'multilingual sentence embeddings'
            except (ImportError, OSError, RuntimeError, ValueError) as exc:
                self.embedding_failure = type(exc).__name__
                self.encoder = None
        return self

    def search(self, query, top_k=5, category=None, sentiment=None, mode='auto'):
        if self.df is None:
            raise RuntimeError('Search index is not ready')
        if not isinstance(query, str) or not query.strip():
            raise ValueError('A nonempty search query is required')
        if not isinstance(top_k, int) or not 1 <= top_k <= 100:
            raise ValueError('top_k must be between 1 and 100')
        if mode not in ('auto', 'lexical', 'lsa', 'semantic'):
            raise ValueError('Search mode must be auto, lexical, lsa or semantic')
        selected = ('semantic' if self.method == 'multilingual sentence embeddings' else
                    ('lsa' if self.lsa_available else 'lexical')) if mode == 'auto' else mode
        if selected == 'semantic':
            if self.method != 'multilingual sentence embeddings':
                raise RuntimeError('Multilingual sentence encoder is not active')
            q = np.asarray(self.encoder.encode([query], normalize_embeddings=True), dtype=float)
            if q.ndim != 2 or q.shape[0] != 1:
                raise RuntimeError('Embedding query shape mismatch')
            similarities = cosine_similarity(normalize(q), self.dense_vectors)[0]
            name = 'multilingual sentence embeddings'
            threshold = 0.25
        else:
            lexical_query = self.vectorizer.transform([query])
            if lexical_query.nnz == 0:
                return {'method': 'LSA latent semantic indexing' if selected == 'lsa' else 'TF IDF lexical retrieval',
                        'results': [], 'note': 'No known query terms in the collection; no match is asserted'}
            if selected == 'lsa':
                if not self.lsa_available:
                    raise RuntimeError('LSA index is unavailable')
                embedded = normalize(self.reducer.transform(lexical_query))
                similarities = cosine_similarity(embedded, self.lsa_vectors)[0]
                name = 'LSA latent semantic indexing (TF IDF + truncated SVD)'
                threshold = 0.20
            else:
                similarities = cosine_similarity(lexical_query, self.lexical_vectors)[0]
                name = 'TF IDF lexical retrieval'
                threshold = 0.0
        candidates = []
        for idx in np.argsort(similarities)[::-1]:
            similarity = float(similarities[idx])
            if not np.isfinite(similarity) or similarity <= threshold:
                continue
            record = self.df.iloc[int(idx)]
            if category and str(record.category).lower() != str(category).lower():
                continue
            def safe(v):
                return None if pd.isna(v) else str(v)
            candidates.append({'article_id': str(record.article_id), 'category': str(record.category),
                               'score': round(similarity, 4), 'snippet': str(record.text)[:250],
                               'source': safe(record.source), 'date': safe(record.date),
                               'retrieval_method': name})
            if len(candidates) >= top_k:
                break
        return {'method': name, 'results': candidates,
                'note': 'Similarity ranks are exploratory and do not imply factual relevance or a live news source'}
