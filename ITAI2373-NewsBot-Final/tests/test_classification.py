import pytest
from src.analysis.classifier import NewsClassifier
from src.data_processing.data_validator import load_news_csv
from config.settings import Settings

def test_classifier_training():
    df=load_news_csv(Settings().demo_path)
    c=NewsClassifier(max_features=300).fit(df,source='synthetic pytest test')
    result=c.predict('A software developer launched a new machine learning system for cloud computing')
    assert result['category'] in set(df.category)
    assert abs(sum(result['probabilities'].values())-1)<0.001
    assert c.metrics['holdout_n']==12

def test_too_few_samples():
    df=load_news_csv(Settings().demo_path).iloc[:2]
    with pytest.raises(ValueError):NewsClassifier().fit(df)
