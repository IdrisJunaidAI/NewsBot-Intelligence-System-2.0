"""Sentiment: VADER when installed, explicit limited dictionary fallback otherwise."""
import re
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    SentimentIntensityAnalyzer=None
_POS={'growth','improved','success','successful','won','increase','profitable','innovation','benefit','recovery','positive','strong','praised','record'}
_NEG={'decline','crisis','lost','fall','risk','failed','concern','shortage','negative','weak','injury','fraud','warning','damage'}
class SentimentAnalyzer:
    def __init__(self):
        self._model=SentimentIntensityAnalyzer() if SentimentIntensityAnalyzer is not None else None
    def analyze(self,text):
        if self._model:
            s=self._model.polarity_scores(text);v=s['compound'];method='VADER'
        else:
            tokens=re.findall(r"[a-z]+",text.lower())
            score=sum(t in _POS for t in tokens)-sum(t in _NEG for t in tokens)
            v=score/max(1,sum(t in _POS or t in _NEG for t in tokens)) if score else 0.0
            method='limited teaching lexicon; install vaderSentiment for VADER'
        return {'label':'positive' if v>=0.05 else 'negative' if v<=-0.05 else 'neutral',
                'score':round(float(v),4),'method':method,
                'note':'Text tone does not measure factual accuracy, bias, or actual public opinion'}
    def evolution(self,df):
        if df.date.notna().sum()<6:return {'available':False,'reason':'No suitable date coverage'}
        scored=df.dropna(subset=['date']).copy();scored['score']=scored.text.map(lambda t:self.analyze(t)['score'])
        scored['period']=scored.date.dt.strftime('%Y-%m')
        return {'available':True,'counts':scored.groupby('period').score.agg(['mean','count']).reset_index().to_dict('records')}
