"""News article schema validation and leakage-aware duplicate controls."""
from pathlib import Path
import pandas as pd
from src.data_processing.text_preprocessor import clean_text

CATEGORY_MAP = {'tech':'technology','sports':'sport'}

def load_news_csv(path):
    """Accept BBC 'Text'/'Category' or general 'text'/'category' CSV schemas."""
    df=pd.read_csv(Path(path))
    mapping={c.lower().replace(' ',''): c for c in df.columns}
    textcol=next((mapping[k] for k in ('text','article','content','fulltext') if k in mapping),None)
    labelcol=next((mapping[k] for k in ('category','label','topic') if k in mapping),None)
    if textcol is None or labelcol is None:
        raise ValueError('Expected news text and category columns, such as Text and Category')
    out=pd.DataFrame({'text':df[textcol], 'category':df[labelcol]})
    for target,names in [('article_id',['articleid','article_id','id']),('date',['date','published_at','published','pubdate']),('source',['source','publisher']),('language',['language','lang'])]:
        col=next((mapping[k] for k in names if k in mapping),None)
        out[target]=df[col] if col else pd.NA
    out=out.dropna(subset=['text','category']).copy()
    out['text']=out.text.astype(str).map(clean_text)
    out['category']=out.category.astype(str).str.strip().str.lower().replace(CATEGORY_MAP)
    out=out[(out.text.str.len()>=30)&(out.category!='')]
    out=out.drop_duplicates(subset=['text']).reset_index(drop=True)
    out['article_id']=[str(v) if pd.notna(v) else f'N{i+1:05d}' for i,v in enumerate(out.article_id)]
    if out.article_id.duplicated().any():
        out['article_id']=[f'N{i+1:05d}' for i in range(len(out))]
    out['date']=pd.to_datetime(out['date'],errors='coerce',utc=True)
    return out

def quality_report(df):
    return {'articles':int(len(df)), 'categories':df.category.value_counts().to_dict(),
            'dated_articles':int(df.date.notna().sum()),'source_coverage':int(df.source.notna().sum())}
