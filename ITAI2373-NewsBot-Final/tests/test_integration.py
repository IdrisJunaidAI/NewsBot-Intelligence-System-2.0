import pytest
from src.system import NewsBotSystem
from config.settings import Settings

def test_full_pipeline():
    s=NewsBotSystem().fit_csv(Settings().demo_path,'synthetic tests')
    article='The software development team launched a robotics algorithm and deployed new cloud computing services.'
    result=s.analyze(article)
    assert result['classification']['category']
    assert len(result['topics'])==3
    assert result['summary']['summary']
    assert 'available' in result['entities']
    matches=s.search.search('cloud machine learning')['results']
    assert 1<=len(matches)<=5
    assert all(row['score']>0 for row in matches)
    count=s.ask('How many technology articles?')
    assert count['answer']=='12 matching articles in the loaded corpus.'
    follow=s.ask('Show me more',context=count['context'])
    assert follow['context']['category']=='technology'
    assert s.multilingual.compare('aprendizaje automático')['available'] is False

def test_unrelated_search_does_not_fake_matches():
    s=NewsBotSystem().fit_csv(Settings().demo_path,'synthetic tests')
    result=s.ask('Jessen Huang latest news')
    assert result['articles']==[]
    assert 'No relevant articles' in result['answer']
    assert 'not a live news service' in result['notice']
    assert s.search.search('ultraxylophone zanzibarquartz')['results']==[]

def test_category_browse_is_distinguished_from_search():
    s=NewsBotSystem().fit_csv(Settings().demo_path,'synthetic tests')
    found=s.ask('Show technology articles')
    assert found['intent']=='browse'
    assert 1<=len(found['articles'])<=5
    assert all(a['category']=='technology' and a['score'] is None for a in found['articles'])
    assert s.ask('Summarize sport')['answer']

def test_insufficient_input():
    s=NewsBotSystem().fit_csv(Settings().demo_path,'synthetic tests')
    with pytest.raises(ValueError):s.analyze('hello')
