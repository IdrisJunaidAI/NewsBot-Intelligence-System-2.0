"""Structural and integration regression checks for the five credited UI components."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"

def test_uiverse_credit_comments_are_in_committed_source():
    css=(STATIC / "uiverse_components.css").read_text(encoding="utf-8")
    js=(STATIC / "uiverse_components.js").read_text(encoding="utf-8")
    refs = [
        ("asif_6635","https://uiverse.io/asif_6635/moody-turtle-2"),
        ("StealthWorm","https://uiverse.io/StealthWorm/spotty-horse-48"),
        ("Pradeepsaranbishnoi","https://uiverse.io/Pradeepsaranbishnoi/honest-penguin-58"),
        ("Nawsome","https://uiverse.io/Nawsome/breezy-ape-20"),
        ("kelvyn_8843","https://uiverse.io/kelvyn_8843/big-cheetah-20"),
    ]
    assert css.lstrip().startswith("/*") and js.lstrip().startswith("/*")
    for author,url in refs:
        assert f"From Uiverse.io by {author}" in css[:1500]
        assert url in css[:1500] and "MIT License" in css[:1500]
        assert url in js[:1500]

def test_home_reuses_existing_flask_and_preserves_bbc_provenance():
    import app as server
    with server.app.test_client() as client:
        result=client.get("/")
        assert result.status_code == 200
        html=result.get_data(as_text=True)
    assert "Authentic BBC intelligence dashboard" in html
    assert "Current BBC News headlines" in html
    assert "synthetic and English" in html or "synthetic teaching" in html
    for target in ("/static/studio_theme.css?v=1","/static/uiverse_components.css?v=1",
                   "/static/uiverse_components.js?v=1"):
        assert target in html
    assert html.index("uiverse_components.js") < html.index("script.js?v=4")
    for item in ("nb-explore","nb_torch_toggle","nb_dataset_switch","nb-loading-curtain","nb-summary-play"):
        assert f'id="{item}"' in html
    assert 'id="nb-summary-play" class="nb-wave-play" disabled' in html
    assert 'id="export_link"' in html and 'id="ml_consent"' in html

def test_existing_live_data_toggle_uses_real_source_and_includes_export():
    js=(STATIC/"dashboard.js").read_text(encoding="utf-8")
    assert "let activeSource = 'bbc'" in js
    assert "datasetToggle.checked ? 'demo':'bbc'" in js
    assert "/api/dashboard?source=" in js
    assert "/api/export/analytics.csv?source=" in js
    assert "snapshot.meta.synthetic" in js

def test_waveform_speech_control_requires_real_generated_summary():
    js=(STATIC/"uiverse_components.js").read_text(encoding="utf-8")
    assert "querySelector('.summary-text')" in js
    assert "window.SpeechSynthesisUtterance(phrase)" in js
    assert "audioButton.disabled = !speechSupported || !phrase" in js
    assert "speech.onend" in js and "speech.onerror" in js
    assert "setLoading" in js and "window.NewsBotUI" in js

def test_components_are_namespaced_and_support_reduced_motion():
    css=(STATIC/"uiverse_components.css").read_text(encoding="utf-8")
    for selector in (".nb-wave-player",".nb-space-btn",".nb-evidence-switch",
                     ".nb-torch",".nb-pl-dot",".nb-loading-curtain"):
        assert selector in css
    assert "@media(prefers-reduced-motion:reduce)" in css
    assert "focus-visible" in css
    assert "\n.btn{" not in css
    assert "\n.container{" not in css
    assert "\n.switch{" not in css

def test_fetch_processes_have_loading_cleanup():
    for script in ("script.js","multilingual.js","dashboard.js"):
        code=(STATIC/script).read_text(encoding="utf-8")
        assert "NewsBotUI?.setLoading" in code
        assert "finally" in code
