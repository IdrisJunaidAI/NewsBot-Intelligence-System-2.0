"""Independent research runner. Requires licensed local data; never exports article bodies.
CSV documents: id,text,language,published_at,source
CSV queries: query_id,query,language,relevant_id
CSV summaries: id,reference (human authored)
CSV fewshot: text,label,split (support or test)
All input files must be reviewed for rights and independent labels.
"""
import argparse, json, hashlib, time
from pathlib import Path
import numpy as np
import pandas as pd

def read(path, columns):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    if not set(columns).issubset(df.columns) or df.empty:
        raise ValueError(f"{path}: missing columns or empty dataset")
    if (df[columns].apply(lambda c: c.str.strip().eq(""))).any().any():
        raise ValueError(f"{path}: blank required value")
    return df

def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def retrieval(docs, queries):
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    if docs.id.duplicated().any() or queries.query_id.duplicated().any():
        raise ValueError("IDs must be unique")
    if not set(queries.relevant_id).issubset(docs.id):
        raise ValueError("Unknown relevance ID")
    if not set(["en","es","fr"]).issubset(queries.language):
        raise ValueError("Need English, Spanish and French queries")
    texts=docs.text.tolist()
    q=queries["query"].tolist()
    v=TfidfVectorizer(ngram_range=(1,2))
    lex=cosine_similarity(v.fit_transform(texts),v.transform(q)).T
    model=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    sem=model.encode(q,normalize_embeddings=True) @ model.encode(texts,normalize_embeddings=True).T
    rows=[]
    for method,scores in [("TFIDF",lex),("MiniLM",sem)]:
        for i,row in enumerate(queries.itertuples()):
            order=np.argsort(-scores[i],kind="stable")
            rank=next(j+1 for j,k in enumerate(order) if docs.id.iloc[k]==row.relevant_id)
            rows.append(dict(method=method,language=row.language,query_id=row.query_id,rank=rank,r1=int(rank==1),r3=int(rank<=3),rr=1/rank))
    return pd.DataFrame(rows)

def summarization(docs, refs):
    from transformers import pipeline
    from rouge_score import rouge_scorer
    if refs.id.duplicated().any() or not set(refs.id).issubset(docs.id):
        raise ValueError("Invalid reference IDs")
    model=pipeline("summarization",model="sshleifer/distilbart-cnn-12-6",device=-1)
    scorer=rouge_scorer.RougeScorer(["rouge1","rouge2","rougeL"],use_stemmer=True)
    rows=[]
    for r in refs.itertuples():
        text=docs.set_index("id").loc[r.id,"text"]
        if docs.set_index("id").loc[r.id,"language"]!="en":
            raise ValueError("DistilBART experiment requires English documents")
        # Truncation is explicit; human references should cover the same source window.
        ids=model.tokenizer(text, truncation=True,max_length=896)["input_ids"]
        source=model.tokenizer.decode(ids,skip_special_tokens=True)
        if len(ids)<24:
            raise ValueError("Summary source too short")
        generated=model(source,max_new_tokens=96,min_new_tokens=8,do_sample=False,truncation=True)[0]["summary_text"]
        import re
        baseline=" ".join(re.split(r"(?<=[.!?])\s+",source)[:2])
        for method,pred in [("lead2",baseline),("DistilBART",generated)]:
            scores=scorer.score(r.reference,pred)
            rows.append(dict(id=r.id,method=method,**{k:v.fmeasure for k,v in scores.items()}))
    return pd.DataFrame(rows)

