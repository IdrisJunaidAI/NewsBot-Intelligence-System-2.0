"""Train models on the approved BBC source or explicitly illustrative demo data."""
import argparse,json
from pathlib import Path
import joblib
from config.settings import Settings
from src.system import NewsBotSystem
from src.utils.export import export_json

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--csv',default=None,help='Input labeled CSV, preferably instructor-approved BBC training data')
    p.add_argument('--demo',action='store_true',help='Use small hand-written synthetic teaching examples')
    p.add_argument('--embeddings',action='store_true',help='Use optional multilingual embeddings if available')
    args=p.parse_args()
    if not args.csv and not args.demo:p.error('Supply --csv PATH or explicitly select --demo')
    settings=Settings();source='DEMO SYNTHETIC DATA ONLY' if args.demo else 'USER SUPPLIED DATASET'
    path=settings.demo_path if args.demo else args.csv
    bot=NewsBotSystem(use_embeddings=args.embeddings).fit_csv(path,source=source)
    settings.model_path.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump(bot,settings.model_path)
    export_json({'provenance':source,'classifier_evaluation':bot.classifier.metrics,
                 'corpus':bot.corpus_stats(),'topic_words':bot.topics.top_words(),
                 'retrieval_method':bot.search.method},settings.model_path.parent.parent/'results'/'training_metrics.json')
    print(json.dumps({'training_mode':source,'articles':len(bot.df),'model_path':str(settings.model_path),
                     'retrieval_method':bot.search.method,'classification_holdout':bot.classifier.metrics['logistic_heldout_accuracy']},indent=2))
    print('Do not compare synthetic demonstration metrics to documented BBC midterm accuracy.')
