"""Reproducible, leakage-aware BBC News classifier evaluation.

Never use the BBC News Sample Solution categories as ground truth. Its five-class
sequence is a formatting placeholder. This script evaluates using a stratified
split of deduplicated labeled training articles, then exports predictions for
all unlabeled test articles. Raw article content is not included in reports.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.metrics import accuracy_score, f1_score, balanced_accuracy_score, classification_report, confusion_matrix
import joblib

SEED=42
MAPPING={'tech':'technology','sports':'sport'}

def normalize(series):
    return series.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()

def read_datasets(train_path:Path, test_path:Path, sample_path:Path|None=None):
    raw=pd.read_csv(train_path)
    test=pd.read_csv(test_path)
    required={'ArticleId','Text','Category'}
    if not required.issubset(raw.columns):raise ValueError(f'Training CSV missing {required - set(raw.columns)}')
    if not {'ArticleId','Text'}.issubset(test.columns):raise ValueError('Test CSV requires ArticleId and Text')
    if raw[list(required)].isna().any().any():raise ValueError('Training contains missing required values')
    if test[['ArticleId','Text']].isna().any().any():raise ValueError('Test contains missing required values')
    cleaned=raw.copy()
    cleaned['Text']=normalize(cleaned.Text)
    cleaned['Category']=cleaned.Category.astype(str).str.strip().str.lower().replace(MAPPING)
    cleaned=cleaned[cleaned.Text.str.len()>=30].drop_duplicates('Text',keep='first').reset_index(drop=True)
    normalized_test=normalize(test.Text)
    raw_train=set(normalize(raw.Text))
    distinct_overlap=set(cleaned.Text).intersection(set(normalized_test))
    info={
       'train_csv_sha256':hashlib.sha256(train_path.read_bytes()).hexdigest(),
       'test_csv_sha256':hashlib.sha256(test_path.read_bytes()).hexdigest(),
       'train_input_rows':len(raw),'train_retained_unique_rows':len(cleaned),
       'train_duplicates_or_short_removed':len(raw)-len(cleaned),
       'test_rows':len(test),'test_unique_texts':int(normalized_test.nunique()),
       'train_test_exact_text_overlap_unique':len(distinct_overlap),
       'training_class_counts':cleaned.Category.value_counts().sort_index().to_dict(),
       'test_has_ground_truth':False,
    }
    if sample_path:
       sample=pd.read_csv(sample_path)
       if not {'ArticleId','Category'}.issubset(sample.columns):raise ValueError('Sample solution requires ArticleId and Category')
       if list(sample.ArticleId)!=list(test.ArticleId):raise ValueError('Sample solution ArticleIds out of order')
       labels=sample.Category.astype(str).to_list()
       repeats=bool(len(labels)>=10 and all(label==labels[i%5] for i,label in enumerate(labels)))
       info['sample_solution_sha256']=hashlib.sha256(sample_path.read_bytes()).hexdigest()
       info['sample_solution_repeating_five_class_pattern']=repeats
       info['sample_solution_notice']='Illustrative submission labels, not verified ground truth; never score against these labels.'
    return cleaned,test,info

def vectorizer():return TfidfVectorizer(stop_words='english',ngram_range=(1,2),max_features=12000,sublinear_tf=True)

def pipeline(est):return Pipeline([('tfidf',vectorizer()),('clf',est)])

def model_families():return {
    'Majority baseline':DummyClassifier(strategy='most_frequent'),
    'Multinomial Naive Bayes':MultinomialNB(),
    'Logistic Regression':LogisticRegression(max_iter=1500,random_state=SEED),
    'Linear SVM':LinearSVC(random_state=SEED),
}

def run_experiment(train_path, test_path, sample_path, output_path, enable_fewshot=True):
    out=Path(output_path);out.mkdir(parents=True,exist_ok=True)
    unique,test,info=read_datasets(Path(train_path),Path(test_path),Path(sample_path) if sample_path else None)
    x_train,x_hold,y_train,y_hold=train_test_split(unique.Text,unique.Category,test_size=0.20,random_state=SEED,stratify=unique.Category)
    indices_train=set(x_train.index);indices_hold=set(x_hold.index)
    assert not indices_train.intersection(indices_hold)
    assert not set(x_train).intersection(set(x_hold)),'Data leakage: duplicate text crossed the split'
    info.update({'split_seed':SEED,'split_stratified':True,'split_after_deduplication':True,
         'training_partition_rows':len(x_train),'heldout_partition_rows':len(x_hold),
         'holdout_class_counts':y_hold.value_counts().sort_index().to_dict(),
         'vectorizer':'TF IDF, English stop words, unigrams/bigrams, 12000 features, sublinear TF',
         'category_mapping':MAPPING,'ground_truth_source':'BBC News Train.csv labels, exclusively'})
    folds=StratifiedKFold(n_splits=3,shuffle=True,random_state=SEED)
    comparisons=[];heldout_results={}
    for name,est in model_families().items():
      model=pipeline(est)
      cv=cross_validate(model,x_train,y_train,cv=folds,scoring={'macro_f1':'f1_macro','accuracy':'accuracy'},n_jobs=1)
      model.fit(x_train,y_train)
      yp=model.predict(x_hold)
      scores={'model':name,'cv_macro_f1':float(cv['test_macro_f1'].mean()),'cv_accuracy':float(cv['test_accuracy'].mean()),
              'holdout_accuracy':float(accuracy_score(y_hold,yp)),
              'holdout_macro_f1':float(f1_score(y_hold,yp,average='macro')),
              'holdout_balanced_accuracy':float(balanced_accuracy_score(y_hold,yp))}
      comparisons.append(scores)
      heldout_results[name]={'metrics':scores,'report':classification_report(y_hold,yp,output_dict=True,zero_division=0),
          'confusion':confusion_matrix(y_hold,yp,labels=sorted(unique.Category.unique())).tolist()}
      if name=='Logistic Regression':
          holdout=pd.DataFrame({'ArticleId':unique.loc[y_hold.index,'ArticleId'].to_numpy(),
                                'TrueCategory':y_hold.to_numpy(), 'PredictedCategory':yp,
                                'Correct':yp==y_hold.to_numpy()})
          holdout.to_csv(out/'holdout_predictions.csv',index=False)
      print(name, 'macro F1',round(scores['holdout_macro_f1'],4),'acc',round(scores['holdout_accuracy'],4),flush=True)
    classes=sorted(unique.Category.unique())
    canonical=pipeline(LogisticRegression(max_iter=1500,random_state=SEED));canonical.fit(unique.Text,unique.Category)
    predictions=canonical.predict(normalize(test.Text))
    submission=pd.DataFrame({'ArticleId':test.ArticleId, 'Category':pd.Series(predictions).replace({'technology':'tech'})})
    submission.to_csv(out/'BBC_Test_Predictions.csv',index=False)
    assert submission.ArticleId.equals(test.ArticleId)
    # Portable, trusted local pipeline; does not serialize raw article texts.
    joblib.dump(canonical,out/'bbc_classifier_pipeline.joblib',compress=3)
    fresults=[]
    if enable_fewshot:
      # Genuine low-data experiment: use only selected labeled rows from the
      # TRAIN partition, keep the held-out labels wholly isolated.
      rngseeds=[17,29,43,71,97]
      frame=pd.DataFrame({'text':x_train, 'label':y_train})
      for k in [5,10,25,50,100]:
        for s in rngseeds:
          examples=frame.groupby('label',group_keys=False).sample(n=k,random_state=s)
          model=pipeline(LogisticRegression(max_iter=1500,random_state=SEED))
          model.fit(examples.text, examples.label)
          pred=model.predict(x_hold)
          fresults.append({'per_class_samples':k,'total_training_samples':len(examples),'seed':s,
              'holdout_macro_f1':float(f1_score(y_hold,pred,average='macro')),
              'holdout_accuracy':float(accuracy_score(y_hold,pred))})
      pd.DataFrame(fresults).to_csv(out/'fewshot_learning_curve.csv',index=False)
    # Save aggregate evidence, no raw article text.
    record={'provenance':info,'classes':classes,'models':comparisons,
       'logistic_regression':heldout_results['Logistic Regression'],
       'linear_svm':heldout_results['Linear SVM'],
       'fewshot_study':{
          'purpose':'Few-shot training size experiment using disjoint fixed labeled holdout',
          'repetitions':5,'sample_sizes_per_class':[5,10,25,50,100],
          'results':fresults,'model':'Logistic Regression TF IDF',
          'limitation':'Low-data learning curve on a historical news corpus; does not establish multilingual ability or current-news reliability'},
       'test_prediction_notice':'BBC Test has no verified labels; no test accuracy is calculated. Sample Solution is a cyclic placeholder.',
       'evaluation_note':'Historical, within-corpus stratified holdout. Duplicate texts removed before splitting. Comparison with midterm is descriptive, not identical folds.'}
    (out/'bbc_evaluation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print('Saved to',out)
    return record

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--train',required=True);p.add_argument('--test',required=True)
 p.add_argument('--sample',default=None);p.add_argument('--out',required=True)
 p.add_argument('--skip-fewshot',action='store_true')
 a=p.parse_args()
 run_experiment(a.train,a.test,a.sample,a.out,enable_fewshot=not a.skip_fewshot)
