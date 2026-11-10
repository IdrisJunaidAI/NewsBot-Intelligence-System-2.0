# Deployment Guide

1. Install Python 3.11 and create an isolated environment.
2. Install `requirements.txt` and `python -m spacy download en_core_web_sm`.
3. Download approved BBC dataset, place at `data/raw/BBC News Train.csv`, then run `python train.py --csv "data/raw/BBC News Train.csv"`.
4. Run `pytest -q`; inspect `data/results/training_metrics.json` and conduct manual source verification.
5. Set a random `FLASK_SECRET_KEY` environment variable and run locally using `python app.py`.
6. Only for a controlled deployment, use an HTTPS reverse proxy, authentication, request limits, error logging, security reviews and privacy impact review. `gunicorn app:app` may be used on a supported production host after those controls. Never publish the raw BBC dataset, model secrets, or uncontrolled user text. Do not enable `debug=True` in production.

Model artifacts loaded through joblib must be generated locally or verified through trusted provenance. Optional translation sends data to an external provider; assess consent, licensing and data sensitivity first. The package does not claim a verified public deployment.

## Optional Flask hosting setup
The repository includes a Render configuration file (`render.yaml`) and `scripts/start_web.sh`. A host supporting Python 3.11 and Gunicorn can run the same script. On first start, an absent model triggers a **synthetic teaching demonstration** with 60 example articles. It does not train the final BBC model.

To deploy on a supported host, connect your GitHub repository in its dashboard, select `render.yaml` or configure the build command `pip install -r requirements.txt` and start command `bash scripts/start_web.sh`. Supply `FLASK_SECRET_KEY` securely. Verify `/health`, `/api/stats`, `/api/analyze`, and `/api/query`, and test browser behavior before sharing the URL. Public hosting is an optional bonus and is **not yet completed**. Investigate hosting availability, quota, latency and security controls.
