"""Render traceable conversational responses."""
def format_response(payload):
    ids=[str(r['article_id']) for r in payload.get('articles',[])]
    return {'answer':payload.get('answer',''),'source_article_ids':ids,
            'method':'retrieval grounded / intent rules','context':payload.get('context',{})}