def temporal(docs):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import NMF
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    d=docs[docs.language=="en"].copy()
    d["month"]=pd.to_datetime(d.published_at,utc=True,errors="raise").dt.strftime("%Y-%m")
    if len(d)<10 or d.month.nunique()<2:
        raise ValueError("Need at least ten English documents across multiple months")
    v=TfidfVectorizer(stop_words="english",min_df=2)
    x=v.fit_transform(d.text)
    k=min(5,x.shape[0],x.shape[1])
    model=NMF(n_components=k,random_state=42,max_iter=500)
    d["topic"]=model.fit_transform(x).argmax(axis=1)
    analyzer=SentimentIntensityAnalyzer()
    d["tone"]=d.text.map(lambda t:analyzer.polarity_scores(t)["compound"])
    counts=d.groupby(["month","topic"]).agg(count=("id","size"),mean_tone=("tone","mean")).reset_index()
    counts["monthly_share"]=counts["count"]/counts.groupby("month")["count"].transform("sum")
    return counts

def fewshot(data):
    from transformers import pipeline
    from sklearn.metrics import accuracy_score,f1_score
    if set(data.split)!={"support","test"} or data.text.duplicated().any():
        raise ValueError("Need distinct support and test texts")
    support=data[data.split=="support"]; test=data[data.split=="test"]
    labels=sorted(support.label.unique())
    if len(labels)<2 or not set(test.label).issubset(labels):
        raise ValueError("Need at least two known labels")
    if support.groupby("label").size().min()<2:
        raise ValueError("Need at least two support examples per label")
    model=pipeline("text2text-generation",model="google/flan-t5-base",device=-1)
    rows=[]
    for shots in [0,1,2]:
        examples=support.groupby("label",sort=True).head(shots)
        prefix="Classify the news text. Answer only with one label: "+", ".join(labels)+".\n"
        for e in examples.itertuples():
            prefix+=f"Text: {e.text[:240]}\nLabel: {e.label}\n"
        predictions=[]
        for e in test.itertuples():
            prompt=prefix+f"Text: {e.text[:500]}\nLabel:"
            if len(model.tokenizer(prompt)["input_ids"])>512:
                raise ValueError("Prompt exceeds context budget; shorten examples")
            prediction=model(prompt,max_new_tokens=12,do_sample=False)[0]["generated_text"].strip().lower()
            predictions.append(prediction if prediction in labels else "__invalid__")
        rows.append(dict(shots_per_label=shots,n=len(test),accuracy=accuracy_score(test.label,predictions),macro_f1=f1_score(test.label,predictions,labels=labels,average="macro",zero_division=0),invalid=sum(p=="__invalid__" for p in predictions)))
    return pd.DataFrame(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["retrieval","summary","temporal","fewshot"])
    p.add_argument("--documents")
    p.add_argument("--queries")
    p.add_argument("--references")
    p.add_argument("--fewshot-data")
    p.add_argument("--output",required=True)
    p.add_argument("--acknowledge-data-rights",action="store_true")
    args=p.parse_args()
    if not args.acknowledge_data_rights:
        p.error("Confirm permission for local use and independent annotations")
    start=time.time()
    files=[]
    if args.mode=="fewshot":
        files=[args.fewshot_data]
        result=fewshot(read(files[0],["text","label","split"]))
    else:
        files=[args.documents]
        docs=read(files[0],["id","text","language","published_at","source"])
        if docs.id.duplicated().any() or docs.text.duplicated().any():
            raise ValueError("Duplicate documents")
        if args.mode=="retrieval":
            files.append(args.queries)
            result=retrieval(docs,read(files[1],["query_id","query","language","relevant_id"]))
        elif args.mode=="summary":
            files.append(args.references)
            result=summarization(docs,read(files[1],["id","reference"]))
        else:
            result=temporal(docs)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/(args.mode+".csv"),index=False)
    manifest={"mode":args.mode,"input_sha256":[fingerprint(f) for f in files],"rows":len(result),"elapsed_seconds":time.time()-start,"status":"executed","limitations":"Input provenance and annotations require human review. No claims of external validity."}
    (out/(args.mode+"_manifest.json")).write_text(json.dumps(manifest,indent=2))
    print(result.to_string(index=False))

if __name__=="__main__":
    main()
