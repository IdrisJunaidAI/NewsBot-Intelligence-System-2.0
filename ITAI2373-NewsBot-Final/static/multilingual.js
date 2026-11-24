/* Local multilingual topic search is the default. External translation is optional. */
(() => {
  'use strict';
  const get = id => document.getElementById(id);
  const create = (tag, text, cls) => {
    const element=document.createElement(tag);
    if (cls) element.className=cls;
    if (text!==undefined && text!==null) element.textContent=String(text);
    return element;
  };
  const message = (parent,text,cls='meta') => {
    if(text!==undefined && text!==null) parent.appendChild(create('p',text,cls));
  };
  const consent=()=>get('ml_consent').checked;
  function displayResults(payload) {
    const out=get('ml_search_results');
    out.replaceChildren();
    if (!payload.available) {
      message(out,payload.reason||'Search is unavailable.','result-notice');
      return;
    }
    message(out,payload.method||'Retrieval method not reported','answer');
    if (payload.language?.language_name) message(out,'Input language: '+payload.language.language_name);
    if (payload.normalized_query) message(out,'Offline English topic keywords: '+payload.normalized_query);
    if (payload.translated_query) message(out,'External machine translation: '+payload.translated_query);
    if (payload.fallback_from) message(out,
      'External translation did not succeed. A limited offline topic search was used instead.','result-notice');
    if (payload.warning) message(out,payload.warning,'result-notice');
    if (payload.note) message(out,payload.note,'meta');
    message(out,payload.external_service_used
      ? 'An external translation request was attempted.' : 'No external translation request was made.','meta');
    if (!payload.matches?.length) {
      message(out,'No matching articles from the synthetic English teaching corpus.');
      return;
    }
    payload.matches.forEach(item=>{
      const card=create('article',undefined,'article-hit');
      card.appendChild(create('strong',String(item.category||'Article')+' | '+String(item.article_id||'')));
      card.appendChild(create('p',item.snippet||'No excerpt available'));
      message(card, 'Similarity score: '+Number(item.score).toFixed(3));
      out.appendChild(card);
    });
  }
  async function request(path,body,target,renderer){
    const host=get(target);
    window.NewsBotUI?.setLoading(target,true);
    host.replaceChildren(create('p','Processing request…'));
    try {
      const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body)});
      const result=await response.json();
      if(!response.ok && !('available' in result)) throw new Error(result.error||'Request failed');
      renderer(result);
    } catch(error) {
      host.replaceChildren();
      message(host,'Unable to complete request: '+error.message,'result-error');
    } finally { window.NewsBotUI?.setLoading(target,false); }
  }
  get('ml_detect').addEventListener('click',()=>{
    request('/api/multilingual/detect',{text:get('ml_text').value.trim()},'ml_result',data=>{
      const host=get('ml_result');host.replaceChildren();
      message(host,'Detected language: '+data.language_name+' ('+data.language+')','answer');
      message(host,data.method);
      message(host,data.note);
    });
  });
  get('ml_translate').addEventListener('click',()=>{
    const text=get('ml_text').value.trim();
    request('/api/multilingual/translate',
      {text,source:'auto',target:get('ml_target').value,external_consent:consent()},
      'ml_result',data=>{
        const host=get('ml_result');host.replaceChildren();
        if(!data.available){
          message(host,data.reason||'Translation not available','result-notice');
          if(data.error_code==='rate_limited'){
            message(host,'You can still explore topics using the offline option on the right. Full sentence translation is not available while the external service is limited.');
            const button=create('button','Search news topics offline','secondary');
            button.type='button';
            button.addEventListener('click',()=>{
              get('ml_query').value=text.slice(0,500);
              get('ml_mode').value='offline';
              get('ml_search').click();
            });
            host.appendChild(button);
          }
          return;
        }
        message(host,data.text,'answer');
        message(host,data.provider+(data.external_service_used?' | external service':' | local identity'));
        message(host,data.note);
      });
  });
  get('ml_search').addEventListener('click',()=>{
    const mode=get('ml_mode').value;
    request('/api/multilingual/search',
      {query:get('ml_query').value.trim(),mode,
       external_consent:mode==='translated' && consent()},
      'ml_search_results',displayResults);
  });
  get('ml_compare').addEventListener('click',()=>{
    request('/api/retrieval/compare',{query:get('ml_query').value.trim()},
      'ml_search_results',result=>{
        const host=get('ml_search_results');host.replaceChildren();
        if(result.error){message(host,result.error,'result-notice');return;}
        if(result.normalized_query) message(host,'English retrieval keywords: '+result.normalized_query,'answer');
        if(result.mapping_note) message(host,result.mapping_note,'meta');
        ['lexical','lsa'].forEach(method=>{
          const section=create('section',undefined,'article-hit');
          section.appendChild(create('strong',result[method]?.method||method));
          const hits=(result[method]?.results||[]).map(v=>v.article_id+
            ': '+Number(v.score).toFixed(3));
          message(section,hits.join(' | ')||'No matches');
          host.appendChild(section);
        });
        message(host,'No translation provider was contacted. Comparisons use limited offline keywords for Spanish or French, not a multilingual neural model.');
      });
  });
  fetch('/api/multilingual/status',{cache:'no-store'}).then(response=>response.json()).then(data=>{
    const host=get('ml_status');host.replaceChildren();
    message(host,'Languages: English, Spanish and French | Offline topic search: '+
      (data.offline_topic_search_available?'ready':'unavailable')+' | LSA: '+
      (data.lsa_active?'ready':'unavailable')+' | Neural MiniLM: '+
      (data.multilingual_embeddings_active?'enabled':'not hosted on Render Free'));
    message(host,'External machine translation: '+
      (data.translation?.installed?'installed but optional':'not installed')+
      (data.translation?.rate_limited?' | temporarily rate limited':'')+
      '. Local topic search never requires external consent.');
  }).catch(()=>{
    message(get('ml_status'),'Capability status unavailable. Offline topic search can still be attempted.');
  });
})();
