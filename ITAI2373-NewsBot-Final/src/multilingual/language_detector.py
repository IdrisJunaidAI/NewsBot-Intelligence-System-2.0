"""Deterministic, cautious identification of English, Spanish and French text.

Statistical language ID is inherently uncertain, especially for short,
quoted, multilingual, or highly technical content.
"""
import re

try:
    from langdetect import detect as _detect
    from langdetect import DetectorFactory
    DetectorFactory.seed = 0
except ImportError:
    _detect = None

SUPPORTED_LANGUAGES = {'en': 'English', 'es': 'Spanish', 'fr': 'French'}
_WORDS = {
    'en': set('the and government said with companies market team this is new after for in of their were launched technology economy reported'.split()),
    'es': set('el la los las de que y en para con un una gobierno empresa mercado según noticias tecnología economía anunció se'.split()),
    'fr': set('le la les des de et dans avec pour une un gouvernement entreprises marché selon nouvelles économie technologie annoncé est'.split()),
}


class LanguageDetector:
    def detect(self, text):
        if not isinstance(text, str):
            raise ValueError('Language detection requires text')
        if len(text.strip()) < 20:
            return {'language': 'unknown', 'language_name': 'Unknown', 'supported': False,
                    'method': 'insufficient text', 'note': 'Supply at least 20 characters'}
        language = None
        method = None
        if _detect is not None:
            try:
                language = _detect(text.strip())
                method = 'langdetect statistical model, deterministic seed'
            except Exception:
                pass
        if language is None:
            words = re.findall(r'\b[^\W\d_]+\b', text.lower(), re.UNICODE)
            scores = {key: sum(word in dictionary for word in words) for key, dictionary in _WORDS.items()}
            best = max(scores, key=scores.get)
            language = best if scores[best] >= 2 else 'unknown'
            method = 'limited stopword heuristic, not a trained multilingual model'
        return {'language': language, 'language_name': SUPPORTED_LANGUAGES.get(language, 'Other or unknown'),
                'supported': language in SUPPORTED_LANGUAGES, 'method': method,
                'note': 'Language identification is probabilistic; verify ambiguous or code switched content'}
