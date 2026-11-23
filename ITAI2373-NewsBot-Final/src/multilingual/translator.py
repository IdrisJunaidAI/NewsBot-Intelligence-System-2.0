"""Explicit opt-in translation using an optional external provider.

No claim is made that the provider is private, always available or offline.
A translation request sends the supplied text to the provider.
"""
import importlib.util

ALLOWED = frozenset({'en', 'es', 'fr'})


class Translator:
    def __init__(self, provider_factory=None):
        self.provider_factory = provider_factory

    def status(self):
        installed = self.provider_factory is not None or importlib.util.find_spec('deep_translator') is not None
        return {'installed': bool(installed), 'ready': 'requires explicit consent and an online provider request',
                'languages': sorted(ALLOWED), 'provider': 'deep-translator GoogleTranslator',
                'privacy': 'The text is sent to an external service; do not send sensitive or confidential articles',
                'translation_quality': 'Not independently evaluated; named entities, nuance and context can be altered'}

    def translate(self, text, source='auto', target='en', external_consent=False):
        if not isinstance(text, str) or not text.strip():
            raise ValueError('A nonempty text is required')
        text = text.strip()
        if len(text) > 2000:
            raise ValueError('Maximum translation input is 2000 characters')
        if source not in (ALLOWED | {'auto'}) or target not in ALLOWED:
            raise ValueError('English, Spanish and French are the supported translation languages')
        if source == target:
            return {'available': True, 'text': text, 'provider': 'identity, no translation required',
                    'source': source, 'target': target, 'external_service_used': False,
                    'note': 'No machine translation performed'}
        if not external_consent:
            return {'available': False, 'text': None, 'source': source, 'target': target,
                    'reason': 'Consent required before text is sent to an external translation service',
                    'external_service_used': False}
        factory = self.provider_factory
        if factory is None:
            try:
                from deep_translator import GoogleTranslator
                factory = GoogleTranslator
            except ImportError:
                return {'available': False, 'text': None, 'source': source, 'target': target,
                        'reason': 'Optional deep-translator dependency is not installed',
                        'external_service_used': False}
        try:
            result = factory(source=source, target=target).translate(text)
            if not isinstance(result, str) or not result.strip():
                raise RuntimeError('Empty translation result')
            return {'available': True, 'text': result.strip(), 'provider': 'GoogleTranslator through deep-translator',
                    'source': source, 'target': target, 'external_service_used': True,
                    'note': 'Machine translated; verify proper names, meaning and local context'}
        except Exception as exc:
            # Never echo third-party exception strings: they may contain user text.
            return {'available': False, 'text': None, 'source': source, 'target': target,
                    'external_service_used': True,
                    'reason': 'External provider request failed (' + type(exc).__name__ + '); retry or use offline language detection'}
