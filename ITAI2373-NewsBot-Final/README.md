# NewsBot Intelligence System 2.0

**ITAI 2373 Natural Language Processing Final Capstone**

**Live application:** https://newsbot-intelligence-system-2-p97f.onrender.com

**Portfolio repository:** https://github.com/IdrisJunaidAI/NewsBot-Intelligence-System-2.0

**Student:** Idris O. Junaid. **Team name and contribution assignments:** must be confirmed.

## What is actually deployed

NewsBot is an educational NLP research prototype hosted as a Flask web application on Render Free. It provides article classification, sentiment analysis, named entity recognition, extractive summarization, topic exploration, lexical search and a conversational interface.

**Two distinct source boundaries are intentional.**

1. **Single article category classification:** TF IDF Logistic Regression weights trained on 1,440 distinct labeled real BBC News Train articles. A released non-executable JSON.GZ coefficient table contains vocabulary, IDF and model weights but no original BBC article texts.
2. **Dashboard charts, topic modeling, stored article search and conversational article retrieval:** 60 synthetic teaching articles. These are not real BBC coverage and are not a live news feed. The frontend labels this distinction.

Article sentiment, entities and extracted summaries are calculated from the user supplied text. Translation, transformer semantic retrieval and cultural perspective comparisons are not deployed and should not be presented as functioning production capabilities.

## Authentic BBC evidence

Three supplied files were audited:

* BBC News Train: 1,490 labeled input articles; 50 exact duplicate texts removed, leaving 1,440.
* BBC News Test: 735 unlabeled articles; 38 distinct article texts overlap the training set.
* BBC News Sample Solution: category labels repeat every five rows. It is a formatting placeholder, **not verified ground truth** and was not used to calculate accuracy.

A stratified split with random seed 42, 1,152 training articles and 288 held out articles, after text deduplication, produced:

| Classifier | Held out accuracy | Macro F1 |
| --- | ---: | ---: |
| Majority class baseline | 23.61% | 7.64% |
| Multinomial Naive Bayes | 95.14% | 94.83% |
| Logistic Regression (deployed) | 95.83% | 95.67% |
| Linear SVM (best tested) | 96.88% | 96.77% |

The model scores are uncalibrated. These historical results are an **internal BBC holdout evaluation**, not real time news performance or an independently labeled external test. Detailed aggregate metrics, class confusion and the research protocol are in `data/results/bbc_evaluation.json` and `docs/BBC_AUTHENTIC_EVALUATION.md`.

### Optional research extension

`data/results/fewshot_learning_curve.csv` contains a repeated low data study with five random subsets at each of 5, 10, 25, 50 and 100 labeled articles per class. On the fixed held out set, mean macro F1 increases from 85.26% to 95.61%. This is a supervised data efficiency experiment, not few shot LLM prompting.

## Development setup

Python 3.11 recommended.

```bash
cd ITAI2373-NewsBot-Final
python -m venv .venv
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
python train.py --demo
python -m pytest -q
python scripts/smoke_real_classifier.py
python app.py
```

To rerun the real BBC experiment, download or supply your approved BBC CSV files locally and run:

```bash
python scripts/evaluate_bbc.py --train "/path/BBC News Train.csv" --test "/path/BBC News Test.csv" --sample "/path/BBC News Sample Solution.csv" --out data/results
```

The original BBC article files are intentionally excluded from this repository. The last command generates real metrics, test category predictions, repeated low data trials and a locally trusted classifier pipeline.

## API and quality

The Flask app exposes `/`, `/health`, `/api/analyze`, `/api/query`, `/api/dashboard`, `/api/stats`, `/api/export/analytics.csv` and `/api/clear`.

The repository uses automated Python, JavaScript and Flask endpoint checks via GitHub Actions. Build logs, deployed service version and request health can be inspected from the Render service dashboard. The app is a research prototype, not a hardened production security, reliability or fact verification service.

## Assessment and limitations

The instructor asks for four advanced modules, comprehensive documentation, a 15 minute team presentation, a technical PDF, executive PDF, individual portfolio repository access and a genuine three page reflective journal. Full multilingual translation, semantic embeddings, cultural context comparison and generative LLM enhancement remain unverified gaps. A dated external news ingestion system would be required for time trend claims and current news queries.

Reports and presentations under `reports/` are drafts unless the group name and verified team contributions are completed. The student and all team members must assess their own contributions and presentation roles.

**AI assistance disclosure:** ChatGPT assisted with source code, research evaluation, regression tests and draft documentation. Student and team are responsible for review, reproducibility, attribution and accurate representation of independent work.

## References

Instructor final project rubric and Web App Development Tutorial; provided BBC news CSV files; scikit-learn, spaCy and VADER project documentation.


## Phase 1: multilingual and semantic retrieval

English, Spanish, French language detection is available locally. The Render Free search uses latent semantic indexing (TF IDF with truncated SVD) with a lexical comparison. Translation assisted search uses a third party translator ONLY with explicit opt-in per request; the provider is not guaranteed. Genuine shared vector multilingual search uses the optional Sentence Transformers multilingual MiniLM model in the Colab notebook or a capable local machine; it is NOT running on the Render Free instance. See docs/MULTILINGUAL_SEMANTIC_PHASE1.md. The corpus search and topic dashboard remain synthetic while the single article BBC category classifier uses the real historical labeled BBC dataset.
