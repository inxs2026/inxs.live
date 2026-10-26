(() => {
 const box=document.getElementById('briefing-mail'),label=document.getElementById('briefing-mail-status'),badge=document.getElementById('briefing-mail-count');
 if(!box)return;
 let busy=false;
 async function update(){if(busy||document.hidden)return;busy=true;
  try{const response=await fetch('/api/mail/unread',{credentials:'same-origin',cache:'no-store'});if(!response.ok)throw new Error();const state=await response.json();badge.hidden=true;box.classList.remove('has-unread');
   if(!state.connected){label.textContent=state.configured?'Connect Gmail':'Setup needed';box.setAttribute('aria-label','Open Mail · '+label.textContent);}
   else if(state.unread===null){label.textContent='Check connection';box.setAttribute('aria-label','Open Mail · connection needs attention');}
   else{const count=state.unread;label.textContent=count?'Unread in inbox':'All caught up';badge.textContent=count>999?'999+':String(count);badge.hidden=!count;box.classList.toggle('has-unread',count>0);box.setAttribute('aria-label','Open Mail · '+count+' unread inbox messages');box.title='Checked '+new Intl.DateTimeFormat('en-CA',{timeStyle:'short',timeZone:'America/Toronto'}).format(new Date());}
  }catch{label.textContent='Unavailable';badge.hidden=true;box.classList.remove('has-unread');box.setAttribute('aria-label','Open Mail · unread count unavailable');}finally{busy=false;}
 }
 update();setInterval(update,120000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)update();});
})();
