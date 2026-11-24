# Phase 1: Multilingual Intelligence and Semantic Retrieval

## Scope and source integrity

This module extends NewsBot 2.0 with English, Spanish and French language detection and optional consent based translation. The default public Render Free instance offers **Latent Semantic Analysis (LSA)** as an affordable semantic indexing method and retains a TF IDF lexical comparison. It does **not** run the larger multilingual transformer encoder on the Free instance. Genuine shared vector cross language retrieval is implemented as an optional Python/Colab runtime using the public Sentence Transformers multilingual MiniLM model.

The searchable collection remains 60 synthetic demonstration articles. Single article category classification separately uses a genuine BBC trained Logistic Regression model. There is no live news ingestion and no culturally representative or multilingual BBC publisher corpus.

## Definitions and accuracy of claims

| Method | Function | Claim boundary |
| --- | --- | --- |
| Language detection | `langdetect` or fallback heuristic | Short and mixed language text can be misidentified |
| External machine translation | `deep-translator` GoogleTranslator | Text sent to third party with explicit consent; quality and uptime unverified |
| TF IDF | Lexical matching | Not semantic or cross language |
| LSA | TF IDF, Truncated SVD and cosine similarity | Statistical latent semantic indexing within English content; not neural embeddings |
| Translation assisted retrieval | Translate Spanish/French query to English then use LSA | Language access depends on translation quality; not direct shared vector retrieval |
| Multilingual Sentence Transformers | 384 dimensional multilingual MiniLM vectors | True cross language semantic retrieval when model is installed, loaded and tested in an adequate environment |

## Local setup

Install the default requirements and run normal training. To use the deployed English LSA, no model download is necessary.

```bash
pip install -r requirements.txt
python train.py --demo
python app.py
python -m pytest -q
```

For authentic cross language dense search use a higher resource machine or Google Colab:

```bash
pip install 'sentence-transformers>=3,<6'
python train.py --demo --embeddings
python app.py
```

The encoder `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` downloads from Hugging Face on first run, and network access and memory are required. Review model licensing and provider terms before distributing.

A complete independent Google Colab notebook is in `notebooks/08_Multilingual_Semantic_Search.ipynb`, including paired English, Spanish and French retrieval queries and a reproducible comparison to the lexical baseline. Do not report accuracy until the model has been run and the results logged.

## Web API

`GET /api/multilingual/status` discloses installed capabilities. `POST /api/multilingual/detect` takes `{"text":"..."}`. `POST /api/multilingual/translate` takes `{"text":"...","source":"auto","target":"en","external_consent":true}`. `POST /api/multilingual/search` takes `{"query":"...","mode":"semantic"}` or `{"query":"...","mode":"translated","external_consent":true}`. `POST /api/retrieval/compare` compares lexical and LSA rankings for an English query. Responses include the actual method and availability/error statements. A 503 response means an optional method is not active, not a successful fallback.

## Privacy and quality limitations

The model does not translate or send data to external providers without explicit consent in that request. Translation may alter names, idioms, negation, technical vocabulary, and culturally specific meaning. The system does not independently verify translations or sentiment across languages. The on premise dense embedding mode computes locally after model download and sends no submitted article text to a translation provider when `mode=semantic`.

The instructor's final project rubric calls for cultural context and comparison of coverage across different language sources. That requirement **cannot be verified with this BBC English only corpus and synthetic demonstration articles**. Genuine multilingual publisher sources and a manually annotated evaluation set will be necessary for research quality cultural perspective analysis.

## Verification plan

1. Test deterministic language detection with English, Spanish and French examples.
2. Test that translation refuses external transmission without explicit consent.
3. Test that identity translation uses no provider.
4. Test LSA and TF IDF rankings and zero overlap input.
5. Test explicit rejection when optional multilingual encoder is absent.
6. Run the Colab notebook with the real pretrained encoder and record Recall@1, Recall@3 and per language behavior.
7. In the deployed Flask app validate capability status, endpoint errors and the two distinct data source labels.

**References:** The instructor's ITAI 2373 final project rubric, the Student Guidance Notebook, Sentence Transformers official documentation, multilingual MiniLM model card and the `deep-translator` usage documentation. External model behavior should be validated empirically before claiming numerical performance.


## Executed Colab benchmark, November 23 2026

The original template notebook was subsequently executed by the student and its saved outputs were supplied for review. The real pretrained multilingual MiniLM model loaded successfully with 384 dimensional embeddings. On **six synthetic English passages and six constructed queries per language**, recorded Recall@1 and Recall@3 were both 100% for English, Spanish and French (18/18 first rank hits). The TF IDF baseline returned Recall@1 of 100%, 50%, and 33.3%, and Recall@3 of 100%, 66.7%, and 50%, respectively. The language detector agreed on all 18 test examples.

**Scope restriction:** These results are a small controlled benchmark, not validation on authentic multilingual BBC news, independent publishers or cultural perspective analysis. LSA was not included in this Colab comparison. Translation was **not executed** because the consent switch remained false. The hosted Free Render system still uses LSA, not MiniLM neural inference.

See `docs/MULTILINGUAL_EXECUTED_RESULTS.md`, `data/results/multilingual_measured_summary.csv`, and `notebooks/08_Multilingual_Semantic_Search_Executed_Evidence.ipynb` for the measured result table and executed code. The cleaned notebook preserves meaningful outputs while removing transient Colab progress widgets. The supplied original notebook's SHA256 appears in `data/results/multilingual_evidence_manifest.json`.


## Offline topic search and resilient translation (November 23, 2026)

NewsBot now defaults to `mode="offline"` for English, Spanish and French queries. For Spanish and French, a **manually curated, bounded list of news topic words** maps terms such as `tecnología` to `technology` and `robotique` to `robotics`. English LSA or TF IDF then retrieves against the **synthetic classroom corpus**. No external data transmission or user consent is required for this mode. It is **not translation**, multilingual model inference, general natural language understanding, or current BBC article search. Unknown topics and negations may be omitted, so results must be reviewed.

`mode="translated"` remains an explicit opt-in external service. Google's underlying endpoint can answer HTTP 429 (`TooManyRequests`) for shared hosted service IPs. The code now classifies rate-limited provider errors, stops repeated requests for a local 10 minute cooldown, and exposes structured errors without leaking submitted text. If a consenting external translation call fails and local news-topic words are recognized, the query is searched using a **conspicuously labeled offline fallback**, not a fabricated translation. Direct text translation is unavailable during the provider limit; it never returns vocabulary lookup as a full translated sentence.

The default web UI selects offline search. The "Compare LSA and TF IDF" control also normalizes recognized Spanish/French topic words locally. Testing includes third-party rate limit simulation, zero external requests in offline mode, fallback output provenance, and Spanish/French retrieval. Actual external provider reliability and translation quality remain unverified.

For robust, full sentence production translation, deploy an authorized paid/free-tier translation API with credentials or separately host an approved offline model, after evaluating data protection, resource limits, and quality. None is assumed installed for this capstone.
