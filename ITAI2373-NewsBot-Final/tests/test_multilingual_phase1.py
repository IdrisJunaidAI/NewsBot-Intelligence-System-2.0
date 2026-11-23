"""English, Spanish, French and retrieval boundary regression tests."""
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from src.language_models.embeddings import SemanticSearch
from src.multilingual.language_detector import LanguageDetector
from src.multilingual.translator import Translator
from src.multilingual.cross_lingual_analyzer import CrossLingualAnalyzer

DATA = pd.DataFrame([
    {'article_id':'A1', 'text':'The researchers launched an AI robotics algorithm using machine learning to improve production.', 'category':'technology', 'date':pd.NaT, 'source':'Demo'},
    {'article_id':'A2', 'text':'A new football team won the championship after the match and supporters celebrated.', 'category':'sport', 'date':pd.NaT, 'source':'Demo'},
    {'article_id':'A3', 'text':'The government debated public policy and new election legislation at parliament.', 'category':'politics', 'date':pd.NaT, 'source':'Demo'},
    {'article_id':'A4', 'text':'The bank announced rising business revenue and quarterly earnings in financial markets.', 'category':'business', 'date':pd.NaT, 'source':'Demo'},
    {'article_id':'A5', 'text':'The film studio released a new movie starring international performers and artists.', 'category':'entertainment', 'date':pd.NaT, 'source':'Demo'},
    {'article_id':'A6', 'text':'Software engineers developed a cloud platform and deployed computer services worldwide.', 'category':'technology', 'date':pd.NaT, 'source':'Demo'},
])


def test_language_detection_three_supported_languages():
    detect = LanguageDetector().detect
    assert detect('The government and the market discussed a technology company and its future policies.')['language'] == 'en'
    assert detect('El gobierno anunció nuevas políticas para la economía y el mercado de tecnología.')['language'] == 'es'
    assert detect('Le gouvernement a annoncé un nouveau programme pour le marché et la technologie.')['language'] == 'fr'
    assert detect('hi')['language'] == 'unknown'


def test_opt_in_translation_and_privacy_boundary():
    calls=[]
    class FakeProvider:
        def __init__(self, **kwargs):
            calls.append(kwargs)
        def translate(self, text):
            calls.append(text)
            return 'The robotics team built a prototype.'
    translator=Translator(provider_factory=FakeProvider)
    block=translator.translate('El equipo construyó un prototipo',source='es',target='en')
    assert not block['available'] and not calls
    ok=translator.translate('El equipo construyó un prototipo',source='es',target='en',external_consent=True)
    assert ok['available'] and ok['external_service_used'] and len(calls)==2
    assert translator.translate('Bonjour le monde',source='fr',target='fr')['text']=='Bonjour le monde'
    with pytest.raises(ValueError):translator.translate('s' * 2001,source='fr',target='en',external_consent=True)
    with pytest.raises(ValueError):translator.translate('Hello',target='zz')


def test_lsa_and_lexical_search_are_distinct_from_multilingual_transformers():
    search=SemanticSearch().fit(DATA)
    assert search.lsa_available
    assert 'LSA' in search.method
    assert search.search('robotics algorithm',mode='lexical')['results'][0]['article_id']=='A1'
    assert search.search('robotics algorithm',mode='lsa')['results'][0]['article_id']=='A1'
    assert search.search('flurblexes zovaxium',mode='lsa')['results']==[]
    with pytest.raises(RuntimeError):search.search('robotics algorithm',mode='semantic')


def test_multilingual_semantics_requires_true_dense_encoder():
    s=SemanticSearch().fit(DATA)
    cross=CrossLingualAnalyzer(s,LanguageDetector(),Translator())
    result=cross.compare('Tecnología y robots para la industria',mode='semantic')
    assert result['available'] is False
    assert 'encoder' in result['reason']


def test_translation_assisted_search_and_provider_consent():
    class MockTranslator:
        def translate(self,text,source,target,external_consent):
            return {'available':external_consent,'text':'robotics algorithm' if external_consent else None,
                    'reason':'Consent required','external_service_used':external_consent}
    s=SemanticSearch().fit(DATA)
    cross=CrossLingualAnalyzer(s,LanguageDetector(),MockTranslator())
    query='Noticias sobre robótica y algoritmos de inteligencia artificial'
    assert not cross.compare(query,mode='translated',external_consent=False)['available']
    result=cross.compare(query,mode='translated',external_consent=True)
    assert result['available']
    assert result['matches'][0]['article_id']=='A1'
    assert 'Translation-assisted' in result['method']
    assert 'NOT shared multilingual transformer' in result['note']


def test_injected_multilingual_encoder_simulates_dense_path_without_claiming_external_model_validation():
    def feat(text):
        t=text.lower()
        return [1,0,0] if ('robot' in t or 'robótica' in t) else ([0,1,0] if 'government' in t else [0,0,1])
    class FakeEncoder:
        def encode(self,texts,normalize_embeddings=True):
            return np.array([feat(t) for t in texts],dtype=float)
    search=SemanticSearch(use_embeddings=True,encoder=FakeEncoder()).fit(DATA)
    result=CrossLingualAnalyzer(search,LanguageDetector(),Translator()).compare(
        'El laboratorio de robótica inventó nuevos sistemas',mode='semantic')
    assert result['available'] and result['matches'][0]['article_id']=='A1'
    assert result['method']=='multilingual sentence embeddings'
