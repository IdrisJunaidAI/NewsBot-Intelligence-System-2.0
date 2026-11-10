"""Flask web interface. Install requirements and train.py before serving."""
from pathlib import Path
import os
import joblib
from flask import Flask,render_template,request,jsonify,session
from config.settings import Settings

app=Flask(__name__)
app.secret_key=os.environ.get('FLASK_SECRET_KEY',os.urandom(32).hex())
app.config.update(MAX_CONTENT_LENGTH=64*1024,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax')
_model=None

def get_model():
    global _model
    if _model is None:
        path=Settings().model_path
        if not path.exists():raise RuntimeError('Train a model first: python train.py --csv "BBC News Train.csv"')
        # joblib/pickle files are executable: load only models YOU trained and trust.
        _model=joblib.load(path)
    return _model

@app.get('/')
def home():return render_template('index.html')

@app.get('/health')
def health():
    return jsonify({'status':'ok','component':'web','model_ready':Settings().model_path.exists()})

@app.post('/api/analyze')
def analyze():
    payload=request.get_json(silent=True) or {}
    try:return jsonify(get_model().analyze(payload.get('text','')))
    except ValueError as exc:return jsonify({'error':str(exc)}),400
    except RuntimeError as exc:return jsonify({'error':str(exc)}),503

@app.post('/api/query')
def query():
    payload=request.get_json(silent=True) or {}
    try:
        answer=get_model().ask(payload.get('query',''),context=session.get('conversation_context',{}))
        session['conversation_context']=answer.get('context',{})
        return jsonify(answer)
    except ValueError as exc:return jsonify({'error':str(exc)}),400
    except RuntimeError as exc:return jsonify({'error':str(exc)}),503

@app.get('/api/stats')
def stats():
    try:return jsonify(get_model().corpus_stats())
    except RuntimeError as exc:return jsonify({'error':str(exc)}),503

@app.post('/api/clear')
def clear():
    session.pop('conversation_context',None)
    return jsonify({'cleared':True})

if __name__=='__main__':
    app.run(host='127.0.0.1',port=int(os.getenv('PORT',5000)),debug=False)
