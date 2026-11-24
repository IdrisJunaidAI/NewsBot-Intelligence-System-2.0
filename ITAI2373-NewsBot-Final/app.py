"""Flask interface for the bounded NewsBot teaching corpus."""
import csv
import io
import os
import json
from pathlib import Path

import joblib
from flask import Flask, Response, jsonify, render_template, request, session

from config.settings import Settings
from src.analysis.bbc_classifier import BBCWeightedClassifier
from src.utils.dashboard import dashboard_snapshot
from src.utils.bbc_feed import get_bbc_headlines
from src.multilingual.offline_query import offline_news_query
from src.utils.batch_analysis import analyze_articles
from src.utils.research_bonus import learning_curve_report

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32).hex())
app.config.update(
    MAX_CONTENT_LENGTH=64 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=bool(os.environ.get('RENDER')),
)
BBC_WEIGHTS_PATH = Path(__file__).resolve().parent / 'data' / 'released_models' / 'bbc_classifier_weights.json.gz'
BBC_EVALUATION_PATH = Path(__file__).resolve().parent / 'data' / 'results' / 'bbc_evaluation.json'
BBC_PUBLIC_DASHBOARD = Path(__file__).resolve().parent / 'data' / 'results' / 'bbc_public_analytics.json'
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
        if BBC_WEIGHTS_PATH.is_file():
            _model.bbc_classifier = BBCWeightedClassifier(BBC_WEIGHTS_PATH)
    return _model


def get_dashboard(source='bbc'):
    """BBC authentic aggregate evidence by default; synthetic demo is opt-in.

    The published BBC aggregate file contains no original article text.
    """
    if source == 'bbc':
        if not BBC_PUBLIC_DASHBOARD.is_file():
            raise RuntimeError('Verified BBC aggregate report is not installed')
        with BBC_PUBLIC_DASHBOARD.open(encoding='utf-8') as handle:
            return json.load(handle)
    if source != 'demo':
        raise ValueError('Choose bbc or demo')
    model = get_model()
    if _dashboard_cache['model'] is not model:
        snapshot = dashboard_snapshot(model)
        bbc=getattr(model,'bbc_classifier',None)
        if bbc is not None and BBC_EVALUATION_PATH.is_file():
            with BBC_EVALUATION_PATH.open(encoding='utf8') as handle:
                record=json.load(handle)
            logistic=record['logistic_regression']['metrics']
            svm=record['linear_svm']['metrics']
            snapshot['bbc_classifier'] = {
                'active': True,
                'model': 'TF IDF Logistic Regression',
                'articles_used': bbc.provenance['articles_used'],
                'heldout_count': record['provenance']['heldout_partition_rows'],
                'heldout_accuracy': logistic['holdout_accuracy'],
                'heldout_macro_f1': logistic['holdout_macro_f1'],
                'comparison_svm_accuracy': svm['holdout_accuracy'],
                'comparison_svm_macro_f1': svm['holdout_macro_f1'],
                'evaluation_source': 'Real BBC labeled training subset, not the synthetic dashboard dataset',
                'note': 'Only article classification uses this authentic BBC model. Corpus charts and search remain 60 synthetic articles.'
            }
        _dashboard_cache['model'] = model
        _dashboard_cache['snapshot'] = snapshot
    return _dashboard_cache['snapshot']


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'component': 'web', 'model_ready': Settings().model_path.exists(),
                    'bbc_classifier_available': BBC_WEIGHTS_PATH.is_file(),
                    'bbc_aggregate_available': BBC_PUBLIC_DASHBOARD.is_file()})


@app.post('/api/analyze')
def analyze():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(get_model().analyze(payload.get('text', '')))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


@app.get('/api/research/fewshot')
def fewshot_research():
    """Show committed real BBC reduced-training-size results, never raw articles."""
    try:
        response = jsonify(learning_curve_report())
        response.headers['Cache-Control'] = 'public, max-age=300'
        return response
    except (OSError, ValueError) as exc:
        app.logger.warning('Few-shot result evidence unavailable: %s', type(exc).__name__)
        return jsonify({'error': 'Research evidence temporarily unavailable'}), 503


