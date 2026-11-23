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
    assert b'News analytics dashboard' in homepage.data
    assert b'dashboard.js' in homepage.data
    response = client.get('/api/dashboard')
    assert response.status_code == 200
    assert response.get_json()['meta']['articles'] == 60
    assert client.get('/api/dashboard').get_json() == response.get_json()
    csv_response = client.get('/api/export/analytics.csv')
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
