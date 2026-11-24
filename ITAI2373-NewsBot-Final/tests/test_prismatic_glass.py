"""Glass design regression coverage without altering the underlying NLP system."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CSS=ROOT/"static"/"prismatic_glass.css"

def test_glass_styles_are_local_and_support_contrast():
    sheet=CSS.read_text(encoding="utf-8")
    assert "backdrop-filter:" in sheet
    assert "-webkit-backdrop-filter:" in sheet
    assert "@supports not" in sheet
    assert "prefers-reduced-motion:reduce" in sheet
    assert "prefers-reduced-transparency:reduce" in sheet
    assert "prefers-contrast:more" in sheet
    assert "https://" not in sheet
    assert "@import" not in sheet

def test_cinematic_glass_applies_to_existing_site_sections():
    sheet=CSS.read_text(encoding="utf-8")
    for selector in ("header{",".portfolio-nav{",".kpi-card,.viz-card,.bbc-rss,.lang-lab,.lang-panel,.card{",
                     ".bbc-headline-card",".nb-glass-signals{"):
        assert selector in sheet

def test_glass_css_is_last_so_original_components_remain_credited():
    import app
    with app.app.test_client() as client:
        result=client.get("/")
        glass=client.get("/static/prismatic_glass.css")
        assert result.status_code==200
        assert glass.status_code==200
        html=result.get_data(as_text=True)
    assert "/static/studio_theme.css?v=1" in html
    assert "/static/uiverse_components.css?v=1" in html
    assert "/static/prismatic_glass.css?v=1" in html
    assert html.index("studio_theme.css") < html.index("uiverse_components.css") < html.index("prismatic_glass.css")
    assert html.count('class="nb-glass-signal"')==3

def test_provenance_and_education_boundaries_remain_clear():
    html=(ROOT/"templates"/"index.html").read_text(encoding="utf-8")
    for message in ("HISTORICAL BBC RESEARCH","ATTRIBUTED BBC RSS LINKS",
                    "English, Spanish and French intelligence",
                    "Current BBC News headlines",
                    "Real historical BBC research analytics and live RSS are separate."):
        assert message in html
    assert 'id="nb_dataset_switch"' in html
    assert 'id="nb-summary-play"' in html
    assert 'id="nb-loading-curtain"' in html
    assert 'id="ml_consent"' in html

def test_individual_submission_status_is_consistent_and_not_overclaimed():
    compliance=(ROOT/"docs"/"individual_submission_compliance.md").read_text(encoding="utf-8")
    contributions=(ROOT/"docs"/"individual_contributions.md").read_text(encoding="utf-8")
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    for content in (compliance,contributions,readme):
        assert "individual" in content.lower()
        assert "November 24, 2026" in content
        assert "independently" in content.lower()
        assert "reported" in content.lower()
    assert "Instructor acceptance of that format has **not** been documented" not in contributions

def test_previous_uiverse_license_notices_preserved():
    stylesheet=(ROOT/"static"/"uiverse_components.css").read_text(encoding="utf-8")
    for author in ("asif_6635","StealthWorm","Pradeepsaranbishnoi","Nawsome","kelvyn_8843"):
        assert "From Uiverse.io by "+author in stylesheet
    assert stylesheet.count("MIT License")>=5
