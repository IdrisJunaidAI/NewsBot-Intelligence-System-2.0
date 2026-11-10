from src.multilingual.language_detector import LanguageDetector
from src.multilingual.translator import Translator

def test_english_detection():
    result=LanguageDetector().detect('The government and the market announced new plans for companies and employment.')
    assert result['language']=='en'

def test_translation_unavailable_explicitly():
    assert Translator().translate('Bonjour à tous',source='fr',target='fr')['available']
