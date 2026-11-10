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
    assert len(s.search.search('cloud machine learning')['results'])==5
    count=s.ask('How many technology articles?')
    assert count['answer']=='12 matching articles in the loaded corpus.'
    follow=s.ask('Show me more',context=count['context'])
    assert follow['context']['category']=='technology'
    assert s.multilingual.compare('aprendizaje automático')['available'] is False

def test_insufficient_input():
    s=NewsBotSystem().fit_csv(Settings().demo_path,'synthetic tests')
    with pytest.raises(ValueError):s.analyze('hello')
