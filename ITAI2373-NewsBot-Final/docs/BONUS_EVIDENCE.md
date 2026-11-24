# Bonus Evidence | Up to 50 Additional Points

This independent ITAI 2373 capstone has two separately auditable bonus tracks. Evidence supports **eligibility for consideration**, not a guaranteed score.

## A. Flask web frontend: up to 30 bonus points

**Public demonstration:** https://newsbot-intelligence-system-2-p97f.onrender.com

**Source repository:** https://github.com/IdrisJunaidAI/NewsBot-Intelligence-System-2.0

| Instructor-specified UI area | Implementation | Verification |
| --- | --- | --- |
| Dashboard overview | `GET /api/dashboard` shows authentic historical BBC derived analytics; synthetic demo requires an explicit switch | Flask tests validate 1,440 BBC evidence articles vs 60 synthetic articles |
| Single article analysis | `POST /api/analyze` returns real BBC trained category plus separate text tone, entity extraction, and extractive summary | Tests cover validation and output provenance |
| **Batch article processing** | **New** `POST /api/batch/analyze` evaluates 2 to 5 user supplied excerpts, bounded at 5,000 characters each and 15,000 combined | Unit/API tests cover total and individual length constraints, nontext input and no processing before validation |
| Natural language query interface | `POST /api/query` with conversation context, intent parsing and source IDs | Integration and API tests; stored content explicitly synthetic |
| Charts and graphs | Interactive BBC category/tone/NMF/LDA charts, model evaluation, and a **new historical learning curve with metric selector** | `/api/research/fewshot` reads measured CSV and provides mean and standard deviation |
| Multilingual features | English/Spanish/French detection, local bounded vocabulary lookup, optional third party translation with consent | API tests include rate limit fallback and no unwanted external calls |
| Current headlines | BBC RSS title/link cards with attribution and safe BBC destination checks | Feed parsing tests; not republished article bodies |
| Web quality | Flask, HTML, CSS, JavaScript; responsive Prismatic Glass theme; five credited MIT Uiverse UI elements; Render Free with GitHub CI | Existing frontend syntax and Python regression tests; manual user acceptance remains recommended |

**Live deployment caveat:** The service runs on Render Free and may require a cold start. The current BBC RSS panel fetches headlines/links only, not protected complete article content. No paid resource is provisioned.

## B. Advanced research extension: up to 20 bonus points

### Authentic historical BBC low-data learning curve

The student supplied authentic BBC labeled train CSV was deduplicated to 1,440 unique articles. A stratified 80/20 split reserved 288 unseen articles as the fixed holdout. Reduced-sized training subsets were sampled from the remaining training partition, **five repetitions per size**. Each fit used TF IDF with Logistic Regression.

| BBC examples / category | Total training examples | Mean heldout macro F1 | Across-seed standard deviation |
| ---: | ---: | ---: | ---: |
| 5 | 25 | 85.26% | 2.31 percentage points |
| 10 | 50 | 90.52% | 2.38 percentage points |
| 25 | 125 | 94.72% | 0.61 percentage points |
| 50 | 250 | 95.41% | 0.83 percentage points |
| 100 | 500 | 95.61% | 1.10 percentage points |

All values above are calculated from the committed **25 original experiment rows**, not synthetic illustrative figures. Across-seed standard deviation is not a confidence interval. Differences between neighboring means do not establish statistically significant superiority.

**Reproduce and examine evidence:**

1. `data/results/fewshot_learning_curve.csv`: 25 numeric recorded results including random seeds.
2. `scripts/evaluate_bbc.py`: original split/model evaluation code for re-running with a separately authorized BBC CSV.
3. `notebooks/09_FewShot_Learning_Curve.ipynb`: instructor-friendly study and plotting walkthrough consuming measured evidence.
4. `src/utils/research_bonus.py`: validated CSV reader and summary statistics with no raw BBC article texts.
5. `GET /api/research/fewshot`: stable evidence API.
6. Live website section **How much labeled data does a classifier need?**: interactive macro F1/accuracy chart with transparent methodology.

**Research limitations:** This is reduced-training-data supervised classification of existing BBC categories. It is not a demonstration of classifying previously unseen categories, not in-context few-shot prompting of an LLM, and not multilingual or domain-shift evaluation. The fixed holdout was repeatedly inspected across training sizes, so the study is exploratory. Permission to reproduce the historical BBC text must be established separately.

## Demonstration script for both bonus items

After opening the live site, show the source-controlled BBC dashboard, switch to the synthetic demo to distinguish sources, run one pasted article through analysis, then run two independent excerpts through the batch panel. Demonstrate a question about stored synthetic articles. Show the low-data learning curve and change the metric between macro F1 and accuracy. Explain that scores come from the committed historical experiment and that the research did not involve an LLM prompt, followed by the limitations above.

The instructor has sole discretion over awarding bonus points.


## Instructor-ready bonus evidence appendix

The optional `reports/FP_BonusEvidence_IdrisJunaid_Individual_ITAI2373.pdf` provides a two-page visual evidence summary, including the measured learning curve and method disclosures. The updated `reports/FP_Presentation_IdrisJunaid_Individual_ITAI2373.pptx` has 20 slides. Slides 17 and 18 separately address the up to 20 point research extension and up to 30 point Flask frontend. The source-controlled PDF `reports/presentation_slides.pdf` is a 20-page viewing copy and is not required in addition to the PPTX for Canvas submission.
