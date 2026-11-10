"""Sentence-transformer semantic search with transparent lexical fallback."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticSearch:
    def __init__(self,use_embeddings=False):
        self.use_embeddings=use_embeddings;self.df=None;self.method='not indexed'
    def fit(self,df):
        self.df=df.reset_index(drop=True).copy()
        if self.use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self.encoder=SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
                self.vectors=self.encoder.encode(self.df.text.tolist(),normalize_embeddings=True)
                self.method='multilingual sentence embeddings'
                return self
            except (ImportError,OSError,RuntimeError) as exc:
                self.embedding_failure=str(exc)
        self.vectorizer=TfidfVectorizer(stop_words='english',ngram_range=(1,2),max_features=14000)
        self.vectors=self.vectorizer.fit_transform(self.df.text)
        self.method='TF IDF lexical fallback (NOT semantic or cross-lingual)'
        return self
    def search(self,query,top_k=5,category=None,sentiment=None):
        if self.df is None:raise RuntimeError('Search index is not ready')
        if self.method=='multilingual sentence embeddings':
            q=self.encoder.encode([query],normalize_embeddings=True)
            similarity=np.asarray(q @ self.vectors.T)[0]
        else:
            similarity=cosine_similarity(self.vectorizer.transform([query]),self.vectors)[0]
        candidates=[]
        for idx in np.argsort(similarity)[::-1]:
            record=self.df.iloc[int(idx)]
            if category and str(record.category).lower()!=str(category).lower():continue
            candidates.append({'article_id':str(record.article_id), 'category':str(record.category),
                'score':round(float(similarity[idx]),4), 'snippet':str(record.text)[:250],
                'source':None if str(record.source)=='<NA>' else str(record.source),
                'date':None if str(record.date)=='NaT' else str(record.date)})
            if len(candidates)>=top_k:break
        return {'method':self.method,'results':candidates}
