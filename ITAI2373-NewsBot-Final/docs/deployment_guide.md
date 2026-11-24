# Individual Portfolio Deployment Guide

NewsBot is deployed as a **Render Free** Python web service with the GitHub `main` branch. The site URL is https://newsbot-intelligence-system-2-p97f.onrender.com and the service uses Flask with Gunicorn.

The build installs Python dependencies and trains a small synthetic demonstration search model because public redistributing full BBC publisher text is not assumed. The article category classifier loads a separate safe, non executable BBC trained JSON.GZ weights release. The default dashboard reads `data/results/bbc_public_analytics.json` built from the authentic historical BBC Train CSV, without full text. The 60 item teaching search corpus is optional and explicitly labeled. Real current BBC headline links come from official attributed RSS with a bounded cache.

## Commands

`python -m pip install -r requirements.txt`  
`python train.py --demo`  
`python scripts/smoke_real_classifier.py`  
`python -m pytest -q`  
`gunicorn app:app`

## Configuration

`FLASK_SECRET_KEY` generated securely by Render; `PYTHON_VERSION` set in `render.yaml`. No API secrets or full article text are committed. The public website is still a limited academic prototype, not an audited news service. Apply rate limiting, observability, provider license review, accessibility testing and production security controls before commercial use.

## Health and deployment checks

Check `/health`, `/api/dashboard` for 1440 real records, `/api/dashboard?source=demo` for 60 teaching records, and `/api/bbc/headlines` for optional RSS headlines. RSS failure must be handled gracefully. Validate `POST /api/analyze` returns BBC category model provenance and `POST /api/query` states that the search corpus is synthetic.

## Data rights

Do not upload `BBC News Train.csv` or other original BBC news article bodies to the public repository by default. Official RSS titles and links should maintain BBC News attribution and comply with relevant publisher conditions. Business use needs separate rights review.
