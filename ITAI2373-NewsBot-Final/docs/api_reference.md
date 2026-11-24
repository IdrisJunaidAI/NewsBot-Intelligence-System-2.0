# NewsBot 2.0 API Reference

**Public host:** https://newsbot-intelligence-system-2-p97f.onrender.com  
**Request type:** JSON over HTTPS. All untrusted input is validated by Flask routes.

| Method and route | Function | Provenance |
| --- | --- | --- |
| `GET /health` | Check HTTP server and model availability | Service state |
| `GET /api/dashboard` | Authentic historical BBC aggregate dashboard | Real BBC labeled Train; no full article text |
| `GET /api/dashboard?source=demo` | Teaching chart statistics | 60 synthetic articles |
| `GET /api/export/analytics.csv?source=bbc` | Aggregated BBC statistical export | No original article bodies |
| `GET /api/export/analytics.csv?source=demo` | Teaching aggregate export | Synthetic |
| `GET /api/bbc/headlines?channel=top` | BBC official RSS headlines and links | Current external third party RSS |
| `POST /api/analyze` | BBC trained single article category with separate tone, NER and summary | Pasted input plus historical model |
| `POST /api/query` | Intent and retrieval from the synthetic corpus | Synthetic fixed collection |
| `POST /api/clear` | Reset conversational filters | Session |
| `GET /api/multilingual/status` | List installed language capabilities | Runtime metadata |
| `POST /api/multilingual/detect` | Identify language | Student pasted text |
| `POST /api/multilingual/translate` | Translate with consent | External provider, privacy warning |
| `POST /api/multilingual/search` | Translation assisted LSA or optional neural mode | Synthetic corpus |
| `POST /api/retrieval/compare` | TF IDF and LSA comparison | Synthetic corpus |

### Request examples

`POST /api/analyze` body: `{"text":"Parliament and technology companies announced a new regulation for the sector ..."}`. Article must have at least 30 characters. Outputs include category, model probability, human review flag, detected language, sentiment, summary, named entities, topics and source provenance. Probabilities are not calibrated.

`POST /api/query` body: `{"query":"Show technology articles"}`. The response explicitly names its synthetic search method and article IDs.

`POST /api/multilingual/translate` body: `{"text":"Bonjour ...","source":"fr","target":"en","external_consent":true}`. The external provider receives content only with explicit consent.

### Error handling

400 for invalid required text or unsupported RSS categories. 422 for unavailable methods that cannot be attempted without consent. 503 when an optional model/provider is unavailable. The BBC RSS adapter caches results for up to 600 seconds, limits results to 10 official BBC links and never requests full BBC article pages.

### Dataset rights

The published BBC aggregate JSON and CSV are derived statistical findings. They do not grant a license to reuse original BBC full texts. Use official publisher links for reading the original articles.


### `POST /api/batch/analyze` (frontend bonus)

Body: `{"articles":["A news excerpt of at least thirty characters ...","Another independent excerpt of at least thirty characters ..."]}`. Accepts **2 to 5** strings, each 30–5000 characters and a maximum of 15000 total. Success (200) returns `{"processed":2,"results":[{"article_number":1,"category":"...","model_probability":0.7,"sentiment":"...","language":"en","summary":"...","needs_human_review":false,"classifier_source":"..."}],"disclaimer":"..."}`. The values shown here are **shape examples, not actual model predictions**. Invalid input yields 400; unavailable model yields 503. No original input text is echoed, although extractive summaries reuse supplied sentences. Cache control: no-store.

### `GET /api/research/fewshot` (research bonus)

Returns the committed **measured** historical BBC low-data experiment data: five sample sizes, five random-seed repetitions, aggregated mean and sample standard deviation for holdout macro F1 and accuracy, provenance, limitations, and experiment count. Reads `data/results/fewshot_learning_curve.csv`; no raw article bodies or input text are served. Missing or corrupt evidence produces 503 rather than invented scores. `data/results/fewshot_learning_curve.csv` is the source of truth.
