# API Reference

## `GET /`
Returns the static analysis and query dashboard.

## `POST /api/analyze`
Request JSON: `{"text":"The company announced..."}`. Minimum length is 30 characters; maximum is 30,000. JSON response fields: `classification` (`category`, model probabilities), `sentiment`, `language`, `summary`, `entities`, `relations`, `topics`, `needs_human_review`, `model_source`. Returns HTTP 400 for malformed text; 503 when model not trained.

## `POST /api/query`
Request JSON: `{"query":"How many technology articles?"}`. Returns `intent`, `answer`, `articles`, `context` and optional topic/method metadata. Relevant article IDs and retrieval method are retained. Uses Flask session for filter context.

## `GET /api/stats`
Returns article count, category distribution, source coverage and date coverage.

## `POST /api/clear`
Clears conversation filter context.

## Python library entry points
`NewsBotSystem.fit_csv(path,source)`, `.analyze(text)`, `.ask(query,context)`, `.corpus_stats()`; `TopicModeler.top_words(method)`; `NewsClassifier.predict(text)`; `Translator.translate(text,source,target)`; `SemanticSearch.search(query,top_k)`.
