# Authentic BBC News classification evaluation

## Data supplied by student

* `BBC News Train.csv`: 1,490 labeled rows. Fifty duplicate article texts were removed before any training or held-out split, leaving 1,440 unique examples.
* `BBC News Test.csv`: 735 unlabeled rows, including 13 duplicate test texts. There are 38 unique texts that also appear in the labeled training file. It must not be treated as an independent accuracy benchmark without verified labels and contamination controls.
* `BBC News Sample Solution.csv`: the assigned category repeats every fifth row in a fixed cycle (`sport`, `tech`, `business`, `entertainment`, `politics`), clearly contradicting some article subjects. These labels are submission placeholders, **not** ground truth; no scores are calculated against them.

## Evaluation protocol and results

We used only the cleaned, deduplicated labeled BBC training corpus for model evaluation. Random seed 42; stratified 80/20 split; 1,152 examples in training and 288 held out. TF IDF with unigram/bigram features, English stop words, 12,000 maximum features, and sublinear term frequency. 3-fold cross validation was conducted **within** the training partition. The holdout was not used for fitting or model selection.

| Algorithm | Held-out accuracy | Held-out macro F1 | Training partition 3-fold macro F1 |
|:--|--:|--:|--:|
| Majority baseline | 23.61% | 7.64% | 7.69% |
| Multinomial Naive Bayes | 95.14% | 94.83% | 96.00% |
| Logistic Regression | 95.83% | 95.67% | 96.70% |
| Linear SVM | 96.88% | 96.77% | 97.70% |

Linear SVM achieved the largest held out F1 in this split. Logistic Regression was released for classifier inference because the deployed NewsBot interface already offers model probability outputs. These values are uncalibrated and must not be interpreted as likelihood of correctness. All results reflect historical BBC news labels and the specific split above, not external 2026 publication accuracy.

## Few-shot research extension

A low-data learning curve was studied using 5 repetitions, training samples per class of 5, 10, 25, 50 and 100. Each subset was selected only from the 1,152-row training partition, and all were evaluated on the same unseen 288-row holdout. Mean macro F1 across random seeds: 85.26%, 90.52%, 94.72%, 95.41% and 95.61%, respectively. Repeated subset selection is exploratory, and held out reuse can influence human modeling decisions. It is not evidence of domain adaptation or large language model few-shot prompting.

## Public deployment separation

The Render Free web deployment loads a compact, non-executable, JSON.GZ table containing only the BBC Logistic Regression TF IDF vocabulary, inverse document frequencies, coefficients, intercepts and class labels. No raw BBC article texts are included in that artifact. The single-article **category classifier** can use real BBC-trained parameters. The **default dashboard category charts, topic modeling aggregates and research classification scores** now use real historical BBC derived data from all 1,440 unique labeled articles, with no raw BBC text published. Historical BBC sentiment aggregate uses separately labeled TextBlob lexical polarity. The stored-article conversational search, per-input statistical topic model and optional demo charts still use the 60 synthetic teaching articles. Sentiment, NER and extractive summaries on pasted text are calculated separately. The current BBC official RSS headline links are a third source and are not the historical training corpus.

The status labels in the web app must reflect that mixed provenance. A complete BBC topic and semantic search deployment would require a separately approved licensed article collection and, for transformer-based search, optional embedding dependencies. The website can display current official BBC RSS headline links, but does not ingest full articles or re-train on this feed. Translation is an opt-in external provider integration on Free hosting; its quality was not independently validated.

## Reproducibility

Run `python scripts/evaluate_bbc.py --train "<train path>" --test "<test path>" --sample "<sample path>" --out data/results/`. Outputs: aggregate JSON evaluation, per-article category predictions, an exploratory few-shot learning curve, and a local Python pipeline artifact. Inspect the file hash before reproducing. Classifier weights were exported as a compact JSON.GZ file for safe web serving, not as a serialized Python executable object.

SHA256 training: `f56a65dab2ea728505a639d2186a2b2f1c0939f28e8e89b5ed1c1fe9520b1323`.

## Limitations and academic integrity

The instructor requires genuine individual contribution records, proper AI tool attribution, and individual reflective record by the sole student. The project files do not establish those details. Historical BBC articles have no trustworthy publication date metadata in these uploads; no temporal-news trend claims can be made. The task's real-time, multilingual translation, cultural perspective, and generative content requirements still need separate implementation and testing.
