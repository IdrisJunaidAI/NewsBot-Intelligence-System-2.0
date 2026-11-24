(() => {
  'use strict';
  const select = document.getElementById('bbc_channel');
  const reload = document.getElementById('bbc_refresh');
  const message = document.getElementById('bbc_feed_status');
  const host = document.getElementById('bbc_headline_cards');
  const official = 'https://www.bbc.com/news';
  let pending = false;
  const add = (parent, tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = String(text);
    parent.appendChild(el);
    return el;
  };
  async function loadHeadlines() {
    if (pending) return;
    pending = true;
    reload.disabled = true;
    host.replaceChildren();
    message.textContent = 'Loading BBC News headlines…';
    try {
      const res = await fetch('/api/bbc/headlines?channel=' + encodeURIComponent(select.value),
        {cache:'no-store'});
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'RSS feed unavailable');
      const items = Array.isArray(data.articles) ? data.articles : [];
      message.textContent = items.length + ' headlines from BBC News official RSS';
      if (!items.length) throw new Error('No headlines returned');
      items.forEach(item => {
        const card = add(host,'article','bbc-headline-card');
        add(card,'span','bbc-source-label','BBC NEWS  ·  ' + select.options[select.selectedIndex].text);
        const title = add(card,'h3','bbc-article-title');
        const link = add(title,'a','',item.title);
        link.href = item.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        if (item.published) add(card,'span','bbc-date',item.published);
        const credit = add(card,'a','bbc-attribution','Read original at BBC News');
        credit.href = item.url;
        credit.target = '_blank';
        credit.rel = 'noopener noreferrer';
      });
    } catch(error) {
      message.textContent = 'Live BBC RSS could not be loaded right now.';
      const card = add(host,'div','bbc-headline-card bbc-feed-error');
      add(card,'p','',error.message);
      const link = add(card,'a','bbc-attribution','Open BBC News directly');
      link.href = official;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    } finally {
      pending = false;
      reload.disabled = false;
    }
  }
  reload.addEventListener('click',loadHeadlines);
  select.addEventListener('change',loadHeadlines);
  loadHeadlines();
})();
