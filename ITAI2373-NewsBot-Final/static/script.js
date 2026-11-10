const el=id=>document.getElementById(id);
async function send(url,payload,target){
  el(target).textContent='Processing request…';
  try {const res=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const body=await res.json();if(!res.ok)throw Error(body.error||'Request failed');
    el(target).textContent=JSON.stringify(body,null,2);
  } catch(e){el(target).textContent='Unable to complete request: '+e.message;}
}
el('analyze').addEventListener('click',()=>send('/api/analyze',{text:el('article').value},'analyze_out'));
el('ask').addEventListener('click',()=>send('/api/query',{query:el('query').value},'chat_out'));
el('reset').addEventListener('click',()=>send('/api/clear',{},'chat_out'));
