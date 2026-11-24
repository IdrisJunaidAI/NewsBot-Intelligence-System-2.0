# NewsBot 2.0 BBC Research First Website Release

## Delivered

* The main dashboard now loads **derived statistics from authentic historical BBC News Train** by default: 1,440 distinct labeled texts after removing 50 repeated articles from 1,490 input rows.
* It shows five true BBC class counts, authentic historical NMF and LDA topic assignments, a separately labeled TextBlob polarity estimate and validated classical classifier results.
* No original BBC news article bodies are included in the server's public corpus or aggregate JSON. Historical BBC topics cannot support time evolution because publication dates are absent.
* The 60 synthetic article collection is retained as an explicit optional dashboard toggle and powers the stored article chatbot.
* The new Current BBC News Headlines section uses official BBC News RSS titles and direct article links with visible attribution and an error fallback. These links are separate from the historical training corpus.
* A responsive individual research portfolio layout, keyboard usable controls, CSV aggregate export, and independent submission documentation were added.
* Github Actions tests BBC aggregate mass balance, classified BBC provenance, source selection, synthetic distinction and RSS parsing.

## Measured evidence

The authentic BBC classifier's Logistic Regression held out accuracy is 95.83% and macro F1 is 95.67% on 288 records; Linear SVM comparison is 96.88% accuracy. The full historical BBC topic statistics use 1,440 unique documents. The separate MiniLM Colab experiment recorded 18/18 top rank retrieval matches on six synthetic passages and 18 queries.

## Honest limitations

* The BBC historical file has no verified article publication dates. Dated topic and sentiment evolution remains unavailable.
* The chatbot and lightweight hosted LSA search do not index full BBC article texts. They explicitly search the separate synthetic examples.
* The RSS section may be unavailable when BBC feed network access fails.
* Cross language cultural interpretation and external translation quality on authentic multilingual news are not validated.
* The professor requires a group submission in the detailed PDF, while this version is an individually prepared alternative pending instructor agreement.
