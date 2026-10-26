(() => {
 'use strict';
 const $ = id => document.getElementById(id);
 const esc = value => String(value || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let accounts = [], account = '', folder = 'INBOX', selected = null, items = [], next = '', page = '', pages = [], search = '', generation = 0, reading = 0, configured = false, sending = false, requestId = '', replyId = '';
 const names = {INBOX:'Inbox', STARRED:'Starred', SENT:'Sent', DRAFT:'Drafts'};
 function status(message, error=false) { $('email-status').textContent=message; $('email-status').classList.toggle('error',error); }
 async function api(action, data, params) {
  const url='/api/mail/'+action+(params?'?'+new URLSearchParams(params):'');
  const response=await fetch(url,{cache:'no-store',credentials:'same-origin',...(data!==undefined?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}:{})});
  if(response.status===401){location.assign('/login?next=%2Femail');throw new Error('Please sign in again.');}
  const result=await response.json();if(!response.ok)throw new Error(result.error||'Email is temporarily unavailable.');return result;
 }
 function date(value,full=false){const d=new Date(value);return Number.isNaN(d.valueOf())?'':new Intl.DateTimeFormat('en-CA',{...(full?{dateStyle:'medium',timeStyle:'short'}:{month:'short',day:'numeric'}),timeZone:'America/Toronto'}).format(d);}
 async function init() {
  try {
   const query=new URLSearchParams(location.search);
   if(location.pathname==='/email/oauth/callback'){
    const data={state:query.get('state')||'',code:query.get('code')||'',error:query.get('error')||''};
    history.replaceState(null,'','/email');status('Completing your Google connection…');
    try{const result=await api('callback',data);account=result.connected;status('Connected '+account+'.');}catch(error){status(error.message,true);}
   }
   const result=await api('status');accounts=result.accounts;configured=result.configured;
   $('email-workspace').hidden=!accounts.length;$('email-setup').hidden=!!accounts.length;$('email-compose').disabled=!accounts.length;$('email-add').disabled=!configured;
   if(!accounts.length){
    $('email-connect').disabled=!configured;
    $('email-setup-title').textContent=configured?'Connect your first Gmail account':'Your Mail page is ready for Google setup';
    $('email-setup-description').textContent=configured?'Connect lexiinxs@gmail.com to read and send email here. Your password is entered only on Google’s sign-in page.':'The Mail page is installed. A Google OAuth client must be configured before lexiinxs@gmail.com can sign in.';
    $('email-setup-note').textContent=configured?'This connection allows reading, sending, and organizing mail. Your existing Gmail app will keep working.':'No mailbox is connected yet. Once Google setup is complete, the Connect with Google button will become available.';
    if(!$('email-status').classList.contains('error'))status(configured?'Ready to connect Gmail.':'Awaiting Google connection setup.');return;
   }
   if(!accounts.some(a=>a.email===account))account=accounts[0].email;
   const options=accounts.map(a=>'<option value="'+esc(a.email)+'">'+esc(a.email)+'</option>').join('');
   $('email-account').innerHTML=options;$('email-account').value=account;$('email-from').innerHTML=options;
   updateGmailLink();await load();
  }catch(error){status(error.message,true);}
 }
 function updateGmailLink(){ $('email-gmail').href='https://mail.google.com/mail/u/?authuser='+encodeURIComponent(account); }
 function clearReader(){selected=null;++reading;$('email-message').innerHTML='<div class="email-empty"><h2>Your conversations</h2><p>Select a message to read it.</p></div>';}
 async function load(){const seq=++generation;const requested=account;clearReader();$('email-messages').innerHTML='<div class="email-empty">Loading messages…</div>';$('email-next').hidden=true;$('email-previous').hidden=true;status('Checking '+account+'…');
  try{const result=await api('messages',undefined,{account,folder,q:search,page});if(seq!==generation||requested!==account)return;items=result.messages;next=result.nextPage;renderList();$('email-next').hidden=!next;$('email-previous').hidden=!pages.length;status(account+' · '+(items.length?'Latest messages loaded.':'No messages in this view.'));}catch(error){if(seq!==generation)return;$('email-messages').innerHTML='<div class="email-empty">Messages could not be loaded. Use Refresh to try again.</div>';status(error.message,true);}
 }
 function renderList(){ $('email-folder-title').textContent=names[folder];document.querySelectorAll('[data-mail-folder]').forEach(b=>b.classList.toggle('selected',b.dataset.mailFolder===folder));$('email-messages').innerHTML=items.length?items.map(m=>'<button class="email-message-row'+(m.unread?' unread':'')+(selected?.id===m.id?' selected':'')+'" type="button" data-message="'+esc(m.id)+'"><span class="email-row-top"><span class="email-row-sender">'+(m.unread?'<span class="email-unread-dot" aria-label="Unread"></span>':'')+esc(folder==='SENT'?m.to:m.from)+'</span><span class="email-row-date">'+esc(date(m.date))+'</span></span><span class="email-row-subject">'+(m.starred?'★ ':'')+esc(m.subject)+'</span><span class="email-row-snippet">'+esc(m.snippet)+'</span></button>').join(''):'<div class="email-empty">'+(search?'No messages match your search.':'This folder is empty.')+'</div>'; }
 async function openMessage(id){const seq=++reading, current=account;selected=null;$('email-message').innerHTML='<div class="email-empty">Opening message…</div>';try{const message=await api('message',undefined,{account:current,id});if(seq!==reading||current!==account)return;selected=message;renderList();renderMessage();if(message.unread){await api('modify',{account:current,id,action:'read'});if(seq!==reading||current!==account)return;message.unread=false;const row=items.find(x=>x.id===id);if(row)row.unread=false;renderList();}}catch(error){if(seq!==reading)return;status(error.message,true);$('email-message').innerHTML='<div class="email-empty">This message could not be opened.</div>';}}
 function renderMessage(){const m=selected;$('email-message').innerHTML='<div class="email-reader-top"><span class="email-note">'+esc(names[folder])+'</span><button class="email-text-button" type="button" data-mail-action="'+(m.starred?'unstar':'star')+'">'+(m.starred?'★ Starred':'☆ Star')+'</button></div><h2>'+esc(m.subject)+'</h2><div class="email-reader-meta"><strong>'+esc(m.from)+'</strong><br>To: '+esc(m.to)+'<br>'+esc(date(m.date,true))+'</div><div class="email-body">'+esc(m.body)+'</div>'+(m.attachments.length?'<div class="email-attachments">'+m.attachments.map(a=>'<button class="email-button email-attachment" type="button" data-attachment="'+esc(a.id)+'">↓ '+esc(a.name)+' · '+Math.ceil(a.size/1024)+' KB</button>').join('')+'</div>':'')+'<div class="email-reader-actions">'+(folder!=='DRAFT'?'<button class="email-button primary" type="button" data-mail-action="reply">Reply</button>':'<span class="email-note">Edit this draft in Gmail.</span>')+(folder==='INBOX'?'<button class="email-button" type="button" data-mail-action="archive">Archive</button>':'')+'</div>';}
 async function connect(email){try{status('Preparing Google sign-in…');const result=await api('connect',{email});const url=new URL(result.url);if(url.origin!=='https://accounts.google.com')throw new Error('Invalid Google connection link.');location.assign(url.href);}catch(error){status(error.message,true);}}
 function compose(reply){requestId=crypto.randomUUID();replyId=reply?.id||'';$('email-from').value=account;$('email-from').disabled=!!reply;$('email-to').value=reply?(reply.replyTo||reply.from):'';$('email-subject').value=reply?(/^re:/i.test(reply.subject)?reply.subject:'Re: '+reply.subject):'';$('email-body').value='';$('email-files').value='';$('email-send-status').textContent='';$('email-send').disabled=false;$('email-compose-title').textContent=reply?'Reply':'New message';$('email-compose-dialog').showModal();}
 $('email-compose').onclick=()=>compose();$('email-connect').onclick=()=>connect('lexiinxs@gmail.com');$('email-add').onclick=()=>$('email-add-dialog').showModal();
 $('email-add-form').onsubmit=e=>{e.preventDefault();$('email-add-dialog').close();connect($('email-new-account').value.trim());};
 document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>{if(b.dataset.close==='email-compose-dialog'&&sending)return;$(b.dataset.close).close();});
 $('email-compose-dialog').addEventListener('cancel',e=>{if(sending)e.preventDefault();});
 $('email-account').onchange=()=>{account=$('email-account').value;page='';pages=[];updateGmailLink();load();};
 document.querySelectorAll('[data-mail-folder]').forEach(b=>b.onclick=()=>{folder=b.dataset.mailFolder;page='';pages=[];load();});
 $('email-refresh').onclick=()=>load();$('email-search-form').onsubmit=e=>{e.preventDefault();search=$('email-search').value.trim();page='';pages=[];load();};
 $('email-next').onclick=()=>{pages.push(page);page=next;load();};$('email-previous').onclick=()=>{page=pages.pop()||'';load();};
 $('email-messages').onclick=e=>{const b=e.target.closest('[data-message]');if(b)openMessage(b.dataset.message);};
 $('email-message').onclick=async e=>{const action=e.target.closest('[data-mail-action]'), attachment=e.target.closest('[data-attachment]');if(!selected)return;const current=account,m=selected;
  try{if(attachment){attachment.disabled=true;const result=await api('attachment',undefined,{account:current,id:m.id,attachment:attachment.dataset.attachment});const bytes=Uint8Array.from(atob(result.data.replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0));const url=URL.createObjectURL(new Blob([bytes],{type:'application/octet-stream'}));const a=document.createElement('a');a.href=url;a.download=result.name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);attachment.disabled=false;return;}
   if(!action)return;const value=action.dataset.mailAction;if(value==='reply'){compose(m);return;}action.disabled=true;await api('modify',{account:current,id:m.id,action:value});if(current!==account||selected?.id!==m.id)return;if(value==='archive'){load();return;}m.starred=value==='star';const row=items.find(x=>x.id===m.id);if(row)row.starred=m.starred;renderList();renderMessage();
  }catch(error){status(error.message,true);if(action)action.disabled=false;if(attachment)attachment.disabled=false;}
 };
 $('email-disconnect').onclick=()=>{$('email-disconnect-address').textContent=account;$('email-disconnect-dialog').showModal();};
 $('email-disconnect-confirm').onclick=async()=>{const email=account;try{await api('disconnect',{account:email});$('email-disconnect-dialog').close();account='';await init();status('Disconnected '+email+'.');}catch(error){status(error.message,true);}};
 async function files(){const chosen=Array.from($('email-files').files);if(chosen.length>10||chosen.reduce((s,f)=>s+f.size,0)>2000000)throw new Error('Choose at most 10 files, totalling less than 2 MB.');return Promise.all(chosen.map(file=>new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve({name:file.name,data:String(reader.result).split(',')[1]});reader.onerror=()=>reject(new Error('Could not read an attachment.'));reader.readAsDataURL(file);})))}
 $('email-send-form').onsubmit=async e=>{e.preventDefault();if(sending)return;sending=true;$('email-send').disabled=true;$('email-send-status').className='';$('email-send-status').textContent='Sending…';try{const attachments=await files();const sender=$('email-from').value;await api('send',{account:sender,to:$('email-to').value,subject:$('email-subject').value,body:$('email-body').value,attachments,replyId,requestId});$('email-compose-dialog').close();if(account===sender){folder='SENT';page='';pages=[];await load();}status('Email sent from '+sender+'.');}catch(error){$('email-send-status').className='error';$('email-send-status').textContent=error.message;}finally{sending=false;$('email-send').disabled=false;}};
 init();
})();
