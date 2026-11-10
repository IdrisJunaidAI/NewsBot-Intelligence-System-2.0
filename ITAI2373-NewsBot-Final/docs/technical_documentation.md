# Technical Documentation | NewsBot Intelligence System 2.0

## 1. Scope and architecture
NewsBot extends the executed October 2026 midterm notebook into a modular analytics pipeline. Component boundaries separate validation, classification, topic discovery, text tone, entity extraction, extractive summarization, search, translation and dialogue. It is a research prototype designed to be upgraded and audited, **not** a complete production security certification.

## 2. Data model and ingestion
Input CSV accepts Text/Category/ArticleId from the BBC competition, plus optional date, source and language metadata. `load_news_csv` lowercases category labels, maps `tech` to `technology`, removes missing text and exact duplicate documents, and preserves original article text for inference. For a real BBC run use the original approved `BBC News Train.csv` file; output sample counts must be recalculated. Data should be partitioned before statistical vocabulary fitting to avoid leakage.

## 3. Classification and comparison
Classifiers compared: majority baseline, Multinomial Naive Bayes, Logistic Regression, Linear SVM. A stratified 80/20 split is formed using seed 42; 3-fold stratified CV is run exclusively within training data. F1 macro and accuracy are reported. An interpretable Logistic Regression/TF IDF pipeline is evaluated on held-out data, then re-fitted on all data for inference. This differs from the midterm model selected by CV. Probabilities are **not** calibration guarantees. For operational use, add calibration, confidence thresholds, external testing and drift monitoring.

## 4. Topic modeling
Latent Dirichlet Allocation uses count vectors. Nonnegative matrix factorization uses TF IDF. Both generate top terms and topic mixtures. Since topic labels are inferred rather than truth, manual interpretation is required. Topic evolution requires authenticated publication timestamps; corpus without dates returns an unavailable message rather than fabricated trends.

## 5. Sentiment, POS and named entities
The current engine uses VADER when present and an explicitly labeled limited lexicon otherwise. spaCy `en_core_web_sm` extracts person, organization, geographical, date and money entities when installed. Entity pairs are **cooccurrence** only. POS and dependency parsing remain documented in the source midterm notebook and can be wired into the service as an additional final extension. Missing spaCy models produce explicit unavailability rather than empty evidence claims.

## 6. Summarization and retrieval
The default summarizer selects sentences from source article via TF IDF similarity centrality. It cannot invent new source sentences, but it may omit critical context. SemanticSearch optionally uses multilingual sentence transformer vectors; if missing it transparently uses lexical TF IDF. Cross-language search is disabled in lexical fallback mode.

## 7. Multilingual intelligence
`LanguageDetector` optionally relies on langdetect and otherwise uses a small English/French/Spanish heuristic. `Translator` uses optional deep-translator network services and explains unavailable states; it does not silently invent translations. Regional/cultural perspective analysis requires an appropriately sampled multilingual dataset and human annotations, not assumed nationality from vocabulary.

## 8. Conversational intelligence
`QueryProcessor` applies rule-driven intent detection and natural language category/sentiment selection, supports multi-turn filter state, returns matching article IDs, counts and extractive summaries. The Flask session records filter state, not complete articles. Questions requesting time filters decline when date provenance is absent.

## 9. API reference
`GET /`: HTML dashboard. `POST /api/analyze` JSON `{ "text": "..." }` returns classification, tone, language, summary, topics and entities. `POST /api/query` JSON `{ "query": "..." }` returns answer and source article IDs with session state. `GET /api/stats` returns corpus metadata. `POST /api/clear` clears dialogue filters. Input length enforced at 30 to 30,000 characters. Model missing returns 503.

## 10. Deployment, security, QA
Run a dedicated Python environment and install `requirements.txt`; download spaCy English model and train from the approved CSV. Use a trusted locally generated joblib artifact only, configure HTTPS and a stable `FLASK_SECRET_KEY`, add rate limiting, observability and authentication before public deployment. The supplied Flask app is a local demonstration scaffold. Tests cover validation, two topic models, classification, retrieval, conversation, language detection and input handling.

## 11. Evaluation design
Classifier metrics are calculated only when the correct dataset is supplied and training executes. Evaluate per-class precision/recall, macro F1, confusion matrix, and external-domain robustness. For retrieval, create manually judged query/article pairs and report precision at 5; for summaries, evaluate coverage, factual consistency and useful brevity through human review; for multilingual search, use cross-language relevance judgments and translation quality checks.

## 12. Attribution and scientific honesty
Documented midterm BBC run retained 1,440 articles and reported SVM accuracy 96.53%, macro F1 96.45%, according to supplied October 2026 reports. No new BBC final-model performance is claimed. Synthetic training data is a software demonstration, not scholarly validation. Report actual new outcomes after execution with approved source. Record each contributor's verified work and AI assistance; do not invent team meetings or commitments.
