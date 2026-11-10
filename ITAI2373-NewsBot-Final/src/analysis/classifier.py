"""Supervised document classification with held-out evaluation and model comparison."""
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.metrics import accuracy_score, f1_score, classification_report
from src.data_processing.feature_extractor import make_tfidf
import numpy as np

class NewsClassifier:
    """Train probabilities with logistic regression; benchmark SVM and Naive Bayes."""
    def __init__(self,max_features=12000,seed=42):
        self.max_features=max_features
        self.seed=seed
        self.model=None
        self.metrics={}
        self.training_source='not trained'

    def fit(self,df,source='unspecified'):
        counts=df.category.value_counts()
        if len(counts)<2 or counts.min()<4:
            raise ValueError('Need at least two categories and four articles per category')
        xtr,xts,ytr,yts=train_test_split(df.text,df.category,test_size=.20,
                    stratify=df.category,random_state=self.seed)
        minimum=ytr.value_counts().min()
        folds=min(3,int(minimum))
        models={
            'Majority baseline':DummyClassifier(strategy='most_frequent'),
            'Multinomial Naive Bayes':MultinomialNB(),
            'Logistic Regression':LogisticRegression(max_iter=1500,random_state=self.seed),
            'Linear SVM':LinearSVC(random_state=self.seed)
        }
        comparison=[]
        for name,estimator in models.items():
            pipe=Pipeline([('tfidf',make_tfidf(self.max_features)),('clf',estimator)])
            cv=StratifiedKFold(n_splits=folds,shuffle=True,random_state=self.seed)
            scores=cross_validate(pipe,xtr,ytr,cv=cv,scoring={'macro_f1':'f1_macro','accuracy':'accuracy'},n_jobs=1)
            comparison.append({'model':name, 'cv_macro_f1':float(scores['test_macro_f1'].mean()),
                               'cv_accuracy':float(scores['test_accuracy'].mean())})
        # Logistic Regression supports predict_proba; these are model probabilities, not calibration guarantees.
        self.model=Pipeline([('tfidf',make_tfidf(self.max_features)),('clf',LogisticRegression(max_iter=1500,random_state=self.seed))])
        self.model.fit(xtr,ytr)
        pred=self.model.predict(xts)
        self.metrics={'source':source,'n_articles':int(len(df)),'holdout_n':int(len(xts)),
             'logistic_heldout_accuracy':float(accuracy_score(yts,pred)),
             'logistic_heldout_macro_f1':float(f1_score(yts,pred,average='macro')),
             'cv_comparison':comparison,'per_class':classification_report(yts,pred,output_dict=True,zero_division=0),
             'evaluation_note':'Independent 20% held-out partition; demonstration data cannot establish real-world reliability'}
        self.training_source=source
        # Fit final inference model on all available data AFTER evaluation, with metrics retained as holdout record.
        self.model.fit(df.text,df.category)
        return self

    def predict(self,text):
        if self.model is None: raise RuntimeError('Classifier untrained. Run train.py with the BBC CSV')
        distribution=self.model.predict_proba([text])[0]
        idx=int(np.argmax(distribution))
        return {'category':str(self.model.classes_[idx]),'model_probability':float(distribution[idx]),
                'probabilities':{str(c):round(float(p),4) for c,p in zip(self.model.classes_,distribution)},
                'model':'Logistic Regression / TF IDF',
                'note':'Probability is uncalibrated and should not be treated as guaranteed correctness'}
