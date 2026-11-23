/* No external charting libraries, tokens, or raw HTML insertion. */
(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const node = (tag, className, value) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined && value !== null) element.textContent = String(value);
    return element;
  };
  const add = (parent, tag, className, value) => {
    const element = node(tag, className, value);
    parent.appendChild(element);
    return element;
  };
  let data = null;
  let selectedTopic = 'NMF';

  function renderBars(container, dataPoints, options = {}) {
    container.replaceChildren();
    if (!Array.isArray(dataPoints) || !dataPoints.length) {
      add(container, 'p', 'empty-chart', options.empty || 'Not available for this collection.');
      return;
    }
    const maximum = Math.max(1, ...dataPoints.map(p => Number(p.count || p.articles || 0)));
    const total = Math.max(1, dataPoints.reduce((sum, p) => sum + Number(p.count || p.articles || 0), 0));
    dataPoints.slice(0, options.limit || 8).forEach((point, index) => {
      const name = point.label || point.period || ('Topic ' + (point.id + 1));
      const count = Number(point.count ?? point.articles ?? 0);
      const share = Number(point.percentage ?? (count * 100 / total));
      const row = add(container, 'div', 'bar-group');
      const heading = add(row, 'div', 'bar-title');
      add(heading, 'span', 'bar-label', name);
      add(heading, 'strong', 'bar-count', count + '  |  ' + share.toFixed(1) + '%');
      const track = add(row, 'div', 'bar-track');
      const bar = add(track, 'div', 'bar-fill bar-color-' + (index % 5));
      bar.style.width = Math.max(0, Math.min(100, count * 100 / maximum)) + '%';
      track.setAttribute('role', 'img');
      track.setAttribute('aria-label', name + ': ' + count + ' articles');
    });
  }

  function renderTopics() {
    const container = byId('topic_chart');
    container.replaceChildren();
    if (!data) return;
    const topics = data.topics?.[selectedTopic] || [];
    const maximum = Math.max(1, ...topics.map(t => t.articles));
    if (!topics.length) {
      add(container, 'p', 'empty-chart', 'No topic model available.');
      return;
    }
    topics.forEach(topic => {
      const card = add(container, 'div', 'topic-row');
      const head = add(card, 'div', 'topic-title');
      add(head, 'strong', '', 'Topic ' + (Number(topic.id) + 1));
      add(head, 'span', 'meta', topic.articles + ' articles');
      add(card, 'p', 'topic-keywords', (topic.keywords || []).join(' · '));
      const track = add(card, 'div', 'bar-track topic-track');
      const fill = add(track, 'div', 'bar-fill');
      fill.style.width = Math.max(0, Math.min(100, 100 * topic.articles / maximum)) + '%';
    });
  }

  function renderKpis(snapshot) {
    const host = byId('dashboard_kpis');
    host.replaceChildren();
    const metrics = [
      ['Stored articles', snapshot.meta.articles.toLocaleString(), 'Current corpus only'],
      ['News categories', snapshot.meta.category_count, 'Distinct category labels'],
      ['Articles with dates', snapshot.meta.dated_articles.toLocaleString(), 'Recorded metadata, not live'],
      ['Retrieval', snapshot.meta.search_method.includes('multilingual sentence') ? 'MiniLM' : (snapshot.meta.search_method.includes('LSA') ? 'LSA' : 'TF IDF'),
       snapshot.meta.search_method.includes('multilingual sentence') ? 'Neural semantic similarity' : (snapshot.meta.search_method.includes('LSA') ? 'Latent semantic indexing' : 'Lexical search')]
    ];
    metrics.forEach(([label, number, qualifier]) => {
      const tile = add(host, 'article', 'kpi-card');
      add(tile, 'span', 'kpi-label', label);
      add(tile, 'strong', 'kpi-number', number);
      add(tile, 'span', 'kpi-qualifier', qualifier);
    });
  }

  function renderQuality(snapshot) {
    const panel = byId('evaluation_panel');
    panel.replaceChildren();
    const evalData = snapshot.evaluation || {};
    add(panel, 'p', 'quality-lead', snapshot.meta.synthetic ?
      'Demonstration model evaluation' : 'Internal training corpus evaluation');
    const row = add(panel, 'div', 'quality-metrics');
    const scores = [
      ['Held out accuracy', evalData.holdout_accuracy],
      ['Macro F1 score', evalData.holdout_macro_f1]
    ];
    scores.forEach(([label, value]) => {
      const tile = add(row, 'div', 'quality-metric');
      add(tile, 'span', 'meta', label);
      add(tile, 'strong', '', typeof value === 'number' ? (value * 100).toFixed(1) + '%' : 'Unavailable');
    });
    add(panel, 'p', 'quality-explainer', evalData.interpretation || 'Evaluation details unavailable.');
    if (Array.isArray(evalData.cross_validation) && evalData.cross_validation.length) {
      add(panel, 'h4', 'small-heading', 'Training set model comparison');
      const list = add(panel, 'div', 'comparison-list');
      evalData.cross_validation.forEach(item => {
        const row = add(list, 'div', 'comparison-row');
        add(row, 'span', '', item.model);
        add(row, 'strong', '', (100 * item.cv_macro_f1).toFixed(1) + '% macro F1');
      });
    }
    add(panel, 'p', 'meta', 'Held out evaluation size: ' + (evalData.holdout_count || 0) + ' articles');
    const bbc = snapshot.bbc_classifier;
    if (bbc && bbc.active) {
      const section = add(panel, 'section', 'bbc-evidence');
      add(section, 'h4', 'small-heading', 'Real BBC classification evaluation');
      add(section, 'p', 'quality-lead', bbc.articles_used + ' distinct labeled BBC articles; 288 held out for evaluation.');
      const realMetrics=add(section, 'div', 'quality-metrics');
      [['BBC Logistic accuracy', bbc.heldout_accuracy], ['BBC Logistic macro F1', bbc.heldout_macro_f1],
       ['BBC Linear SVM accuracy (comparison only)', bbc.comparison_svm_accuracy]].forEach(([label,value]) => {
        const tile=add(realMetrics, 'div', 'quality-metric');
        add(tile,'span','meta',label);
        add(tile,'strong','', (100*Number(value)).toFixed(2)+'%');
      });
      add(section, 'p', 'result-notice', bbc.note);
    }
  }

  function render(snapshot) {
    data = snapshot;
    const notice = byId('corpus_notice');
    notice.replaceChildren();
    add(notice, 'strong', '', snapshot.meta.corpus + '. ');
    add(notice, 'span', '', snapshot.meta.disclaimer);
    if (snapshot.bbc_classifier?.active) {
      add(notice, 'p', 'quality-lead',
          'Article category classification uses a real BBC trained model. The searchable articles, topic charts and corpus statistics remain synthetic demonstrations. This is not live news.');
    }
    const status = byId('dashboard_status');
    status.replaceChildren();
    add(status, 'span', 'data-indicator', snapshot.meta.synthetic ? 'Synthetic data' : 'User supplied corpus');
    add(status, 'span', 'meta', 'Data source: ' + snapshot.meta.source);
    renderKpis(snapshot);
    renderBars(byId('category_chart'), snapshot.categories);
    renderBars(byId('sentiment_chart'), snapshot.sentiments);
    renderQuality(snapshot);
    const timeline = (snapshot.timeline || []).map(d => ({label: d.period, count: d.articles}));
    renderBars(byId('timeline_chart'), timeline, {empty: 'Publication date information was not supplied.', limit: 6});
    renderTopics();
  }

  async function load() {
    const status = byId('dashboard_status');
    status.textContent = 'Loading corpus analytics…';
    try {
      const response = await fetch('/api/dashboard', {cache: 'no-store'});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || 'Analytics request failed');
      render(payload);
    } catch (error) {
      status.replaceChildren();
      add(status, 'p', 'result-error', 'Analytics unavailable: ' + error.message);
      byId('export_link').setAttribute('aria-disabled', 'true');
    }
  }

  document.querySelectorAll('[data-topic-method]').forEach(button => {
    button.addEventListener('click', () => {
      selectedTopic = button.dataset.topicMethod;
      document.querySelectorAll('[data-topic-method]').forEach(other => {
        const active = other.dataset.topicMethod === selectedTopic;
        other.classList.toggle('active', active);
        other.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
      renderTopics();
    });
  });
  load();
})();
