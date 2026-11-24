# Data provenance and licensing

The repository stores a deliberately **synthetic 60 article teaching corpus** as `data/raw/demo_articles.csv`. The student-supplied **original historical BBC News Train/Test CSVs are not included** because permission to republish full BBC news articles is not established.

For independent replication with authorized local data, consult `docs/BBC_AUTHENTIC_EVALUATION.md` and `scripts/evaluate_bbc.py`. The repository contains derived aggregates, evaluation metrics and safe public classifier weights; no original article bodies are embedded in the public JSON.

The `data/processed/` folder is reserved for locally generated cleaned datasets and is intentionally empty in Git. Generated raw and intermediate data should not be committed without verifying publisher rights and privacy.
