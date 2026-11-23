"""Run genuine transformer semantic evaluation on a small controlled synthetic corpus.

Uses online model download only with --download-model. Reports real numbers only
when executed; no shipped claims of accuracy are made before execution.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
DOCUMENTS = [
    ('robotics', 'Engineers designed autonomous robotics systems and machine learning algorithms for a factory.'),
    ('climate', 'Researchers documented climate change and renewable solar energy for coastal cities.'),
    ('finance', 'A financial institution reported quarterly profits, revenue growth and share prices.'),
    ('health', 'Doctors studied hospital treatments and vaccines to improve patient health.'),
    ('sport', 'A football club won the tournament after its final match against a rival team.'),
    ('cinema', 'An award winning movie director announced a new international film release.'),
]
QUERIES = [
    ('en','robotics','How are robots and machine learning used in a factory?'),
    ('es','robotics','¿Cómo se utilizan los robots y el aprendizaje automático en una fábrica?'),
    ('fr','robotics','Comment les robots et l’apprentissage automatique sont ils utilisés dans une usine ?'),
    ('en','climate','What do scientists say about renewable solar energy?'),
    ('es','climate','¿Qué dicen los científicos sobre la energía solar renovable?'),
    ('fr','climate','Que disent les scientifiques au sujet de l’énergie solaire renouvelable ?'),
    ('en','finance','What did the bank report about profits and revenues?'),
    ('es','finance','¿Qué informó el banco sobre sus beneficios e ingresos?'),
    ('fr','finance','Que rapporte la banque au sujet des bénéfices et des revenus ?'),
    ('en','health','Which hospital treatment improved patient health?'),
    ('es','health','¿Qué tratamientos hospitalarios mejoraron la salud de los pacientes?'),
    ('fr','health','Quels traitements hospitaliers améliorent la santé des patients ?'),
    ('en','sport','Which team won the football tournament final?'),
    ('es','sport','¿Qué equipo ganó la final del torneo de fútbol?'),
    ('fr','sport','Quelle équipe a remporté la finale du tournoi de football ?'),
    ('en','cinema','Which director announced the international film?'),
    ('es','cinema','¿Qué director anunció una película internacional?'),
    ('fr','cinema','Quel réalisateur a annoncé un nouveau film international ?'),
]


def evaluate(encoder):
    ids=[d[0] for d in DOCUMENTS]
    texts=[d[1] for d in DOCUMENTS]
    query_texts=[q[2] for q in QUERIES]
    tfidf=TfidfVectorizer(stop_words='english',ngram_range=(1,2))
    doc_terms=tfidf.fit_transform(texts)
    lexical=cosine_similarity(tfidf.transform(query_texts),doc_terms)
    vectors=np.asarray(encoder.encode(texts,normalize_embeddings=True),dtype=float)
    q_vectors=np.asarray(encoder.encode(query_texts,normalize_embeddings=True),dtype=float)
    semantic=cosine_similarity(q_vectors,vectors)
    records=[]
    for i,(language,correct,query) in enumerate(QUERIES):
        for name,matrix in [('TF IDF baseline',lexical),('multilingual MiniLM',semantic)]:
            ranking=np.argsort(matrix[i])[::-1]
            rank=next((j+1 for j,index in enumerate(ranking) if ids[index]==correct),None)
            records.append({'language':language,'method':name,'target_article':correct,
                            'query':query,'rank':rank,'recall_at_1':int(rank is not None and rank<=1),
                            'recall_at_3':int(rank is not None and rank<=3)})
    frame=pd.DataFrame(records)
    summary=frame.groupby(['method','language'],as_index=False)[['recall_at_1','recall_at_3']].mean()
    return frame,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--download-model',action='store_true',help='Explicitly authorize downloading the real pretrained multilingual encoder')
    p.add_argument('--output-dir',default='data/results')
    args=p.parse_args()
    if not args.download_model:
        p.error('Pass --download-model only when network/model download and compute are available')
    from sentence_transformers import SentenceTransformer
    encoder=SentenceTransformer(MODEL)
    rows,summary=evaluate(encoder)
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    rows.to_csv(out/'multilingual_query_retrieval_results.csv',index=False)
    summary.to_csv(out/'multilingual_retrieval_summary.csv',index=False)
    manifest={'model':MODEL,'dataset':'18 curated synthetic queries across en/es/fr and six synthetic English texts',
              'measured':True,'notes':'Not an external news relevance benchmark; handcrafted query labels may favor these examples',
              'results':summary.to_dict(orient='records')}
    (out/'multilingual_retrieval_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print(summary.to_string(index=False))


if __name__=='__main__':main()
