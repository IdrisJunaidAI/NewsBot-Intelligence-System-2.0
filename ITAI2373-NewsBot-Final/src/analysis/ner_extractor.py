"""spaCy named entity extraction with explicit availability reporting."""
from collections import Counter
try:import spacy
except ImportError:spacy=None
class EntityExtractor:
    def __init__(self):
        self.pipeline=None
        if spacy is not None:
            try:self.pipeline=spacy.load('en_core_web_sm')
            except OSError:pass
    def extract(self,text):
        if self.pipeline is None:
            return {'available':False,'entities':[],'reason':'Install spaCy and download en_core_web_sm for NER'}
        doc=self.pipeline(text)
        return {'available':True,'entities':[{'text':x.text,'label':x.label_} for x in doc.ents if x.label_ in ('PERSON','ORG','GPE','DATE','MONEY')][:30]}
    def relationships(self,text):
        result=self.extract(text)
        if not result['available']:return {'available':False,'pairs':[],'reason':result['reason']}
        e=list(dict.fromkeys((x['text'] for x in result['entities'] if x['label'] in ('PERSON','ORG','GPE'))))
        return {'available':True,'pairs':[[e[i],e[j]] for i in range(len(e)) for j in range(i+1,len(e))][:20],
           'note':'Same-article cooccurrence only; not verified affiliations or causality'}
