"""Offline query reliability and external translation rate limit regression tests."""
from types import SimpleNamespace

import pandas as pd

from src.multilingual.offline_query import offline_news_query
from src.multilingual.translator import Translator
from src.multilingual.language_detector import LanguageDetector
from src.multilingual.cross_lingual_analyzer import CrossLingualAnalyzer
from src.language_models.embeddings import SemanticSearch


def corpus():
    return pd.DataFrame([
        {"article_id":"TECH","category":"technology",
         "text":"The robotics technology company built machine learning algorithms for computing.",
         "source":"SYNTHETIC","date":pd.NaT},
        {"article_id":"SPORT","category":"sport",
         "text":"The football team won the match after a difficult championship season.",
         "source":"SYNTHETIC","date":pd.NaT},
        {"article_id":"POL","category":"politics",
         "text":"Parliament and the government introduced a public election policy.",
         "source":"SYNTHETIC","date":pd.NaT},
        {"article_id":"BUS","category":"business",
         "text":"The company discussed economy and bank investment in the market.",
         "source":"SYNTHETIC","date":pd.NaT},
    ])


def test_offline_keyword_map_spanish_and_french_is_not_translation():
    es = offline_news_query("Noticias sobre tecnología y robótica","es")
    assert es["available"]
    assert es["query_en"]=="technology robotics"
    assert "NOT full sentence translation" in es["note"]
    fr = offline_news_query("Actualités sur la technologie et la robotique","fr")
    assert fr["available"]
    assert fr["query_en"]=="technology robotics"
    unknown = offline_news_query("Una historia sobre el color púrpura","es")
    assert not unknown["available"]
    assert unknown["query_en"] is None


def test_offline_search_requires_no_consent_and_no_provider_calls():
    class ForbiddenTranslator:
        def translate(self,*args,**kwargs):
            raise AssertionError("An offline query must never contact a translation provider")
    search = SemanticSearch().fit(corpus())
    analyzer = CrossLingualAnalyzer(search,LanguageDetector(),ForbiddenTranslator())
    for query in ("Noticias sobre tecnología y robótica",
                  "Actualités sur la technologie et la robotique"):
        result = analyzer.compare(query,mode="offline",external_consent=True)
        assert result["available"]
        assert result["external_service_used"] is False
        assert result["matches"][0]["article_id"]=="TECH"
        assert result["mode"]=="offline"
        assert "Offline topic keywords" in result["method"]


def test_provider_too_many_requests_has_cooldown_and_no_repeat():
    class TooManyRequests(Exception):
        pass
    attempts = []
    time_state = [50.]
    class Provider:
        def __init__(self,source,target):
            pass
        def translate(self,text):
            attempts.append(1)
            raise TooManyRequests("do not display provider error contents")
    translator = Translator(provider_factory=Provider,clock=lambda:time_state[0])
    first=translator.translate("Noticias sobre tecnología y robótica",
                               source="es",target="en",external_consent=True)
    assert first["available"] is False
    assert first["error_code"]=="rate_limited"
    assert first["external_service_used"] is True
    assert "do not display" not in first["reason"]
    second=translator.translate("Noticias sobre tecnología y robótica",
                                source="es",target="en",external_consent=True)
    assert second["available"] is False
    assert second["error_code"]=="rate_limited"
    assert second["external_service_used"] is False
    assert len(attempts)==1
    assert translator.status()["rate_limited"] is True
    time_state[0]+=601.
    translator.translate("Noticias sobre tecnología y robótica",
                         source="es",target="en",external_consent=True)
    assert len(attempts)==2


def test_provider_rate_limit_falls_back_to_limited_offline_search():
    class TooManyRequests(Exception):
        pass
    class Provider:
        def __init__(self,source,target):
            pass
        def translate(self,text):
            raise TooManyRequests("Please retry later")
    search=SemanticSearch().fit(corpus())
    translator=Translator(provider_factory=Provider)
    analyzer=CrossLingualAnalyzer(search,LanguageDetector(),translator)
    result=analyzer.compare("Noticias sobre tecnología y robótica",
                            mode="translated",external_consent=True)
    assert result["available"]
    assert result["mode"]=="offline"
    assert result["fallback_from"]=="rate_limited"
    assert result["translation_error_code"]=="rate_limited"
    assert result["external_service_used"] is True
    assert result["matches"][0]["article_id"]=="TECH"
    assert "NOT full sentence translation" in result["note"]
    # A second request is handled locally during the cooldown.
    other=analyzer.compare("Noticias sobre tecnología y robótica",
                           mode="translated",external_consent=True)
    assert other["available"]
    assert other["external_service_used"] is False


def test_flask_offline_mode_and_spanish_comparison_do_not_call_provider(monkeypatch):
    import app as application
    class TranslatorForbidden:
        def status(self):
            return {"installed":False,"rate_limited":False}
        def translate(self,*args,**kwargs):
            raise AssertionError("No provider allowed for offline routes")
    search=SemanticSearch().fit(corpus())
    detector=LanguageDetector()
    translator=TranslatorForbidden()
    sys=SimpleNamespace(search=search,languages=detector,translator=translator,
                        source="SYNTHETIC",multilingual=CrossLingualAnalyzer(search,detector,translator))
    monkeypatch.setattr(application,"get_model",lambda:sys)
    application.app.config["TESTING"]=True
    with application.app.test_client() as client:
        status=client.get("/api/multilingual/status")
        assert status.status_code==200
        assert status.get_json()["offline_topic_search_available"]
        result=client.post("/api/multilingual/search",
            json={"query":"Noticias sobre tecnología y robótica","mode":"offline"})
        assert result.status_code==200
        payload=result.get_json()
        assert payload["matches"][0]["article_id"]=="TECH"
        assert payload["external_service_used"] is False
        comparison=client.post("/api/retrieval/compare",
            json={"query":"Actualités sur la technologie et la robotique"})
        assert comparison.status_code==200
        assert comparison.get_json()["normalized_query"]=="technology robotics"
        assert comparison.get_json()["lsa"]["results"][0]["article_id"]=="TECH"
        html=client.get("/").get_data(as_text=True)
        assert '<option value="offline" selected>' in html
