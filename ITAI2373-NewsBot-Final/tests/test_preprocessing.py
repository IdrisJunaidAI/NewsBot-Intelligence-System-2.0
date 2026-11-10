import pytest
from src.data_processing.text_preprocessor import clean_text
from src.data_processing.data_validator import load_news_csv
from config.settings import Settings

def test_markup():
    assert clean_text(' <p>A &amp; B</p>  ')=='A & B'
def test_bad_input():
    with pytest.raises(TypeError):clean_text(None)
def test_demo_schema():
    df=load_news_csv(Settings().demo_path)
    assert len(df)==60 and len(df.category.unique())==5
    assert df.article_id.is_unique
    assert df.date.notna().all()
