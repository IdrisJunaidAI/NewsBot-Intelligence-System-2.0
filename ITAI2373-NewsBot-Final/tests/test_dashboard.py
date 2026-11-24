"""Regression coverage for documented corpus analytics and structured report export."""
import csv
import io

import pytest

from config.settings import Settings
from src.system import NewsBotSystem
from src.utils.dashboard import dashboard_snapshot
from scripts.validate_bbc_csv import audit_dataset


@pytest.fixture(scope='module')
def demo():
    return NewsBotSystem().fit_csv(Settings().demo_path, 'DEMO SYNTHETIC DATA ONLY')


def test_dashboard_counts_and_provenance(demo):
    report = dashboard_snapshot(demo)
    assert report['meta']['synthetic'] is True
    assert report['meta']['articles'] == 60
    assert report['meta']['category_count'] == 5
    assert report['meta']['has_live_news'] is False
    assert sum(x['count'] for x in report['categories']) == 60
    assert sum(x['count'] for x in report['sentiments']) == 60
    assert sum(x['articles'] for x in report['topics']['NMF']) == 60
    assert sum(x['articles'] for x in report['topics']['LDA']) == 60
    assert report['evaluation']['holdout_count'] == 12
    assert report['evaluation']['source'] == 'DEMO SYNTHETIC DATA ONLY'


def test_dashboard_web_and_csv(demo, monkeypatch):
    import app as server
    monkeypatch.setattr(server, '_model', demo)
    monkeypatch.setattr(server, '_dashboard_cache', {'model': None, 'snapshot': None})
    server.app.config['TESTING'] = True
    client = server.app.test_client()
    homepage = client.get('/')
    assert homepage.status_code == 200
    assert b'Authentic BBC intelligence dashboard' in homepage.data
    assert b'dashboard.js' in homepage.data
    response = client.get('/api/dashboard?source=demo')
    assert response.status_code == 200
    assert response.get_json()['meta']['articles'] == 60
    assert client.get('/api/dashboard?source=demo').get_json() == response.get_json()
    csv_response = client.get('/api/export/analytics.csv?source=demo')
    assert csv_response.status_code == 200
    assert csv_response.mimetype == 'text/csv'
    rows = list(csv.DictReader(io.StringIO(csv_response.get_data(as_text=True))))
    assert any(row['section'] == 'provenance' and row['label'] == 'synthetic' for row in rows)
    assert any(row['section'] == 'categories' and row['count'] == '12' for row in rows)
    assert not any('The software developer introduced' in str(row) for row in rows)


def test_bbc_schema_preflight_without_real_bbc(tmp_path):
    """A compatible fake schema tests the importer without inventing BBC results."""
    import pandas as pd
    rows = []
    for category in ('tech', 'business', 'sport', 'politics', 'entertainment'):
        for i in range(5):
            rows.append({'Text': f'{category} news story number {i}. '
                          f'This is a complete article text with a unique marker {i} and subject {category}.',
                         'Category': category})
    path = tmp_path / 'fixture_not_real_bbc.csv'
    pd.DataFrame(rows).to_csv(path, index=False)
    report = audit_dataset(path)
    assert report['retained_rows'] == 25
    assert report['all_five_bbc_categories'] is True
    assert len(report['file_sha256']) == 64
    assert report['removed_rows'] == 0
    assert 'model' not in report

def test_authentic_bbc_dashboard_is_default_without_full_text(demo, monkeypatch):
    import app as server
    monkeypatch.setattr(server, '_model', demo)
    with server.app.test_client() as client:
        response = client.get('/api/dashboard')
        assert response.status_code == 200
        data = response.get_json()
        assert data['meta']['articles'] == 1440
        assert data['meta']['synthetic'] is False
        assert data['meta']['dated_articles'] == 0
        assert data['meta']['article_text_public'] is False
        assert sum(x['count'] for x in data['categories']) == 1440
        assert sum(x['articles'] for x in data['topics']['NMF']) == 1440
        assert sum(x['articles'] for x in data['topics']['LDA']) == 1440
        assert abs(data['evaluation']['holdout_accuracy'] - 0.95833333333) < .0001
        raw = response.get_data(as_text=True)
        assert 'The software developer introduced' not in raw
        assert client.get('/api/dashboard?source=unknown').status_code == 400
        exported = client.get('/api/export/analytics.csv')
        assert exported.status_code == 200
        assert '1440' not in exported.get_data(as_text=True) or 'evaluation' in exported.get_data(as_text=True)


def test_bbc_rss_parser_is_attributed_and_sanitized():
    from src.utils.bbc_feed import parse_bbc_rss
    xml = b"""<rss><channel>
      <item><title>BBC sample title</title><link>https://www.bbc.com/news/articles/example123</link>
      <pubDate>Mon, 23 Nov 2026 18:00:00 GMT</pubDate></item>
      <item><title>Phishing link</title><link>https://example.net/steal</link></item>
      </channel></rss>"""
    record = parse_bbc_rss(xml, 'top')
    assert record['attribution'] == 'BBC News'
    assert record['articles'][0]['title'] == 'BBC sample title'
    assert len(record['articles']) == 1
    assert not any(item['url'].startswith('https://example.net') for item in record['articles'])
