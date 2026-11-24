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
