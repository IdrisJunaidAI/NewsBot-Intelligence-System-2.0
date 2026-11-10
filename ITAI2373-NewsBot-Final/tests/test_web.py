"""Browser API smoke tests using Flask test client, without external web requests."""
import pytest

flask = pytest.importorskip('flask')
from app import app
from src.system import NewsBotSystem
from config.settings import Settings

@pytest.fixture(scope='module')
def client():
    model=NewsBotSystem().fit_csv(Settings().demo_path,'synthetic web smoke tests')
    import app as application
    application._model=model
    application.app.config.update(TESTING=True)
    yield application.app.test_client()
    application._model=None

def test_home_and_health(client):
    assert client.get('/').status_code == 200
    assert client.get('/health').get_json()['status'] == 'ok'

def test_analyze_api(client):
    resp=client.post('/api/analyze', json={'text':'Researchers unveiled a technology platform and new robotics system for industrial applications.'})
    assert resp.status_code == 200
    assert resp.get_json()['classification']['category']

def test_invalid_short_text(client):
    resp=client.post('/api/analyze', json={'text':'short'})
    assert resp.status_code == 400

def test_conversation_and_reset(client):
    resp=client.post('/api/query', json={'query':'How many technology articles?'})
    assert resp.status_code == 200
    assert resp.get_json()['context']['category']=='technology'
    assert client.post('/api/clear', json={}).status_code==200
