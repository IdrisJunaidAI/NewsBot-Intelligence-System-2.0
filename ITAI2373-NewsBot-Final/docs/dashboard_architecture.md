# NewsBot 2.0 Analytics Dashboard Architecture

## Scope and terminology

This dashboard summarizes only the **currently loaded article collection**. It is not connected to a live news provider and its corpus may be entirely synthetic. Every chart includes provenance and an explicit label for training corpus origin. This deliberately avoids confusing model validation with journalistic fact verification.

## Dataflow

1. The existing `train.py` script trains `NewsBotSystem` using the selected CSV file and produces a trusted local `data/models/newsbot2.joblib` artifact.
2. The Flask application (`app.py`) loads that artifact using `get_model()` and exposes a cached snapshot through `GET /api/dashboard`.
3. `src/utils/dashboard.py` calculates category frequencies, VADER sentiment distribution, strongest topic assignments for both LDA and NMF, recorded month frequencies, dataset metadata coverage, and the classifier evaluation saved during training.
4. `static/dashboard.js` renders responsive, accessible visualizations directly from the API, without third party JavaScript, remote API calls, or the unsafe insertion of article text as HTML.
5. `GET /api/export/analytics.csv` exports a metadata and aggregation report with spreadsheet formula injection safeguards. It does not export raw article text.

## API contracts

`GET /api/dashboard`

The JSON response contains `meta`, `categories`, `sentiments`, `topics.LDA`, `topics.NMF`, `timeline`, `evaluation`, and `chart_notes`. Each category or sentiment item includes a `label`, `count`, and `percentage`. The topic objects include statistical keywords and how many articles are assigned to the highest weighted topic.

`GET /api/export/analytics.csv`

Returns aggregate charts and validation statistics in five columns: `section`, `label`, `count`, `percentage`, and `details`. The export includes model source provenance and whether the dataset is synthetic.

## Evaluation integrity

* Values in the model comparison list come from cross validation on the training portion and are not generalizable to future news.
* Held out accuracy and macro F1 are historical measurements stored by the actual training process. The dashboard never fabricates evaluation scores.
* The synthetic 60 article teaching corpus is not suitable for claims about BBC news classification accuracy.
* Topic assignments are statistical clusters rather than verified descriptions of emerging external events.
* Sentiment labels are VADER text tone classifications, not human emotion or article credibility assessment.
* The date chart reports only dates present in the source file, with no inferred publication dates.
* Language detection and translation are separate system features; the dashboard does not imply multilingual transformer search is enabled.

## Testing

Run `python -m pytest -q` from the project root. Tests check category and sentiment totals, topic distribution totals, synthesis provenance, model holdout metadata, `GET /api/dashboard`, CSV export, and the BBC shaped CSV preflight check. GitHub Actions also runs `node --check` for frontend JavaScript syntax.

## Deployment

The existing Render Free blueprint builds from `main` and uses synthetic training data. The new dashboard adds no paid resources or external integrations. Release from a tested pull request and inspect the Render deployment health endpoint after merging.
