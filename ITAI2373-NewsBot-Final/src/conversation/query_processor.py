"""Conversational queries over the loaded corpus, never an implied live news feed."""
import re
import pandas as pd
from src.conversation.intent_classifier import recognize_intent

# Tokens that do not add a named entity or an independent retrieval constraint.
_BROWSE_WORDS=set(
    'show list browse give find me us any some all the a an about in on from of '
    'news article articles stories story items records results please i want '
    'latest recent current positive negative neutral summarize summary brief'.split()
)
_LIVE_RE=re.compile(r'\b(latest|current|today|breaking|right now|real.time|recent)\b',re.I)

def _row_result(row):
    """Category browsing is not a text similarity match, so score is null."""
    def safe(value):
        return None if pd.isna(value) else str(value)
    return {'article_id':str(row.article_id),'category':str(row.category),
            'score':None,'snippet':str(row.text)[:250],
            'source':safe(row.source),'date':safe(row.date),
            'match_reason':'category browsing, not similarity search'}

class QueryProcessor:
    def __init__(self,system):self.system=system

    def process(self,query,context=None):
        state=dict(context or {})
        if not isinstance(query,str) or not query.strip():raise ValueError('Question is required')
        query=query.strip(); lower=query.lower(); intent=recognize_intent(query)
        for c in self.system.df.category.unique():
            if re.search(r'\b'+re.escape(str(c))+r'\b',lower):
                state['category']=str(c);break
        for word in ('positive','negative','neutral'):
            if re.search(r'\b'+word+r'\b',lower):state['sentiment']=word;break
        if re.search(r'\b(reset|clear filters)\b',lower):state={}
        source_df=self.system.df
        if 'category' in state:source_df=source_df[source_df.category==state['category']]
        if 'sentiment' in state:
            labels=source_df.text.map(lambda x:self.system.sentiment.analyze(x)['label'])
            source_df=source_df[labels==state['sentiment']]
        note=('This is a fixed collection, not a live news service. '
              'The system cannot confirm the latest developments.') if _LIVE_RE.search(lower) else None
        if re.search(r'\b(this week|past week|last seven days)\b',lower):
            if source_df.date.notna().sum()==0:
                return {'intent':intent,'answer':'Date filtering is unavailable: the corpus has no verified publication dates.',
                        'articles':[],'context':state,'notice':note}
            from pandas import Timestamp,Timedelta
            cutoff=Timestamp.now(tz='UTC')-Timedelta(days=7)
            source_df=source_df[source_df.date>=cutoff]

        # A category-only command is a browse action, not a claim of lexical
        # relevance. Never use this fallback for queries naming people/events.
        tokens=set(re.findall(r"[a-z]+",lower))
        category_tokens={str(state['category']).lower()} if 'category' in state else set()
        generic=bool(category_tokens and tokens <= _BROWSE_WORDS | category_tokens)
        if intent=='count':
            if not generic and tokens - (_BROWSE_WORDS | category_tokens |
                                         {'how','many','count','number','are','there','is','were','have','been'}):
                matches=self.system.search.search(query,top_k=len(source_df),
                    category=state.get('category'))['results']
                allowed=set(source_df.article_id)
                total=sum(r['article_id'] in allowed for r in matches)
                answer=f'{total} relevant articles in the loaded corpus (lexical search, not live news).'
            else:
                total=len(source_df)
                answer=f'{total} matching articles in the loaded corpus.'
            return {'intent':intent,'answer':answer,'articles':[],'context':state,'notice':note}
        if intent=='topics':
            terms=self.system.topics.top_words('NMF',5)
            return {'intent':intent,'answer':'Topics are statistical word clusters, not verified events.',
                    'topics':terms,'articles':[],'context':state,'notice':note}
        if generic and intent=='search':
            rows=source_df.head(5)
            matches=[_row_result(row) for _,row in rows.iterrows()]
            return {'intent':'browse','answer':f'Showing {len(matches)} of {len(source_df)} stored articles '
                    f'in the selected category or sentiment filters.',
                    'articles':matches,'context':state,'notice':note}

        if intent=='summarize' and len(source_df)>0:
            results=self.system.search.search(query,top_k=1,category=state.get('category'))['results']
            if not results and generic:
                results=[_row_result(source_df.iloc[0])]
            if results:
                matched=source_df[source_df.article_id==results[0]['article_id']]
                if len(matched):
                    summary=self.system.summarizer.summarize(str(matched.iloc[0].text))['summary']
                    return {'intent':intent,'answer':summary,'articles':[results[0]],'context':state,
                        'note':'Extracted source sentences, not independently verified','notice':note}
        result=self.system.search.search(query,top_k=5,category=state.get('category'))
        allowed=set(source_df.article_id)
        matches=[r for r in result['results'] if r['article_id'] in allowed]
        answer=(f'Found {len(matches)} relevant stored articles. Retrieval method: {result["method"]}.'
                if matches else
                'No relevant articles were found in this loaded collection. '
                'Try a category query such as "Show technology articles".')
        return {'intent':intent,'answer':answer,'articles':matches,
                'context':state,'notice':note}
