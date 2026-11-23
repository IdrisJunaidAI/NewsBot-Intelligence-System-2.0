"""Flask interface for the bounded NewsBot teaching corpus."""
import csv
import io
import os

import joblib
from flask import Flask, Response, jsonify, render_template, request, session

from config.settings import Settings
from src.utils.dashboard import dashboard_snapshot

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32).hex())
app.config.update(
    MAX_CONTENT_LENGTH=64 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=bool(os.environ.get('RENDER')),
)
_model = None
_dashboard_cache = {'model': None, 'snapshot': None}


def get_model():
    global _model
    if _model is None:
        path = Settings().model_path
        if not path.exists():
            raise RuntimeError('Train a model first with python train.py --csv "BBC News Train.csv"')
        # Deserializing a joblib file can execute code. Load only trusted, locally trained artifacts.
        _model = joblib.load(path)
    return _model


def get_dashboard():
    """Reuse expensive summary computation while the in-memory corpus is unchanged."""
    model = get_model()
    if _dashboard_cache['model'] is not model:
        snapshot = dashboard_snapshot(model)
        _dashboard_cache['model'] = model
        _dashboard_cache['snapshot'] = snapshot
    return _dashboard_cache['snapshot']


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'component': 'web', 'model_ready': Settings().model_path.exists()})


@app.post('/api/analyze')
def analyze():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(get_model().analyze(payload.get('text', '')))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


@app.post('/api/query')
def query():
    payload = request.get_json(silent=True) or {}
    try:
        answer = get_model().ask(payload.get('query', ''), context=session.get('conversation_context', {}))
        session['conversation_context'] = answer.get('context', {})
        return jsonify(answer)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


@app.get('/api/stats')
def stats():
    try:
        return jsonify(get_model().corpus_stats())
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


@app.get('/api/dashboard')
def dashboard():
    try:
        return jsonify(get_dashboard())
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


def _csv_cell(value):
    """Prevent spreadsheet formula execution in an exported aggregate report."""
    text = str(value if value is not None else '')
    if text.lstrip().startswith(('=', '+', '-', '@')):
        return "'" + text
    return text


@app.get('/api/export/analytics.csv')
def export_analytics():
    try:
        data = get_dashboard()
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['section', 'label', 'count', 'percentage', 'details'])
    for kind in ('categories', 'sentiments'):
        for item in data[kind]:
            writer.writerow([kind, _csv_cell(item['label']), item['count'], item['percentage'], ''])
    for method, topics in data['topics'].items():
        for item in topics:
            writer.writerow(['topic_' + method, 'Topic ' + str(item['id'] + 1),
                             item['articles'], '', _csv_cell(', '.join(item['keywords']))])
    for item in data['timeline']:
        writer.writerow(['recorded_month', _csv_cell(item['period']), item['articles'], '', ''])
    for key in ('holdout_accuracy', 'holdout_macro_f1', 'holdout_count'):
        writer.writerow(['evaluation', key, '', '', data['evaluation'][key]])
    writer.writerow(['provenance', 'source', '', '', _csv_cell(data['meta']['source'])])
    writer.writerow(['provenance', 'synthetic', '', '', data['meta']['synthetic']])
    writer.writerow(['provenance', 'disclaimer', '', '', data['meta']['disclaimer']])
    return Response(buffer.getvalue(), mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename="newsbot_corpus_analytics.csv"',
        'Cache-Control': 'no-store'
    })


@app.post('/api/clear')
def clear():
    session.pop('conversation_context', None)
    return jsonify({'cleared': True})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', 5000)), debug=False)
