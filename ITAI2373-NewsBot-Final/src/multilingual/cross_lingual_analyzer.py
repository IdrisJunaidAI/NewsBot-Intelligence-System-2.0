"""Cross language search requires multilingual embeddings; no lexical-only claims."""
class CrossLingualAnalyzer:
    def __init__(self,search):self.search_engine=search
    def compare(self,query,top_k=5):
        if self.search_engine.method!='multilingual sentence embeddings':
            return {'available':False,'reason':'Enable multilingual sentence embeddings for genuine cross-language retrieval'}
        result=self.search_engine.search(query,top_k=top_k)
        return {'available':True,'method':result['method'],'matches':result['results'],
                'note':'Cross-language relevance does not prove cultural interpretation; human review required'}
