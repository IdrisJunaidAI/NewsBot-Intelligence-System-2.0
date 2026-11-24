# Technical Documentation | NewsBot Intelligence System 2.0

**Scope:** Individual ITAI 2373 capstone with AI assistance disclosed. The PDF `reports/FP_TechnicalDoc_IdrisJunaid_Individual_ITAI2373.pdf` is the print submission of this research design.

## Architecture and provenance

The Flask app combines data preprocessing, classification, LDA/NMF topic discovery, sentiment and NER, extractive summarization, LSA/TF IDF search, optional consent protected translation, and conversational intent/context routing. The public dashboard now defaults to the authentic historical BBC aggregate report `data/results/bbc_public_analytics.json` with 1,440 distinct labeled articles. It never serves the full historic BBC text.

The 60 synthetic training examples remain separate and are only the chatbot searchable collection. Current BBC official RSS titles and links are another separate data source. The real BBC trained Logistic Regression classifier is used to categorize new pasted English articles. Topic weights reported for individual input still come from the synthetic topic model and must be labeled separately.

## Dataset and partitioning

The supplied original `BBC News Train.csv` contains 1,490 labeled article rows. Deduplication of repeated text removes 50 records before random seed 42 stratified 80/20 splitting. There are 1,152 training and 288 held out records. The original `BBC News Test.csv` has 735 unlabeled records and overlaps on 38 distinct texts, so no external test accuracy is inferred. The cyclic sample solution file is not reliable test ground truth.

## Models and results

| Model | Held out accuracy | Macro F1 |
| --- | ---: | ---: |
| Majority baseline | 23.61% | 7.64% |
| Multinomial Naive Bayes | 95.14% | 94.83% |
| Logistic Regression deployed | 95.83% | 95.67% |
| Linear SVM comparison | 96.88% | 96.77% |

NMF on TF IDF and LDA on counts were fitted on the 1,440 authentic historical articles for the derived topic aggregation. The published aggregate sentiment is **TextBlob lexical polarity** with cutoffs +0.1 and -0.1. The article analysis endpoint uses VADER for separate English text tone. Neither gives verified public sentiment. The historical BBC CSV has no trusted dates: no time trend or sentiment evolution is fabricated.

## Language and semantic search

The deployed lightweight search uses TF IDF and truncated SVD LSA on the separate synthetic corpus. The user executed the real multilingual MiniLM model in Google Colab with 384 dimensional embeddings. On six synthetic passages and 18 questions (six each English/Spanish/French), the neural model achieved 18 of 18 top rank retrieval matches; the lexical baseline achieved 11 of 18. Translation was disabled in that notebook. The optional external translator on Flask requires explicit consent and its quality was not measured. Authentic cross publisher culture comparisons are not implemented.

## Web, APIs and provenance

* `/api/dashboard` defaults to authentic BBC statistical aggregates; `?source=demo` is explicitly synthetic.
* `/api/export/analytics.csv` respects the same source selection.
* `/api/bbc/headlines` displays attributed BBC official RSS titles and source links only, if the network source is available.
* `/api/analyze` uses BBC trained weights on user pasted English text.
* `/api/query` searches only the 60 synthetic demonstration articles.
* `/api/multilingual/*` provides language detection and optional consent protected translation and retrieval.

## Quality and security

GitHub Actions runs Python and JavaScript syntax validation, Flask API tests, demo training and authentic BBC classifier checks. New regression tests confirm that the default dashboard contains 1,440 real articles and no full historic text. The RSS parser ignores non BBC URLs and has a bounded cache. The hosted service is Render Free with a Python 3.11 Gunicorn application and a secret key provided by the host, not the repository. It is not penetration tested or production certified.

## Reproducibility

Run `python -m pip install -r requirements.txt`, `python train.py --demo`, `python -m pytest -q`, `python scripts/smoke_real_classifier.py` then `python app.py`. Historical BBC evaluation requires licensed local CSV access. To reproduce aggregate topic counts, run `python scripts/export_bbc_public_analytics.py --csv "path/to/BBC News Train.csv"` with offline `textblob` available, using the evidence JSON in `data/results/bbc_evaluation.json`. Data and model version details must be recorded for scientific reproducibility.

## Limitations, rights, academic integrity

Classifier probabilities are not calibrated, publisher rights and potential AI restrictions must be respected, BBC records lack dates, translation quality is not externally validated, and cultural context across real multilingual publishers is not proven. The student reports that the professor explicitly accepts independent completion and will not create a group. Individual authorship and documented AI assistance are retained. AI assistance was used to develop code, tests and drafts and must be disclosed rather than represented as work completed without support.

## Primary references

Instructor supplied final project and web application guidance; supplied BBC Train/Test/Sample CSVs; scikit-learn, spaCy, VADER and TextBlob documentation; official Sentence Transformers multilingual MiniLM model card; BBC Global Terms of Use for RSS and publisher content; GitHub Actions and Render deployment evidence.


## Optional bonus features and reproducible evidence

The Flask frontend now includes an intentionally bounded `POST /api/batch/analyze` endpoint for 2–5 pasted excerpts (30–5000 characters each, 15000 total). Input validation occurs before any model inference, and the service returns per-document category, uncalibrated model probability, sentiment, language, extractive summary and review indicator. No raw article body is intentionally persisted; published summaries necessarily reuse user-supplied sentences. The interface runs on Render Free without new external dependencies.

The advanced research extension is a **25-run historical BBC reduced-training-data experiment**, using five independently sampled training subsets at each of five sizes and a fixed 288-article holdout. The numeric CSV in `data/results/fewshot_learning_curve.csv`, the original `scripts/evaluate_bbc.py` experiment, `notebooks/09_FewShot_Learning_Curve.ipynb`, and the `GET /api/research/fewshot` endpoint provide auditable source, method, and presentation. See `docs/BONUS_EVIDENCE.md` for exact means, standard deviations and caveats. This is not unseen-category adaptation or in-context LLM few-shot prompting.


### Submission evidence synchronization

The optional two-page bonus appendix in `reports/FP_BonusEvidence_IdrisJunaid_Individual_ITAI2373.pdf` records the new frontend batch and authentic historical BBC low-data extension. The authoritative PowerPoint has 20 slides with speaker notes, and `reports/presentation_slides.pdf` is a matching PDF viewing copy. Existing technical PDF remains the core source analysis report; the bonus appendix is supplementary rather than silently modifying previously attested model results.
