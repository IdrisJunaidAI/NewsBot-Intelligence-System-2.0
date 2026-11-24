# NewsBot Intelligence System 2.0

## Individual ITAI 2373 NLP capstone

**Student:** Idris O. Junaid  
**Submission scope:** Individual work and independently accountable research portfolio.  
**Professor's individual submission decision:** Student reported on November 24, 2026 that individual completion is accepted and no groups will be formed. This report has not been independently verified against written instructor correspondence.  
**Source repository:** https://github.com/IdrisJunaidAI/NewsBot-Intelligence-System-2.0  
**Website:** https://newsbot-intelligence-system-2-p97f.onrender.com  
**Due:** December 1, 2026, at 11:59 PM Central Time.

### Website data source: authentic BBC evidence first

The dashboard shows aggregate statistics computed from the student's supplied labeled BBC News Train CSV by default. The source contains 1,490 records; after removal of 50 repeated article texts, 1,440 distinct records remain across the five original labeled categories. It shows actual BBC category frequencies, LDA and NMF statistical topic counts, TextBlob polarity estimates and the original stratified classifier holdout evidence. The report in `data/results/bbc_public_analytics.json` contains **no original BBC article bodies or full text** and no invented publication dates. The original CSV is excluded from public GitHub and the live server.

A clearly marked toggle exposes the **separate 60 article synthetic teaching corpus** for chatbot article retrieval and its demonstration charts. The live website does not yet semantically search full historic BBC article texts: that would require a legally authorized publication or retrieval deployment. It must never imply that synthetic chatbot search results came from BBC News.

The **Current BBC News Headlines** panel uses attributed, unmodified headline titles and source links from an official BBC RSS feed when available. RSS entries are **current third party links**, not the historical classifier training corpus. Publisher conditions apply; this personal academic demonstration is not licensed for commercial use.

### Classification results from authentic BBC historical data

| Model | Held out accuracy | Macro F1 |
| --- | ---: | ---: |
| Majority baseline | 23.61% | 7.64% |
| Multinomial Naive Bayes | 95.14% | 94.83% |
| Logistic Regression deployed for classification | 95.83% | 95.67% |
| Linear SVM comparison | 96.88% | 96.77% |

A fixed seed 42, stratified 80/20 split was used after deduplicating repeated article texts. The holdout includes 288 articles. The 735 record BBC test CSV contains no verified labels; the supplied sample solution repeats a sequence and is not a credible ground truth. Do not claim test accuracy on those 735 records. The released Logistic Regression inference weights were trained on all 1,440 unique records after the holdout experiment, and do not contain the underlying news text.

### Multilingual study

An executed student Colab notebook demonstrates real `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` inference with 384 dimensional embeddings. On a small synthetic six document benchmark and six queries in each of English, Spanish and French, recorded Recall@1 and Recall@3 were 100% for MiniLM across the three languages. The English only TF IDF baseline had Recall@1 of 100%, 50% and 33.3%, respectively. This is **not validation on authentic multilingual news** and does not establish cultural context interpretation. External translation was disabled during that Colab run. Hosted Render Free uses an LSA index instead of MiniLM due resource limits.

### Installed system modules

1. **Content Analysis:** classification, LDA/NMF topic modeling, VADER sentiment for individual English input, spaCy entity recognition, category and topic visualization, deduplication and quality reporting.
2. **Understanding and Generation:** extractive summarization, TF IDF/LSA retrieval comparison, rule grounded insight templates; neural multilingual MiniLM in a separate tested Colab execution.
3. **Multilingual Intelligence:** language detection for English, Spanish and French, optional consent based translation with a third party provider, and an experimental cross language embedding pipeline. Translation quality and cultural perspective analysis remain unverified.
4. **Conversational Interface:** intent parsing, filters and multi turn session context for the separate synthetic demonstration corpus. No live BBC corpus conversation is claimed.

### Reproduction

Use Python 3.11 and run from `ITAI2373-NewsBot-Final`:

