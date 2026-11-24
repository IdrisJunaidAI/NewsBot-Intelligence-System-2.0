"""Bonus frontend and authentic research extension regression tests."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.utils.batch_analysis import analyze_articles
from src.utils.research_bonus import learning_curve_report

ROOT = Path(__file__).resolve().parents[1]
ARTICLE1 = ("Technology researchers introduced software for a new robotics and "
            "machine learning system used in public manufacturing.")
ARTICLE2 = ("The government announced a business investment policy to support "
            "regional services, new employment, and local market development.")


def fake_system():
    calls = []
    def analyze(text):
        calls.append(text)
        return {
            "classification": {"category": "technology", "model_probability": 0.72},
            "sentiment": {"label": "neutral"},
            "language": {"language": "en"},
            "summary": {"summary": text[:90]},
            "needs_human_review": False,
            "language_limitation": None,
            "model_source": "Real historical BBC model",
        }
    return SimpleNamespace(analyze=analyze), calls


def test_fewshot_research_is_real_measured_computed_csv():
    evidence = learning_curve_report()
    assert evidence["available"]
    assert evidence["source"].startswith("Authentic historical BBC")
    assert evidence["original_article_text_published"] is False
    assert evidence["heldout_articles"] == 288
    assert evidence["total_model_fits"] == 25
    assert [p["per_class_samples"] for p in evidence["points"]] == [5,10,25,50,100]
    assert all(p["repetitions"] == 5 for p in evidence["points"])
    assert all(len(p["seeds"]) == 5 for p in evidence["points"])
    assert evidence["points"][0]["mean_macro_f1"] == pytest.approx(0.852566, abs=0.00002)
    assert evidence["points"][4]["mean_macro_f1"] == pytest.approx(0.956111, abs=0.00003)


def test_missing_or_tampered_research_file_fails_closed(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("per_class_samples,total_training_samples,seed,holdout_macro_f1,holdout_accuracy\n5,25,17,2,2\n")
    with pytest.raises(ValueError):
        learning_curve_report(p)


def test_batch_analyzes_two_and_returns_no_unrequested_raw_inputs():
    service, calls = fake_system()
    result = analyze_articles(service,[ARTICLE1,ARTICLE2])
    assert result["processed"] == 2
    assert len(calls) == 2
    assert result["results"][0]["article_number"] == 1
    assert result["results"][0]["category"] == "technology"
    assert result["results"][0]["classifier_source"] == "Real historical BBC model"
    assert "submitted" in result["disclaimer"].lower()


@pytest.mark.parametrize("bad", [
    None, "article", [], [ARTICLE1], [ARTICLE1] * 6,
    [ARTICLE1, "too short"], [ARTICLE1, 4],
    [ARTICLE1, "x" * 5001], ["a" * 4000] * 4,
])
def test_bad_batch_rejected_before_any_model_inference(bad):
    service, calls = fake_system()
    with pytest.raises(ValueError):
        analyze_articles(service,bad)
    assert calls == []


def test_bonus_flask_routes_and_content_type(monkeypatch):
    import app as server
    service, calls = fake_system()
    monkeypatch.setattr(server, "get_model", lambda: service)
    with server.app.test_client() as client:
        research = client.get("/api/research/fewshot")
        assert research.status_code == 200
        assert research.get_json()["total_model_fits"] == 25
        assert research.headers["Cache-Control"].startswith("public")
        good = client.post("/api/batch/analyze", json={"articles":[ARTICLE1,ARTICLE2]})
        assert good.status_code == 200
        assert good.get_json()["processed"] == 2
        assert good.headers["Cache-Control"] == "no-store"
        assert client.post("/api/batch/analyze", json={"articles":[ARTICLE1]}).status_code == 400
        assert client.post("/api/batch/analyze", json=["invalid"]).status_code == 400
        assert client.post("/api/batch/analyze", data="nope", content_type="text/plain").status_code == 400
    assert len(calls) == 2


def test_bonus_structural_ui_uses_existing_glass_and_credit_preservation():
    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "static" / "bonus_features.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "bonus_research.css").read_text(encoding="utf-8")
    assert 'id="bonus_research_title"' in html
    assert 'id="bonus_batch_text"' in html
    assert 'id="bonus_batch_run"' in html
    assert 'id="bonus_research_chart"' in html
    assert "/static/bonus_features.js?v=1" in html
    assert "/static/bonus_research.css?v=1" in html
    assert "/api/research/fewshot" in js
    assert "/api/batch/analyze" in js
    assert "textContent" in js
    assert "innerHTML" not in js
    assert "prefers-reduced-transparency:reduce" in css
    assert "uiverse_components.css" in html
    assert "prismatic_glass.css" in html
