from src.analysis.topic_modeler import TopicModeler
from src.data_processing.data_validator import load_news_csv
from config.settings import Settings

def test_both_models():
    df=load_news_csv(Settings().demo_path)
    t=TopicModeler(n_topics=4).fit(df.text)
    assert set(t.models)=={'LDA','NMF'}
    assert len(t.top_words('LDA'))==4
    assert len(t.top_words('NMF'))==4
    assert t.topic_evolution(df)['available']
