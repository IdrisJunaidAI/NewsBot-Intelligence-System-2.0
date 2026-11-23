/* Multilingual NewsBot lab. Text reaches external translation only on opt-in. */
(() => {
  'use strict';
  const get = id => document.getElementById(id);
  function create(tag, text, cls) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }
  function message(parent, text, cls = 'meta') {
    parent.appendChild(create('p', text, cls));
  }
  function renderResults(payload) {
    const out = get('ml_search_results');
    out.replaceChildren();
    if (!payload.available) {
      message(out, payload.reason || 'Retrieval is unavailable in this environment.', 'result-notice');
      return;
    }
    message(out, payload.method || 'Retrieval method not stated', 'answer');
    if (payload.language?.language_name) message(out, 'Detected query language: ' + payload.language.language_name);
    if (payload.translated_query) message(out, 'English query sent to search: ' + payload.translated_query);
    if (payload.note) message(out, payload.note, 'result-notice');
    if (!payload.matches?.length) {
      message(out, 'No supported matching articles in the stored teaching collection.');
      return;
    }
    payload.matches.forEach(result => {
      const card = create('article', undefined, 'article-hit');
      card.appendChild(create('strong', result.category + ' | ' + result.article_id));
      card.appendChild(create('p', result.snippet || 'No snippet available'));
      message(card, 'Similarity: ' + Number(result.score).toFixed(3));
      out.appendChild(card);
    });
  }
  async function request(path, payload, target, renderer) {
    const out = get(target);
    out.replaceChildren(create('p', 'Processing…'));
    try {
      const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)});
      const result = await response.json();
      if (!response.ok && !('available' in result)) throw new Error(result.error || 'Request failed');
      renderer(result);
    } catch (error) {
      out.replaceChildren();
      message(out, 'Unable to complete request: ' + error.message, 'result-error');
    }
  }
  const consent = () => get('ml_consent').checked;
  get('ml_detect').addEventListener('click', () => {
    const text = get('ml_text').value.trim();
    request('/api/multilingual/detect', {text}, 'ml_result', result => {
      const out = get('ml_result'); out.replaceChildren();
      message(out, 'Detected language: ' + result.language_name + ' (' + result.language + ')', 'answer');
      message(out, result.method);
      message(out, result.note, 'meta');
    });
  });
  get('ml_translate').addEventListener('click', () => {
    const text = get('ml_text').value.trim();
    request('/api/multilingual/translate', {text, source:'auto', target:get('ml_target').value,
      external_consent:consent()}, 'ml_result', result => {
        const out = get('ml_result'); out.replaceChildren();
        if (!result.available) { message(out, result.reason, 'result-notice'); return; }
        message(out, result.text, 'answer');
        message(out, result.provider + (result.external_service_used ? ' | external service' : ' | local identity'));
        message(out, result.note, 'meta');
      });
  });
  get('ml_search').addEventListener('click', () => {
    const query = get('ml_query').value.trim();
    request('/api/multilingual/search', {query, mode:get('ml_mode').value,
      external_consent:consent()}, 'ml_search_results', renderResults);
  });
  get('ml_compare').addEventListener('click', () => {
    const query = get('ml_query').value.trim();
    request('/api/retrieval/compare', {query}, 'ml_search_results', result => {
      const out = get('ml_search_results'); out.replaceChildren();
      if (result.error) {message(out, result.error, 'result-error'); return;}
      ['lexical', 'lsa'].forEach(method => {
        const section = create('section', undefined, 'article-hit');
        section.appendChild(create('strong', result[method]?.method || method));
        message(section, (result[method]?.results || []).map(x => x.article_id + ': ' + x.score.toFixed(3)).join(' | ') || 'No matches');
        out.appendChild(section);
      });
      message(out, 'Latent semantic indexing captures corpus co-occurrence; it is not a multilingual transformer.');
    });
  });
  fetch('/api/multilingual/status', {cache:'no-store'}).then(r => r.json()).then(status => {
    const target = get('ml_status'); target.replaceChildren();
    message(target, 'Languages: English, Spanish and French | Latent semantic indexing: ' +
      (status.lsa_active ? 'available' : 'unavailable') + ' | multilingual transformer: ' +
      (status.multilingual_embeddings_active ? 'enabled' : 'requires separate model environment'));
    message(target, 'External translation is optional. Provider installed: ' +
      (status.translation?.installed ? 'yes' : 'no') + '. Translation success must be confirmed per request.');
  }).catch(() => {
    message(get('ml_status'), 'Capability status unavailable');
  });
})();