```bash
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
python train.py --demo
python -m pytest -q
python scripts/smoke_real_classifier.py
python app.py
```

For real BBC reproduction, supply a licensed, locally stored copy of `BBC News Train.csv` and follow `docs/BBC_AUTHENTIC_EVALUATION.md`. To regenerate the public aggregate export, run `python scripts/export_bbc_public_analytics.py --csv "path/to/BBC News Train.csv"`, if the optional offline dependencies are installed. No original BBC article text should be committed.

### APIs

* `GET /api/dashboard` defaults to the authentic historical BBC aggregate evidence.
* `GET /api/dashboard?source=demo` provides explicitly synthetic corpus statistics.
* `GET /api/export/analytics.csv?source=bbc` downloads derived BBC aggregates.
* `GET /api/bbc/headlines?channel=top` retrieves BBC attributed RSS titles and BBC page links.
* `POST /api/analyze` classifies a pasted article with authentic historical BBC weights and discloses limitations.
* `POST /api/query` queries only the separate demonstration article collection.
* `GET /api/multilingual/status`, `POST /api/multilingual/detect`, `POST /api/multilingual/translate`, `POST /api/multilingual/search` and `POST /api/retrieval/compare` expose documented language features.

### Scope, ethics and transparency

This is an educational research prototype, not an audited production platform or fact checker. The historical BBC training corpus has no verified publication dates, so topic and sentiment evolution cannot be inferred from it. The RSS headlines can provide dated current links but are not the training corpus. The BBC publisher's reuse conditions and dataset license must be followed. Model probability is not guaranteed calibration. Cross language news cultural comparisons have not been externally verified.

**Academic integrity:** ChatGPT assisted with implementation, draft writing and test development. The student supplied source data, ran and returned executed Colab evidence, reviewed the code and research outputs, and retains responsibility for testing, comprehension, revisions and submission. AI assistance must not be misrepresented as unaided work.

**Individual submission status:** The student reports the professor accepted completion individually and does not intend to form groups. The files use `Individual` in the group segment of the published filename template. The professor's approval is student reported, not independently corroborated by a written notice. No fictional collaborators are reported.

### Evidence and reports

See `docs/individual_contributions.md`, `docs/technical_documentation.md`, `docs/individual_submission_compliance.md`, `docs/MULTILINGUAL_EXECUTED_RESULTS.md`, the protected historical files in the repository root, the regression test suite and the `reports/` directory for individual submission artifacts.

## GitHub link and presentation alternatives

The course specifies an individual public repository for each submitter. This repository satisfies that condition for the approved solo capstone. The presentation format is a **19 slide PowerPoint with notes OR a 10 to 15 minute video**. The MP4 demonstration supplied separately is a **synthetic narration rehearsal aid**; it does not replace a recording where the student appears and walks through the live application. See [submission and video guidance](docs/VIDEO_PRESENTATION_AND_INDIVIDUAL_REPOSITORY.md).

### Bonus coursework evidence

The optional **Flask frontend** now includes a 2–5 article batch analyzer and an interactive authentic BBC few-shot learning curve alongside the existing BBC dashboard, multilingual lab and synthetic corpus chatbot. For reproducible bonus research evidence, see [BONUS_EVIDENCE.md](docs/BONUS_EVIDENCE.md), [professor rubric matrix](docs/assessment_matrix.md) and [notebook 09](notebooks/09_FewShot_Learning_Curve.ipynb). The measured 25-run learning curve is low-data supervised classification, **not** LLM few-shot prompting or generalization to unseen categories. No paid hosting or additional live-news content is needed.

**Submission formats:** The professor's directory-tree examples use descriptive names such as `reports/technical_report.pdf`, while Canvas explicitly mandates `FP_TechnicalDoc_...` filenames. The required, individually named PDFs/PPTX reside in `reports/`; see [reports README](reports/README.md). The professor approved individual work as reported by the student.