@app.post('/api/batch/analyze')
def batch_analyze():
    """Analyze 2–5 user supplied excerpts without persistence."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({'error': 'Provide a JSON object containing an articles array'}), 400
    try:
        data = analyze_articles(get_model(), payload.get('articles'))
        response = jsonify(data)
        response.headers['Cache-Control'] = 'no-store'
        return response
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        app.logger.warning('Batch analysis unavailable: %s', type(exc).__name__)
        return jsonify({'error': 'Article analysis model temporarily unavailable'}), 503


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
        return jsonify(get_dashboard(request.args.get('source', 'bbc')))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
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
        data = get_dashboard(request.args.get('source', 'bbc'))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
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



@app.get('/api/multilingual/status')
def multilingual_status():
    try:
        bot = get_model()
        return jsonify({
            'supported_languages': ['en', 'es', 'fr'],
            'translation': bot.translator.status(),
            'lsa_active': bool(bot.search.lsa_available),
            'offline_topic_search_available': True,
            'offline_topic_search_languages': ['en', 'es', 'fr'],
            'offline_topic_search_note': 'Local curated term mapping, not full machine translation or multilingual transformer inference.',
            'multilingual_embeddings_active': bot.search.method == 'multilingual sentence embeddings',
            'semantic_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'news_source': bot.source, 'live_news': False,
            'note': 'BBC classification and synthetic corpus retrieval are separate sources.'
        })
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


@app.post('/api/multilingual/detect')
def multilingual_detect():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(get_model().languages.detect(payload.get('text','')))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


@app.post('/api/multilingual/translate')
def multilingual_translate():
    payload = request.get_json(silent=True) or {}
    try:
        result = get_model().translator.translate(
            payload.get('text',''), source=payload.get('source','auto'),
            target=payload.get('target','en'),
            external_consent=payload.get('external_consent') is True)
        return jsonify(result), (200 if result['available'] else (503 if result.get('external_service_used') else 422))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


@app.post('/api/multilingual/search')
def multilingual_search():
    payload = request.get_json(silent=True) or {}
    try:
        result = get_model().multilingual.compare(
            payload.get('query',''), mode=payload.get('mode','semantic'),
            external_consent=payload.get('external_consent') is True)
        return jsonify(result), (200 if result['available'] else (503 if result.get('external_service_used') or payload.get('mode')=='semantic' else 422))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503


@app.post('/api/retrieval/compare')
def retrieval_compare():
    payload = request.get_json(silent=True) or {}
    try:
        system = get_model()
        search = system.search
        query = payload.get('query','')
        if not isinstance(query,str) or not query.strip():
            raise ValueError('A nonempty search query is required')
        detection = system.languages.detect(query)
        language = detection['language']
        if language in ('es','fr'):
            mapping = offline_news_query(query,language)
            if not mapping['available']:
                return jsonify({'error':mapping['reason'],'language':detection}),422
            query_en = mapping['query_en']
            mapping_note = mapping['note']
        else:
            query_en = query
            mapping_note = 'Direct English query; no external translation used'
        return jsonify({
            'lexical': search.search(query_en,top_k=5,mode='lexical'),
            'lsa': search.search(query_en,top_k=5,mode='lsa'),
            'language': detection,
            'normalized_query': query_en,
            'mapping_note': mapping_note,
            'external_service_used': False,
            'source':'Stored corpus contains 60 synthetic articles, not authentic BBC current news'
        })
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503



@app.get('/api/bbc/headlines')
def bbc_headlines():
    """Official BBC RSS titles and links only, for educational personal use."""
    channel = request.args.get('channel', 'top')
    if channel not in ('top', 'technology', 'business', 'world', 'science'):
        return jsonify({'error': 'Unsupported BBC feed channel'}), 400
    try:
        return jsonify(get_bbc_headlines(channel))
    except (OSError, ValueError, RuntimeError) as exc:
        return jsonify({'error': 'Live RSS unavailable; open the official BBC News feed directly',
                        'feed': 'https://feeds.bbci.co.uk/news/rss.xml',
                        'detail': type(exc).__name__}), 503


@app.post('/api/clear')
def clear():
    session.pop('conversation_context', None)
    return jsonify({'cleared': True})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', 5000)), debug=False)
