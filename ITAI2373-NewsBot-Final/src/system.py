"""NewsBot 2.0: cohesive analysis engine with explicit provenance and capability status."""
from config.settings import Settings
from src.data_processing.data_validator import load_news_csv,quality_report
from src.analysis.classifier import NewsClassifier
from src.analysis.topic_modeler import TopicModeler
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.ner_extractor import EntityExtractor
from src.language_models.summarizer import NewsSummarizer
from src.language_models.embeddings import SemanticSearch
from src.language_models.generator import InsightGenerator
from src.multilingual.language_detector import LanguageDetector
from src.multilingual.translator import Translator
from src.multilingual.cross_lingual_analyzer import CrossLingualAnalyzer
from src.conversation.query_processor import QueryProcessor

class NewsBotSystem:
    def __init__(self,settings=None,use_embeddings=False):
        self.settings=settings or Settings()
        self.classifier=NewsClassifier(max_features=self.settings.max_features,seed=self.settings.seed)
        self.topics=TopicModeler(n_topics=self.settings.n_topics,seed=self.settings.seed)
        self.sentiment=SentimentAnalyzer();self.entities=EntityExtractor()
        self.summarizer=NewsSummarizer();self.search=SemanticSearch(use_embeddings=use_embeddings)
        self.languages=LanguageDetector();self.translator=Translator();self.generator=InsightGenerator()
        self.multilingual=CrossLingualAnalyzer(self.search, self.languages, self.translator);self.conversation=QueryProcessor(self)
        self.df=None;self.source='not loaded';self.bbc_classifier=None
    def fit_csv(self,path,source=None):
        self.df=load_news_csv(path)
        self.source=source or str(path)
        self.classifier.fit(self.df,source=self.source)
        self.topics.fit(self.df.text)
        self.search.fit(self.df)
        return self
    def analyze(self,text):
        if not isinstance(text,str) or len(text.strip())<30:
            raise ValueError('Please enter an article of at least 30 characters')
        if len(text)>self.settings.max_input_characters:raise ValueError('Article is too long')
        bbc=getattr(self,'bbc_classifier',None)
        classification=bbc.predict(text) if bbc is not None else self.classifier.predict(text)
        detected_language=self.languages.detect(text)
        language_out_of_domain=detected_language['language']!='en'
        analysis={'classification':classification,'sentiment':self.sentiment.analyze(text),
             'language':detected_language,'summary':self.summarizer.summarize(text),
             'entities':self.entities.extract(text),'relations':self.entities.relationships(text),
             'topics':self.topics.topics_for(text),
             'needs_human_review':(classification['model_probability']<self.settings.low_confidence_threshold or language_out_of_domain),
             'language_limitation':('The category classifier and VADER sentiment are intended for English text; results for another or uncertain language are out of domain and require review. Use consent based translation if appropriate.' if language_out_of_domain else None),
             'model_source':('BBC News Train.csv, 1440 distinct labeled articles' if bbc is not None else self.source),
             'corpus_source':self.source,
             'source_note':('Category model uses historical BBC data; corpus search and topic model use the separate synthetic demo corpus.' if bbc is not None else 'All models use the same loaded corpus.')}
        return analysis
    def corpus_stats(self):return quality_report(self.df)
    def ask(self,query,context=None):return self.conversation.process(query,context)
