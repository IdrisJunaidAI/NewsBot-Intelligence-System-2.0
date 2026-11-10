"""Conversational queries over corpus with persistent caller-managed context."""
import re
from src.conversation.intent_classifier import recognize_intent

class QueryProcessor:
    def __init__(self,system):self.system=system
    def process(self,query,context=None):
        state=dict(context or {})
        if not isinstance(query,str) or not query.strip():raise ValueError('Question is required')
        query=query.strip();intent=recognize_intent(query)
        for c in self.system.df.category.unique():
            if re.search(r'\b'+re.escape(str(c))+r'\b',query.lower()):state['category']=str(c);break
        for word in ('positive','negative','neutral'):
            if re.search(r'\b'+word+r'\b',query.lower()):state['sentiment']=word;break
        if re.search(r'\b(reset|clear filters)\b',query.lower()):state={}
        source_df=self.system.df
        if 'category' in state:source_df=source_df[source_df.category==state['category']]
        if 'sentiment' in state:
            # For small educational corpora this computes scores at query time.
            labels=source_df.text.map(lambda x:self.system.sentiment.analyze(x)['label'])
            source_df=source_df[labels==state['sentiment']]
        if re.search(r'\b(this week|past week|last seven days)\b',query.lower()):
            if source_df.date.notna().sum()==0:
                return {'intent':intent,'answer':'Date filtering unavailable: corpus has no verified publication dates.',
                        'articles':[],'context':state}
            from pandas import Timestamp,Timedelta
            cutoff=Timestamp.now(tz='UTC')-Timedelta(days=7)
            source_df=source_df[source_df.date>=cutoff]
        if intent=='count':
            return {'intent':intent,'answer':f'{len(source_df)} matching articles in the loaded corpus.',
                    'articles':[],'context':state}
        if intent=='topics':
            terms=self.system.topics.top_words('NMF',5)
            return {'intent':intent,'answer':'Topics are statistical word clusters, not verified events.',
                    'topics':terms,'articles':[],'context':state}
        if intent=='summarize' and len(source_df)>0:
            result=self.system.search.search(query,top_k=1,category=state.get('category'))['results']
            if result:
                matched=source_df[source_df.article_id==result[0]['article_id']]
                if len(matched):
                    summary=self.system.summarizer.summarize(str(matched.iloc[0].text))['summary']
                    return {'intent':intent,'answer':summary,'articles':[result[0]],'context':state,
                        'note':'Extracted source sentences, not independently verified'}
        result=self.system.search.search(query,top_k=5,category=state.get('category'))
        matches=[r for r in result['results'] if r['article_id'] in set(source_df.article_id)]
        return {'intent':intent,'answer':f'Found {len(matches)} matching articles. Retrieval method: {result["method"]}.',
                'articles':matches,'context':state}
