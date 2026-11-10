"""Latent Dirichlet Allocation and nonnegative matrix factorization."""
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
import numpy as np

class TopicModeler:
    def __init__(self,n_topics=5,seed=42):
        self.n_topics=n_topics;self.seed=seed;self.models={};self.vectorizers={};self.features={}
    def fit(self,texts):
        docs=list(texts)
        if len(docs)<4:raise ValueError('At least four documents required for topic modeling')
        n=min(self.n_topics,len(docs)-1)
        for name,vectorizer,model in [
             ('LDA',CountVectorizer(stop_words='english',max_features=4000,min_df=1),LatentDirichletAllocation(n_components=n,random_state=self.seed,max_iter=12)),
             ('NMF',TfidfVectorizer(stop_words='english',max_features=4000,min_df=1),NMF(n_components=n,init='nndsvda',random_state=self.seed,max_iter=400))]:
            x=vectorizer.fit_transform(docs)
            if min(x.shape)<n:raise ValueError('Topic count exceeds corpus vocabulary or document count')
            self.features[name]=model.fit_transform(x)
            self.vectorizers[name]=vectorizer;self.models[name]=model
        return self
    def top_words(self,method='NMF',n_words=8):
        model=self.models[method];vocab=self.vectorizers[method].get_feature_names_out()
        return [{'topic':i,'words':list(vocab[np.argsort(comp)[-n_words:][::-1]])} for i,comp in enumerate(model.components_)]
    def topics_for(self,text,method='NMF'):
        v=self.vectorizers[method].transform([text]);w=self.models[method].transform(v)[0]
        return [{'topic':int(i),'weight':round(float(w[i]),4)} for i in np.argsort(w)[::-1][:3]]
    def topic_evolution(self,df,method='NMF'):
        """Trends require real article dates; undated BBC records are not suitable."""
        if df.date.notna().sum()<6:return {'available':False,'reason':'Insufficient publication dates; no trend claims made'}
        weights=self.models[method].transform(self.vectorizers[method].transform(df.text))
        tmp=df[['date']].copy();tmp['period']=tmp.date.dt.strftime('%Y-%m')
        tmp['topic']=weights.argmax(axis=1)
        grouped=tmp.dropna(subset=['period']).groupby(['period','topic']).size().reset_index(name='articles')
        return {'available':True,'counts':grouped.to_dict('records'),'note':'Article counts, not population-wide trends'}
