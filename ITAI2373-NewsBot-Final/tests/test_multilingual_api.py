"""Flask request contract tests for the multilingual lab without network services."""
from types import SimpleNamespace
import pandas as pd
import pytest

from src.language_models.embeddings import SemanticSearch
from src.multilingual.language_detector import LanguageDetector
from src.multilingual.translator import Translator
from src.multilingual.cross_lingual_analyzer import CrossLingualAnalyzer


@pytest.fixture()
def client(monkeypatch):
    import app as flask_module
    corpus = pd.DataFrame([
        {'article_id':'T1', 'text':'Engineers built robotics systems and algorithms for artificial intelligence.',
         'category':'technology', 'source':'SYNTHETIC', 'date':pd.NaT},
        {'article_id':'S1', 'text':'Football fans celebrated the last match and the championship.',
         'category':'sport', 'source':'SYNTHETIC', 'date':pd.NaT},
        {'article_id':'P1', 'text':'Government leaders approved a new political policy in parliament.',
         'category':'politics', 'source':'SYNTHETIC', 'date':pd.NaT},
        {'article_id':'E1', 'text':'The film director announced a new cinema award for actors.',
         'category':'entertainment', 'source':'SYNTHETIC', 'date':pd.NaT},
    ])
    search=SemanticSearch().fit(corpus)
    detector=LanguageDetector()
    calls=[]
    class FakeProvider:
        def __init__(self,source,target):
            calls.append((source,target))
        def translate(self,text):
            calls.append(text)
            return 'robotics algorithms'
    translator=Translator(provider_factory=FakeProvider)
    system=SimpleNamespace(search=search,languages=detector,translator=translator,
                           source='DEMO SYNTHETIC DATA ONLY',
                           multilingual=CrossLingualAnalyzer(search,detector,translator))
    monkeypatch.setattr(flask_module,'get_model',lambda:system)
    flask_module.app.config['TESTING']=True
    with flask_module.app.test_client() as http:
        yield http,calls


def test_status_and_language_detection(client):
    http,_=client
    data=http.get('/api/multilingual/status').get_json()
    assert data['supported_languages']==['en','es','fr']
    assert data['lsa_active'] is True
    assert data['multilingual_embeddings_active'] is False
    assert data['live_news'] is False
    response=http.post('/api/multilingual/detect',json={
        'text':'El gobierno presentó una nueva estrategia para mejorar el mercado y la economía.'})
    assert response.status_code==200
    assert response.get_json()['language']=='es'


def test_translator_requires_optin_and_does_not_transmit_without_it(client):
    http,calls=client
    query={'text':'El gobierno anunció una nueva estrategia económica.', 'source':'es','target':'en'}
    no=http.post('/api/multilingual/translate',json=query)
    assert no.status_code==422
    assert no.get_json()['available'] is False
    assert calls==[]
    yes=http.post('/api/multilingual/translate',json={**query,'external_consent':True})
    assert yes.status_code==200
    assert yes.get_json()['external_service_used'] is True
    assert len(calls)==2


def test_crosslanguage_methods_and_comparison(client):
    http,_=client
    unavailable=http.post('/api/multilingual/search',json={
        'query':'Investigación de robots para fábricas y máquinas','mode':'semantic'})
    assert unavailable.status_code==503
    assert not unavailable.get_json()['available']
    translated=http.post('/api/multilingual/search',json={
        'query':'Noticias sobre sistemas de robótica e inteligencia artificial',
        'mode':'translated','external_consent':True})
    assert translated.status_code==200
    body=translated.get_json()
    assert body['available']
    assert body['matches'][0]['article_id']=='T1'
    assert 'Translation-assisted' in body['method']
    compare=http.post('/api/retrieval/compare',json={'query':'robotics algorithms'})
    assert compare.status_code==200
    assert compare.get_json()['lsa']['results'][0]['article_id']=='T1'
    assert compare.get_json()['lexical']['results'][0]['article_id']=='T1'


def test_invalid_translation_and_query_return_400(client):
    http,_=client
    bad=http.post('/api/multilingual/translate',json={'text':'hello','target':'zz'})
    assert bad.status_code==400
    bad_query=http.post('/api/retrieval/compare',json={'query':''})
    assert bad_query.status_code==400
