"""True shared-vector retrieval OR transparently labeled translation-assisted search."""


class CrossLingualAnalyzer:
    def __init__(self, search, detector=None, translator=None):
        self.search_engine = search
        self.detector = detector
        self.translator = translator

    def compare(self, query, top_k=5, mode='semantic', external_consent=False):
        if not isinstance(query, str) or len(query.strip()) < 4:
            raise ValueError('Please enter a meaningful search query')
        if mode not in ('semantic', 'translated'):
            raise ValueError('Mode must be semantic or translated')
        if not isinstance(top_k, int) or not 1 <= top_k <= 10:
            raise ValueError('top_k must be between 1 and 10')
        query = query.strip()
        if len(query) > 500:
            raise ValueError('Maximum search query length is 500 characters')
        detection = self.detector.detect(query) if self.detector else {'language': 'unknown'}
        if mode == 'semantic':
            if self.search_engine.method != 'multilingual sentence embeddings':
                return {'available': False, 'mode': 'semantic', 'language': detection,
                        'reason': 'True cross-language semantic retrieval requires the optional multilingual Sentence Transformers encoder. Use the Colab notebook or enable and install the model in a capable environment.',
                        'external_service_used': False}
            results = self.search_engine.search(query, top_k=top_k)
            return {'available': True, 'mode': 'semantic', 'language': detection,
                    'method': results['method'], 'matches': results['results'],
                    'external_service_used': False,
                    'note': 'Shared multilingual embedding space; relevance is an estimate, not fact verification'}
        if self.translator is None or self.detector is None:
            return {'available': False, 'mode': 'translated',
                    'reason': 'Language detector or translator is unavailable'}
        code = detection['language']
        if code == 'unknown':
            return {'available': False, 'mode': 'translated', 'language': detection,
                    'reason': 'Language uncertain; use a longer English, Spanish or French query'}
        if code not in {'en', 'es', 'fr'}:
            return {'available': False, 'mode': 'translated', 'language': detection,
                    'reason': 'This demonstration supports English, Spanish and French queries'}
        if code == 'en':
            query_en = query
            translation = None
        else:
            translation = self.translator.translate(query, source=code, target='en',
                                                    external_consent=external_consent)
            if not translation['available']:
                return {'available': False, 'mode': 'translated', 'language': detection,
                        'reason': translation['reason'],
                        'external_service_used': translation.get('external_service_used', False)}
            query_en = translation['text']
        search_mode = 'lsa' if getattr(self.search_engine, 'lsa_available', False) else 'lexical'
        results = self.search_engine.search(query_en, top_k=top_k, mode=search_mode)
        return {'available': True, 'mode': 'translated', 'language': detection,
                'translated_query': query_en if translation else None,
                'method': 'Translation-assisted ' + results['method'],
                'matches': results['results'],
                'external_service_used': bool(translation and translation.get('external_service_used')),
                'note': 'Cross-language access is via translation to English and latent/lexical retrieval, NOT shared multilingual transformer embeddings. Translation quality is unverified.'}
