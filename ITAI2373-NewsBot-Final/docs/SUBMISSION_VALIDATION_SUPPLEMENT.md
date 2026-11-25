# Submission validation supplement (candidate, not yet executed)

The existing submitted evidence remains unchanged. This branch adds optional research scripts, not new measured results. Do not cite a score until the corresponding experiment completes and outputs are independently reviewed.

## Execution and acceptance

Run from ITAI2373-NewsBot-Final in a fresh Python 3.11 environment with access to pretrained model downloads. Install requirements-research.txt. Keep licensed source text and annotations outside GitHub. Use lowercase English category labels for the few-shot input.

| Experiment | Local input | Acceptance evidence |
| --- | --- | --- |
| Multilingual retrieval | documents.csv: id,text,language,published_at,source; queries.csv: query_id,query,language,relevant_id | Independent authentic documents and queries, English Spanish French, Recall@1, Recall@3, MRR per language and errors |
| Abstractive generation | Same documents CSV; references.csv: id,reference | Human authored references to English source windows, ROUGE against lead two sentences, manual factuality review |
| Temporal analysis | Dated documents CSV, verified publication dates | Monthly topic shares and sentiment with sample counts, stable topic model, source coverage caveat |
| LLM few shot | fewshot.csv: text,label,split (support/test) | Distinct held-out examples, zero/one/two demonstrations per label, accuracy and macro F1, invalid predictions |

Example commands (replace local paths):

```bash
python -m pip install -r requirements-research.txt
python scripts/submission_research.py retrieval --documents /local/documents.csv --queries /local/queries.csv --output /local/results --acknowledge-data-rights
python scripts/submission_research.py summary --documents /local/documents.csv --references /local/references.csv --output /local/results --acknowledge-data-rights
python scripts/submission_research.py temporal --documents /local/documents.csv --output /local/results --acknowledge-data-rights
python scripts/submission_research.py fewshot --fewshot-data /local/fewshot.csv --output /local/results --acknowledge-data-rights
python -m pytest -q
python scripts/smoke_real_classifier.py
```

Recommended study design: 30 or more independently sourced documents, 10 or more independently written queries per language, at least 20 human reference summaries, and a balanced held-out few-shot test with at least 10 items per category. These are proposed minima, not instructor requirements. Do not tune on the held-out test. Record dataset license, source, model revision, package versions, hardware, random seeds and exact execution date. Have a reviewer assess translation adequacy, cultural framing and summary factual consistency separately; retrieval and ROUGE cannot establish these.

## Release gate

1. Verify existing main branch CI and browser smoke tests; check health, dashboard source toggles, single and batch analysis, conversation, multilingual interface, RSS and CSV export.
2. Save current test logs with commit hash; preserve historical November 10 log as historical evidence.
3. Inspect all actual PDF/PPTX deliverables and reconcile every number to the measured experiment outputs. Add a methods/results appendix only after execution; do not replace existing metrics with unrelated benchmarks.
4. Confirm instructor's original rubric and individual naming permission. Confirm whether the user tutorial requires personal recording. Do not present synthetic narration as personal video.
5. Rehearse live defense; retain AI assistance attribution. Submit four required files and optional bonus appendix only after approval.

## Current status

Research runner is authored but not yet executed. Licensed data, independent annotations, model downloads and actual final documents are required before claiming improved grades. Existing 95.83% BBC Logistic Regression holdout and 18/18 controlled synthetic retrieval remain distinct experiments. The current public app remains unchanged.
