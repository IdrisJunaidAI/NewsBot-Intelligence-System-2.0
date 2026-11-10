# NewsBot User Guide

## Start
Install requirements, obtain the approved BBC training CSV from Kaggle, train the model and start `python app.py`. Open the local browser link. Use only articles that you are authorized to process.

## Article analysis
Paste a news article of at least 30 characters and select Analyze. Review the predicted BBC category, model probability (not calibrated), sentiment, topic membership, extracted summary, language detection and entities. If the spaCy model is absent, entity extraction will explicitly say unavailable.

## Questions
Ask “How many technology articles?” or “Show positive business articles.” Follow up “Show more” to retain prior category filter. Select Reset filters to clear conversation state. Results reference article IDs from the loaded corpus. Search is lexical unless the optional multilingual embedding model was loaded successfully.

## Frequently asked questions
**Why is Health absent?** The approved BBC training dataset contains five categories and no labeled Health category.  
**Why no topic timeline?** BBC rows do not include trusted publication dates.  
**Does sentiment measure bias or truth?** No. It estimates linguistic tone.  
**Why are translation or semantic search unavailable?** The optional packages and network/model downloads were not enabled.  
**Can I trust a high probability?** No. Inspect the model's errors and validate on new publishers.

## Troubleshooting
An error saying “Train a model first” means run `python train.py --csv "data/raw/BBC News Train.csv"`. A missing spaCy pipeline requires `python -m spacy download en_core_web_sm`. A missing dependency requires installation from `requirements.txt` inside a clean environment. Do not re-use arbitrary external joblib or pickle files.
