const $ = id => document.getElementById(id);
const conversation = $('conversation');
const initialReferences = $('references').innerHTML;
let ready = false, busy = false, entries = [], lastQuestion = '';
const icon = name => { const svg = document.createElementNS('http://www.w3.org/2000/svg','svg'); const use = document.createElementNS('http://www.w3.org/2000/svg','use'); use.setAttribute('href','#'+name); svg.append(use); return svg; };
function updateSend(){ $('send').disabled = !ready || busy || !$('question').value.trim(); }
function addMessage(role, text, error=false){
  const article=document.createElement('article'); article.className='message '+role+'-message'+(error?' error':'');
  const label=document.createElement('div');label.className='message-label';
  if(role==='assistant')label.append(icon('spark'));
  label.append(document.createTextNode(role==='user'?'YOU':'ENSO ASSISTANT'));
  const content=document.createElement('div');content.className='message-text';content.textContent=text;
  article.append(label,content);conversation.append(article);return article;
}
function sourceLink(page, className){const a=document.createElement('a');a.href='/manual#page='+page;a.target='_blank';a.rel='noopener';a.className=className;a.append(icon('book'),document.createTextNode('HR Manual · Page '+page+' ↗'));return a;}
function showReferences(result){
 const panel=$('references');panel.replaceChildren();const title=document.createElement('div');title.className='panel-label';title.textContent='POLICY REFERENCES';panel.append(title);
 if(result.pages.length){for(const page of result.pages){const link=sourceLink(page,'reference-card');const sub=document.createElement('span');sub.textContent='View the cited passage in the original PDF';link.append(sub);panel.append(link);}}
 else {const p=document.createElement('p');p.className='reference-note';p.textContent='No supporting passage was found for this question. The assistant has not added external information.';panel.append(p);}
}
function updateRecents(){const list=$('recent-list');list.replaceChildren();for(const e of entries.slice().reverse().slice(0,6)){const b=document.createElement('button');b.textContent=e.question;b.title=e.question;b.onclick=()=>{$('question').value=e.question;updateSend();$('question').focus();};list.append(b);}}
async function submit(question){
 if(busy||!ready||!question.trim())return;
 question=question.trim();busy=true;lastQuestion=question;$('welcome').hidden=true;conversation.hidden=false;$('question').value='';$('question').style.height='auto';updateSend();
 addMessage('user',question);
 const pending=addMessage('assistant','');pending.classList.add('pending');const spinner=document.createElement('span');spinner.className='spinner';pending.querySelector('.message-text').append(spinner,document.createTextNode('Finding the relevant policy…'));pending.scrollIntoView({behavior:'smooth',block:'nearest'});
 try{
  const response=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})});const result=await response.json();if(!response.ok)throw new Error(result.error||'The request failed. Please retry.');
  pending.remove();const answer=addMessage('assistant',result.answer);const badge=document.createElement('div');badge.className='answer-badge'+(result.supported?'':' unsupported');badge.textContent=result.supported?'✓  Source-backed answer':'No supporting policy found';answer.querySelector('.message-label').after(badge);
  for(const page of result.pages)answer.append(sourceLink(page,'source-chip'));
  entries.push({question,...result});$('export-chat').disabled=false;updateRecents();showReferences(result);answer.scrollIntoView({behavior:'smooth',block:'nearest'});
 }catch(error){pending.remove();const article=addMessage('assistant',error.message,true);const retry=document.createElement('button');retry.className='source-chip';retry.textContent='Try again ↗';retry.onclick=()=>submit(question);article.append(retry);article.scrollIntoView({behavior:'smooth',block:'nearest'});}
 finally{busy=false;updateSend();$('question').focus();}
}
$('question-form').addEventListener('submit',e=>{e.preventDefault();submit($('question').value);});
$('question').addEventListener('input',()=>{const t=$('question');t.style.height='auto';t.style.height=Math.min(t.scrollHeight,150)+'px';updateSend();});
$('question').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();submit($('question').value);}});
document.querySelectorAll('[data-question]').forEach(b=>b.onclick=()=>{if(!ready||busy){$('question').value=b.dataset.question;updateSend();$('question').focus();return;}submit(b.dataset.question);});
$('new-chat').onclick=()=>{if(busy)return;entries=[];conversation.replaceChildren();conversation.hidden=true;$('welcome').hidden=false;$('question').value='';$('recent-list').innerHTML='<p>Your questions will appear here.</p>';$('export-chat').disabled=true;$('references').innerHTML=initialReferences;updateSend();window.scrollTo({top:0,behavior:'smooth'});$('question').focus();};
$('new-chat-mobile').onclick=()=> $('new-chat').click();
$('assistant-nav').onclick=()=>{$('question').focus();};
$('export-chat').onclick=()=>{const text=entries.map(e=>'Question: '+e.question+'\n\n'+(e.supported?'Answer: ':'')+e.answer+(e.reference?'\n\nReference: '+e.reference:'')).join('\n\n----------------------------------------\n\n');const blob=new Blob(['HR POLICY ASSISTANT\nEnso Group HR Policy Manual\n\n'+text],{type:'text/plain'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='hr-policy-conversation.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
async function status(){try{const r=await fetch('/api/status');const data=await r.json();ready=data.ready;$('status').classList.toggle('error',!ready);$('status').querySelector('span').textContent=ready?'Manual connected':'Setup needed';if(data.pages)$('page-count').textContent=data.pages+' pages';$('setup-message').hidden=ready;$('setup-message').textContent=data.error||'';updateSend();if(!ready&&data.error==='The assistant is starting.')setTimeout(status,1000);}catch{ready=false;$('status').classList.add('error');$('status').querySelector('span').textContent='Connection lost';$('setup-message').hidden=false;$('setup-message').textContent='The local server is unavailable. Restart Start_Web_Assistant.command.';updateSend();}}
status();
