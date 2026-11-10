# NewsBot Intelligence System 2.0

## ITAI 2373 Final Project | Individual Portfolio Development Copy

**Student:** Idris O. Junaid  
**Source midterm repository:** https://github.com/IdrisJunaidAI/ITAI2373_NewsBot_Midterm  
**Status:** Reproducible draft implementation with Flask frontend and deployment blueprint, not a verified publicly accessible production deployment.  
**Training corpus:** Instructor-approved BBC News Classification (`BBC News Train.csv`) must be supplied by the user.  
**Disclaimer:** The included `demo_articles.csv` contains exactly 60 synthetic articles authored as teaching examples and may not support externally valid evaluation.

### Research purpose
NewsBot 2.0 connects advanced classification, latent topic models, sentiment, named entities, summarization, article retrieval, language detection, optional translation and a conversational web interface. NewsBot is a research prototype, not a news verification service or medical, regulatory, or financial decision engine.

### From midterm to final
The October 2026 midterm notebook reported a Linear SVM held-out accuracy of **96.53%** and macro F1 of **96.45%** on its BBC sample of **1,440** articles, based on the student-submitted execution reports. Those are **midterm metrics only**. This project deliberately defaults to a Logistic Regression model to expose model probabilities, while retaining Linear SVM and Naive Bayes for a separate CV comparison. Report new model results only after re-running with the BBC CSV and inspect class-specific performance.

### Quick start
Python 3.11 recommended. In a new clean environment:

```bash
python -m venv .venv
# Activate your environment before installing packages
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python train.py --csv "data/raw/BBC News Train.csv"
pytest -q
python app.py
```

Then visit `http://127.0.0.1:5000`.

For a clearly labeled local demonstration only, substitute `python train.py --demo`. Demonstration results **must never** be reported as BBC performance.

### Optional advanced capabilities

```bash
pip install sentence-transformers deep-translator
python train.py --csv "data/raw/BBC News Train.csv" --embeddings
```

The semantic search component uses multilingual embeddings only when explicitly requested and successfully installed. Otherwise, it uses TF IDF lexical retrieval and labels this limitation in every response. Translation requires a network service and must not be represented as available offline. Named entity recognition requires `en_core_web_sm`; no entities are fabricated when the model is missing. Historical BBC data has no reliable article date, so topic evolution and time-based filters are unavailable unless a suitable dated corpus is provided.

### System components

| Module | Implementation |
| --- | --- |
| Data quality | Schema mapping, cleaning, duplicate check, date provenance |
| Classification | Leakage-aware 80/20 split, CV comparisons, logistic probabilities |
| Topic discovery | LDA and NMF with inspectable words, temporal aggregation when dated |
| Tone and entities | VADER, spaCy entities and clearly labeled cooccurrence |
| Understanding | Extractive article summary and retrieval |
| Multilingual | Language detection, optional translation and multilingual embeddings |
| Conversation | Intent routing, corpus filtering, multi-turn filter context, article IDs |
| Web interface | Flask dashboard with `/api/analyze`, `/api/query`, `/api/stats` |

### Reproducibility and governance
Keep raw BBC source in `data/raw/` and do not push licensed data or secrets publicly. The application loads only trusted local `joblib` models. User-entered articles may contain sensitive information and are **not** sent to external providers unless the user intentionally enables an optional network translator. Review generated interpretation, sentiment and entity links manually. Set `FLASK_SECRET_KEY` for deployment and place Flask behind an HTTPS reverse proxy. This is not a hardened, audited public service.

### Submission and individual contributions
The `docs/individual_contributions.md` file differentiates verified midterm activities from unverified future final work. This project package was assembled with AI coding assistance for review and testing; attribution should be retained and the student/team must inspect, modify, run, and understand it before submission. The instructor requires each student's repository and the team's reflective journal with real contributions. Names and group responsibilities must be verified before finalizing report filenames.

### File map
`src/` reusable modules; `config/` settings; `notebooks/` guided execution; `tests/` automated tests; `data/` example data and outputs; `docs/` developer and user guides; `reports/` draft PDF reports and PowerPoint.

### Important limitations
1. The real BBC training CSV and fitted model were **not** attached to the final-project upload.
2. Standalone deployment and external translation require network access and installation not available during initial package assembly.
3. The 60 sample article teaching set is synthetic; no new final-model claims are made about actual publisher accuracy.
4. The optional 20-point research bonus in the rubric lists specific extensions such as few-shot learning and live processing. The default system does not assert completion of those extensions.

### References
Kaggle BBC News Classification: https://www.kaggle.com/competitions/learn-ai-bbc/data  
scikit-learn: https://scikit-learn.org/stable/  
spaCy: https://spacy.io/  
VADER: Hutto & Gilbert (2014), ICWSM  
Instructor final project guide and web application guide, supplied course materials.

### Frontend and optional hosting blueprint

The responsive Flask app consists of `app.py`, `templates/index.html`, `static/style.css` and `static/script.js`. It exposes a dashboard, article analysis, natural language queries and health checks. `render.yaml`, `Procfile` and `scripts/start_web.sh` provide an optional hosting entry point. Hosting has **not** been performed or verified.

The startup script trains from the included **synthetic demonstration** corpus if no model is present; this allows the web application to be viewed but cannot validate scientific performance. Before presenting as a research deployment, train on approved BBC news data and confirm model dependencies and provenance. Do not commit the BBC raw dataset or untrusted model artifacts. Full model loading in hosted environments requires validation of compute, memory, package versions and application security. The hosting provider may charge fees and its current deployment options must be confirmed.

Continuous integration tests run on GitHub Actions using `.github/workflows/ci.yml`, including Flask route tests. The source package is self contained for code review; enabling optional language models requires additional installation and internet connectivity.
