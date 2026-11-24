// Render API data as accessible text nodes, never as unescaped HTML or raw JSON.
const el = id => document.getElementById(id);
function make(tag, className, value) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (value !== undefined && value !== null) item.textContent = String(value);
  return item;
}
function add(parent, tag, className, value) {
  const child = make(tag, className, value);
  parent.appendChild(child);
  return child;
}
function displayError(target, message) {
  const out = el(target);
  out.replaceChildren();
  add(out, 'p', 'result-error', message);
}
function displayArticle(parent, article) {
  const card = add(parent, 'article', 'article-hit');
  const head = add(card, 'div', 'hit-heading');
  add(head, 'strong', '', article.category ? article.category.toUpperCase() : 'Article');
  add(head, 'span', 'meta', 'Article ID: ' + (article.article_id || 'Unknown'));
  if (article.snippet) add(card, 'p', 'hit-snippet', article.snippet);
  const meta = add(card, 'div', 'hit-meta');
  if (article.source) add(meta, 'span', 'meta', 'Source: ' + article.source);
  if (article.date) add(meta, 'span', 'meta', 'Recorded date: ' + article.date.slice(0, 10));
  if (typeof article.score === 'number') {
    add(meta, 'span', 'meta', 'Similarity: ' + article.score.toFixed(3));
  } else {
    add(meta, 'span', 'meta', 'Category browse, not a similarity match');
  }
}
function renderQuestion(body) {
  const out = el('chat_out');
  out.replaceChildren();
  add(out, 'p', 'answer', body.answer || 'No answer was returned.');
  if (body.notice) add(out, 'p', 'result-notice', body.notice);
  if (body.note) add(out, 'p', 'meta', body.note);
  if (Array.isArray(body.articles) && body.articles.length) {
    add(out, 'h3', 'results-title', 'Articles in the loaded collection');
    body.articles.forEach(a => displayArticle(out, a));
  }
  if (Array.isArray(body.topics) && body.topics.length) {
    add(out, 'h3', 'results-title', 'Discovered topics');
    body.topics.forEach(t => add(out, 'p', 'topic-line',
      'Topic ' + (Number(t.topic) + 1) + ': ' + (t.words || []).join(', ')));
  }
  if (body.context && (body.context.category || body.context.sentiment)) {
    const filters = [body.context.category, body.context.sentiment].filter(Boolean);
    add(out, 'p', 'meta', 'Active filters: ' + filters.join(', '));
  }
}
function renderAnalysis(body) {
  const out = el('analyze_out');
  out.replaceChildren();
  const c = body.classification || {};
  const s = body.sentiment || {};
  const language = body.language || {};
  const summary = body.summary || {};
  const entities = body.entities || {};
  const grid = add(out, 'div', 'metric-grid');
  function metric(label, value) {
    const item = add(grid, 'div', 'metric');
    add(item, 'span', 'meta', label);
    add(item, 'strong', 'metric-value', value || 'Not available');
  }
  metric('Category', c.category);
  metric('Sentiment', s.label);
  metric('Language', language.language);
  metric('Model probability', typeof c.model_probability === 'number'
    ? (c.model_probability * 100).toFixed(1) + '%' : '');
  if (body.language_limitation) add(out, 'p', 'result-notice', body.language_limitation);
  if (body.needs_human_review) {
    add(out, 'p', 'result-notice',
      'This classification falls below the review threshold. Human review is recommended.');
  }
  add(out, 'p', 'meta', 'Model probability is not calibrated certainty.');
  if (summary.summary) {
    add(out, 'h3', 'results-title', 'Extractive summary');
    add(out, 'p', 'summary-text', summary.summary);
  }
  if (Array.isArray(body.topics) && body.topics.length) {
    add(out, 'h3', 'results-title', 'Topic weights');
    add(out, 'p', 'topic-line', body.topics.map(t =>
      'Topic ' + (Number(t.topic) + 1) + ': ' + t.weight).join('  |  '));
  }
  if (entities.available && Array.isArray(entities.entities)) {
    add(out, 'h3', 'results-title', 'Named entities');
    if (!entities.entities.length) add(out, 'p', 'meta', 'No named entities identified.');
    const chips = add(out, 'div', 'entity-list');
    entities.entities.forEach(e => add(chips, 'span', 'entity-chip',
      e.text + ' (' + e.label + ')'));
  } else if (entities.reason) {
    add(out, 'p', 'meta', entities.reason);
  }
  if (body.model_source) add(out, 'p', 'meta', 'Category classifier training: ' + body.model_source);
  if (body.corpus_source) add(out, 'p', 'meta', 'Topic and search corpus: ' + body.corpus_source);
  if (body.source_note) add(out, 'p', 'result-notice', body.source_note);
  add(out, 'p', 'meta', 'Automated analysis is not independent fact verification.');
}
async function send(url, payload, target, mode) {
  const out = el(target);
  window.NewsBotUI?.setLoading(target,true);
  out.replaceChildren(add(document.createElement('div'), 'p', 'meta', 'Processing request…'));
  try {
    const response = await fetch(url, {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Request failed');
    if (mode === 'question') renderQuestion(data);
    else if (mode === 'analysis') renderAnalysis(data);
    else { out.replaceChildren(); add(out, 'p', 'answer', 'Conversation filters reset.'); }
  } catch (error) { displayError(target, 'Unable to complete request: ' + error.message); }
  finally { window.NewsBotUI?.setLoading(target,false); }
}
el('analyze').addEventListener('click', () => {
  const text = el('article').value.trim();
  if (text.length < 30) {
    displayError('analyze_out', 'Enter at least 30 characters from a news article to run analysis.');
    el('article').focus(); return;
  }
  send('/api/analyze', {text}, 'analyze_out', 'analysis');
});
el('ask').addEventListener('click', () => {
  const query = el('query').value.trim();
  if (!query) {
    displayError('chat_out', 'Enter a question or choose an example.');
    el('query').focus(); return;
  }
  send('/api/query', {query}, 'chat_out', 'question');
});
el('query').addEventListener('keydown', e => {
  if (e.key === 'Enter') { e.preventDefault(); el('ask').click(); }
});
el('reset').addEventListener('click', () => send('/api/clear', {}, 'chat_out', 'clear'));
document.querySelectorAll('[data-example-query]').forEach(button => {
  button.addEventListener('click', () => {
    el('query').value = button.dataset.exampleQuery;
    el('ask').click();
  });
});
