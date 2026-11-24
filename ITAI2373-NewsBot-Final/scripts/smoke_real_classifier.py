"""Run live-code BBC classifier integration checks after synthetic corpus build."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app

with app.test_client() as c:
    health = c.get('/health')
    assert health.status_code == 200, health.data
    assert health.get_json()['bbc_classifier_available'], health.get_json()
    sample = ("Parliament debated the national budget and new legislation today. "
              "Government officials met to discuss policy and political negotiations.")
    response = c.post('/api/analyze', json={'text':sample})
    assert response.status_code == 200, response.data
    result = response.get_json()
    assert result['classification']['model'] == 'BBC news TF IDF Logistic Regression'
    assert 'BBC News Train.csv' in result['model_source']
    assert 'SYNTHETIC' in result['corpus_source']
    dashboard = c.get('/api/dashboard')
    assert dashboard.status_code == 200, dashboard.data
    analytics = dashboard.get_json()
    assert analytics['meta']['synthetic'] is False
    assert analytics['meta']['articles'] == 1440
    assert sum(x['count'] for x in analytics['categories']) == 1440
    demo_response = c.get('/api/dashboard?source=demo')
    assert demo_response.status_code == 200
    assert demo_response.get_json()['meta']['synthetic'] is True
    assert demo_response.get_json()['meta']['articles'] == 60
    assert analytics['bbc_classifier']['active'] is True
    assert analytics['bbc_classifier']['articles_used'] == 1440
    assert abs(analytics['bbc_classifier']['heldout_accuracy'] - 0.9583333333) < 1e-5
    assert c.get('/api/export/analytics.csv').status_code == 200
    query = c.post('/api/query', json={'query':'Jessen Huang latest news'})
    assert query.status_code == 200
    assert query.get_json()['articles'] == []
print('BBC model API, provenance split, dashboard and query: PASSED')
