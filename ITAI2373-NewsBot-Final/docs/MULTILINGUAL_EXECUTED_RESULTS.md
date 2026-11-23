# Executed Multilingual MiniLM Retrieval Evidence

## Evidence and execution status

The uploaded Google Colab notebook executed seven code cells (execution counts 1 through 7). Its output confirms that `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` was loaded as a real pretrained encoder and returned **384 dimensional** vectors. The test used **6 synthetic English articles and 18 investigator constructed queries** (6 English, 6 Spanish, 6 French). The experiment encoded both article passages and queries with the same multilingual model. TF IDF served as the lexical comparison.

## Recorded results

| Method | Language | Queries | Recall@1 | Recall@3 |
| --- | --- | ---: | ---: | ---: |
| MiniLM | English | 6 | 100% | 100% |
| MiniLM | Spanish | 6 | 100% | 100% |
| MiniLM | French | 6 | 100% | 100% |
| TF IDF | English | 6 | 100% | 100% |
| TF IDF | Spanish | 6 | 50.0% | 66.7% |
| TF IDF | French | 6 | 33.3% | 50.0% |

Micro-average top result success: **MiniLM 18/18 (100%)** and **TF IDF 11/18 (61.1%)**. These numbers are arithmetic summaries of the notebook output, not new model executions. Language identification agreement was **18/18** on this constructed set. The notebook's three recorded robotics queries returned the same correct top article in English, Spanish and French with cosine scores 0.801, 0.835 and 0.821 respectively.

## Important interpretation and limitation

1. This experiment establishes that the actual pretrained encoder can perform cross language retrieval on these examples. It **does not** establish real multilingual news accuracy, model generalization or performance on the BBC corpus.
2. Only 6 documents and 18 semantically straightforward queries were tested. The lexical method may have ties at zero similarity for Spanish or French; its observed ranking can depend on arbitrary tie order.
3. Language detection succeeded for these selected queries. Longer, noisy, short, code switched, or domain specific text was not systematically tested.
4. `ALLOW_EXTERNAL_TRANSLATION = False`; the saved output explicitly says external translation was disabled. **Translation quality and provider availability were not measured.**
5. The Colab notebook compares multilingual MiniLM to TF IDF. **It does not compare MiniLM to the Render LSA implementation** in the same benchmark.
6. Cultural context comparisons, multilingual publisher perspectives, current news and external validity remain unverified.
7. The notebook source saves CSV and manifest files in the Colab runtime but those separately exported files were not part of the user supplied attachment. The measured summary CSV in this repository is extracted from the executed notebook's displayed aggregate table.

## Reproducibility

Run `notebooks/08_Multilingual_Semantic_Search_Executed_Evidence.ipynb` in Colab with the listed dependencies. The notebook includes the openly shown synthetic articles, query labels, inference code, ranking logic and saved output evidence. For rigorous further study, introduce a larger independently labeled multilingual evaluation corpus and compare using identical queries, relevance judgments and candidate sets. Record environment versions and model revision at next execution.

## Connection to deployed system

The live Free Render deployment uses lightweight **LSA** for the synthetic article corpus. It does **not** run a Sentence Transformers MiniLM inference service on Render. The **BBC Logistic Regression category classifier** operates on pasted article text but was trained on historical English BBC articles. The Colab MiniLM results are independent research evidence and do not change these deployment boundaries.

**AI assistance disclosure:** This writeup and summary file were prepared with AI support from the user supplied executed notebook. The recorded experimental output is derived from the user's Colab execution.