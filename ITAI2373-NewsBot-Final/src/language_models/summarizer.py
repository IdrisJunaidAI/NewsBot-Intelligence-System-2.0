"""Extractive summary selects original sentences, preventing invented source claims."""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def split_sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+',text.strip()) if len(s.strip())>=15]
class NewsSummarizer:
    def summarize(self,text,n_sentences=3):
        sentences=split_sentences(text)
        if not sentences:return {'summary':'','method':'extractive TF IDF','source_sentences':0}
        if len(sentences)<=n_sentences:
            chosen=sentences
        else:
            matrix=TfidfVectorizer(stop_words='english').fit_transform(sentences)
            similarities=cosine_similarity(matrix)
            scores=similarities.sum(axis=1)
            chosen=[sentences[i] for i in sorted(np.argsort(scores)[-n_sentences:])]
        return {'summary':' '.join(chosen),'method':'extractive TF IDF sentence centrality',
                'source_sentences':len(sentences),'note':'Extracted from supplied article; does not independently verify claims'}
