"""Create publishable aggregate statistics without raw article text."""
from pathlib import Path
import hashlib,json,re,collections,argparse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.decomposition import NMF,LatentDirichletAllocation
from textblob import TextBlob
ROOT=Path(__file__).resolve().parents[1]
cli=argparse.ArgumentParser(description='Export no-text authentic BBC historical analytics')
cli.add_argument('--csv',required=True,help='Local instructor approved BBC News Train.csv')
cli.add_argument('--evaluation',default=str(ROOT/'data/results/bbc_evaluation.json'))
cli.add_argument('--out',default=str(ROOT/'data/results/bbc_public_analytics.json'))
args=cli.parse_args()
SOURCE=Path(args.csv)
DEST=Path(args.out)
EVAL=Path(args.evaluation)
df=pd.read_csv(SOURCE)
df['cleaned']=df['Text'].astype(str).str.replace(r'\s+',' ',regex=True).str.strip()
df['Category']=df.Category.astype(str).str.lower().str.strip().replace({'tech':'technology'})
df=df[df.cleaned.str.len()>=30].drop_duplicates(subset=['cleaned']).reset_index(drop=True)
cat=df.Category.value_counts()
# TextBlob is the available deterministic offline reference sentiment engine;
# do not relabel this as the VADER output of the separate web demo.
labels=[]
for t in df.cleaned:
 p=TextBlob(t).sentiment.polarity
 labels.append('positive' if p>0.10 else ('negative' if p < -0.10 else 'neutral'))
sent=collections.Counter(labels)
cat_sent={str(category):dict(collections.Counter(pd.Series(labels)[df.Category.eq(category)].tolist())) for category in cat.index}
texts=df.cleaned.tolist()
tfidf=TfidfVectorizer(stop_words='english',max_features=3500,min_df=3,max_df=.93,ngram_range=(1,2))
X=tfidf.fit_transform(texts)
# NMF trained on TFIDF representation
nmf=NMF(n_components=5,random_state=42,init='nndsvda',max_iter=280)
Z=nmf.fit_transform(X)
cv=CountVectorizer(stop_words='english',max_features=2000,min_df=3,max_df=.93)
count=cv.fit_transform(texts)
lda=LatentDirichletAllocation(n_components=5,random_state=42,learning_method='batch',max_iter=8, n_jobs=1)
L=lda.fit_transform(count)
def topics(weights,components,names):
 labels=np.argmax(weights,axis=1)
 c=collections.Counter(labels)
 out=[]
 for i,comp in enumerate(components):
  tokens=[str(names[j]) for j in np.argsort(comp)[::-1][:7]]
  out.append({'id':int(i),'keywords':tokens,'articles':int(c.get(i,0))})
 return out
metrics=json.load(open(EVAL,encoding='utf-8'))
met=metrics['logistic_regression']['metrics'];svm=metrics['linear_svm']['metrics']
log_cv=[{ 'model':x.get('model',''),'cv_macro_f1':x.get('cv_macro_f1'), 'cv_accuracy':x.get('cv_accuracy')} for x in metrics.get('models',[]) if isinstance(x,dict)]

result={
 'meta':{
  'corpus':'BBC historical labeled research corpus',
  'source':'BBC News Train.csv (student supplied for course research)',
  'synthetic':False,'articles':int(len(df)), 'input_rows':int(pd.read_csv(SOURCE).shape[0]),
  'category_count':int(len(cat)),'dated_articles':0,'source_coverage':0,
  'search_method':'Not available for full BBC corpus: full article texts are not publicly hosted',
  'has_live_news':False,'article_text_public':False,
  'disclaimer':'Authentic historical BBC research statistics. This dataset has no publication dates and is not a live news feed. Full article texts are deliberately excluded from the public server.',
  'dataset_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
  'notes':'Aggregate counts, topic weights, and classifier evaluation only; no copyrighted article text.'
 },
 'categories':[{'label':str(k),'count':int(v),'percentage':round(100*v/len(df),1)} for k,v in cat.items()],
 'sentiments':[{'label':str(k),'count':int(v),'percentage':round(100*v/len(df),1)} for k,v in sorted(sent.items(),key=lambda x:-x[1])],
 'sentiment_method':'TextBlob lexical polarity with +0.10 and -0.10 cutoffs, descriptive estimate; not VADER or external validation',
 'sentiment_by_category':cat_sent,
 'topics':{'NMF':topics(Z,nmf.components_,tfidf.get_feature_names_out()),'LDA':topics(L,lda.components_,cv.get_feature_names_out())},
 'timeline':[],
 'evaluation':{'model':'TF IDF Logistic Regression, actual BBC labeled data','holdout_accuracy':met['holdout_accuracy'],
               'holdout_macro_f1':met['holdout_macro_f1'],'holdout_count':288,'source':'BBC deduplicated labeled Train, stratified 80/20, seed 42',
               'cross_validation':log_cv,
               'interpretation':'Internal held out evaluation, not external or current news accuracy. 50 duplicate texts removed before splitting.'},
 'bbc_classifier':{'active':True,'model':'TF IDF Logistic Regression','articles_used':1440,
                   'heldout_count':288,'heldout_accuracy':met['holdout_accuracy'],
                   'heldout_macro_f1':met['holdout_macro_f1'],
                   'comparison_svm_accuracy':svm['holdout_accuracy'],'comparison_svm_macro_f1':svm['holdout_macro_f1'],
                   'evaluation_source':'Real BBC labeled training corpus','note':'The research corpus is BBC. Stored article search is still a separately labeled synthetic demo. Full BBC article text is not redistributed.'},
 'chart_notes':{'categories':'Historical BBC label frequencies, not current news proportions',
               'sentiments':'TextBlob polarity on historical article texts; interpret cautiously',
               'topics':'NMF and LDA statistical topic assignments computed on authentic BBC training text; no time trend inferred',
               'timeline':'Historical BBC CSV has no verified publication timestamp'}
}
DEST.parent.mkdir(parents=True,exist_ok=True)
DEST.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print('WROTE',DEST,DEST.stat().st_size)
print('Counts',cat.to_dict(),'Sentiment',sent, 'topics',[(t['keywords'][:3],t['articles']) for t in result['topics']['NMF']])
