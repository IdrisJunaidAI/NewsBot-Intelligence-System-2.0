/* Rubric bonus UI: real recorded BBC low-data experiment and bounded batch analysis.
   Safe DOM creation only: no HTML insertion, remote dependencies, or simulated results. */
(() => {
  'use strict';
  const node = id => document.getElementById(id);
  const add = (parent, tag, css, value) => {
    const child = document.createElement(tag);
    if (css) child.className = css;
    if (value !== undefined && value !== null) child.textContent = String(value);
    parent.appendChild(child);
    return child;
  };
  const chart = node('bonus_research_chart');
  const metric = node('bonus_metric');
  const note = node('bonus_research_note');
  let published = null;

  function drawCurve(data) {
    chart.replaceChildren();
    const isAccuracy = metric.value === 'accuracy';
    const suffix = isAccuracy ? 'accuracy' : 'macro_f1';
    const graph = add(chart, 'div', 'bonus-curve');
    data.points.forEach(point => {
      const mean = Number(point['mean_' + suffix]);
      const sd = Number(point['sd_' + suffix]);
      const row = add(graph, 'div', 'bonus-curve-row');
      const label = add(row, 'div', 'bonus-curve-head');
      add(label, 'strong', '', point.per_class_samples + ' articles per category');
      add(label, 'span', '', (mean * 100).toFixed(2) + '% ± ' + (sd * 100).toFixed(2) + '%');
      const track = add(row, 'div', 'bonus-curve-track');
      track.setAttribute('role', 'img');
      track.setAttribute('aria-label', point.per_class_samples + ' articles per category: mean '
        + (mean * 100).toFixed(2) + ' percent, standard deviation '
        + (sd * 100).toFixed(2) + ' percent across five seeds');
      const bar = add(track, 'div', 'bonus-curve-bar');
      bar.style.width = Math.max(0, Math.min(100, mean * 100)) + '%';
    });
  }

  async function loadResearch() {
    try {
      const response = await fetch('/api/research/fewshot', {cache:'no-store'});
      const result = await response.json();
      if (!response.ok || !result.available || !Array.isArray(result.points))
        throw new Error(result.error || 'Measured data could not be loaded');
      published = result;
      drawCurve(result);
      note.replaceChildren();
      add(note, 'strong', '', result.study);
      add(note, 'p', '', result.methods);
      add(note, 'p', '', 'Total recorded runs: ' + result.total_model_fits
        + '. Fixed holdout: ' + result.heldout_articles + ' BBC articles.');
      add(note, 'p', 'meta', result.limits);
    } catch (error) {
      chart.replaceChildren();
      add(chart,'p','result-error','Research results unavailable: '+error.message);
      note.textContent = 'Open the measured evidence CSV in the GitHub repository to review the source data.';
    }
  }

  metric.addEventListener('change', () => {
    if (published) drawCurve(published);
  });
  loadResearch();

  const button = node('bonus_batch_run');
  const results = node('bonus_batch_results');
  const field = node('bonus_batch_text');

  async function analyzeBatch() {
    const excerpts = field.value.split(/^\s*={3,}\s*$/m).map(x => x.trim()).filter(Boolean);
    results.replaceChildren();
    if (excerpts.length < 2 || excerpts.length > 5) {
      add(results,'p','result-error','Provide 2 to 5 article excerpts separated by === on its own line.');
      return;
    }
    if (excerpts.some(x => x.length < 30 || x.length > 5000) ||
        excerpts.reduce((sum,x)=>sum+x.length,0)>15000) {
      add(results,'p','result-error','Each article must contain 30 to 5000 characters, with 15000 characters total.');
      return;
    }
    button.disabled = true;
    window.NewsBotUI?.setLoading('bonus_batch_results',true);
    add(results, 'p', 'meta', 'Analyzing submitted articles…');
    try {
      const response = await fetch('/api/batch/analyze', {
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({articles:excerpts})
      });
      const data = await response.json();
      if (!response.ok || !Array.isArray(data.results))
        throw new Error(data.error || 'Batch analysis unavailable');
      results.replaceChildren();
      add(results, 'p','answer',data.processed + ' article analyses completed');
      add(results, 'p','meta',data.disclaimer);
      const grid = add(results, 'div', 'bonus-batch-results-grid');
      data.results.forEach(item => {
        const card = add(grid,'article','article-hit');
        add(card,'h3','','Article ' + item.article_number);
        add(card,'p','bonus-metric-line','Category: ' + (item.category || 'Unknown'));
        add(card,'p','bonus-metric-line','Sentiment: ' + (item.sentiment || 'Unknown')
          + ' | Language: ' + (item.language || 'Unknown'));
        add(card,'p','meta','Model probability (uncalibrated): ' +
          (typeof item.model_probability === 'number' ?
            (item.model_probability*100).toFixed(1)+'%' : 'Unavailable'));
        if (item.needs_human_review)
          add(card,'p','result-notice','Human review recommended. ' + (item.language_limitation || ''));
        add(card,'p','',item.summary || 'No extractive summary available');
      });
    } catch (error) {
      results.replaceChildren();
      add(results,'p','result-error','Unable to complete batch analysis: '+error.message);
    } finally {
      button.disabled = false;
      window.NewsBotUI?.setLoading('bonus_batch_results',false);
    }
  }
  button.addEventListener('click',analyzeBatch);
})();
