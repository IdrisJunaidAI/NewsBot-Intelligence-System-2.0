"""Cited, structured insight generation (non-LLM); avoids ungrounded factual claims."""
class InsightGenerator:
    def explain(self,article_id,analysis):
        category=analysis['classification']['category']
        tone=analysis['sentiment']['label']
        return {'article_id':article_id,
            'insight':f'Article {article_id} is categorized as {category}; its text tone is estimated as {tone}.',
            'limits':'An analytical signal, not independent fact checking or regulatory advice',
            'generation_type':'grounded template, not generative language model'}
