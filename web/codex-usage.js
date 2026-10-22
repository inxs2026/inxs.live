"use strict";
function codexWindowLabel(w){const m=w.windowDurationMins;return m===300?'5-hour limit':m===10080?'Weekly limit':m?`${m>=1440?m/1440+'-day':m>=60?m/60+'-hour':m+'-minute'} limit`:(w.slot==='primary'?'Primary limit':'Secondary limit');}
function codexMeter(w,stale){
 const known=typeof w.remainingPercent==='number'&&Number.isFinite(w.remainingPercent);
 const remaining=known?Math.max(0,Math.min(100,w.remainingPercent)):null;
 const reset=w.resetsAt?new Date(w.resetsAt*1000).toISOString():null;
 return `<article class="panel health-card codex-card"><h3>${esc(codexWindowLabel(w))}</h3><p class="codex-bucket">${esc(w.name)}</p><div class="disk-value">${known?remaining.toFixed(0)+'%':'—'} <small>${known?'remaining':'unavailable'}</small></div>${known?`<meter class="codex-meter${remaining<=10?' low':''}" min="0" max="100" value="${remaining}" aria-label="${esc(codexWindowLabel(w))} remaining allowance">${remaining.toFixed(0)}%</meter><p>${w.usedPercent.toFixed(0)}% used${stale?' · Last confirmed reading':''}</p>`:''}<p class="backup-note">${reset?'Resets '+esc(formatted(reset)):'Reset time unavailable'}</p></article>`;
}
function codexBankedResets(bank,stale){
 const count=Number.isInteger(bank?.availableCount)&&bank.availableCount>=0?bank.availableCount:null;
 const details=Array.isArray(bank?.credits)?bank.credits:null;
 const expiry=value=>{if(typeof value!=='number'||!Number.isFinite(value)||value<=0)return 'Expiry time unavailable';const d=new Date(value*1000);if(!Number.isFinite(d.getTime()))return 'Expiry time unavailable';return (value*1000<=Date.now()?'Expired ':'Expires ')+new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',year:'numeric',month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(d);};
 const status=count===null?'Not available':`${count} ${stale?'last confirmed':'available'}`;
 const rows=details?.length?`<ul class="codex-reset-list">${details.map((credit,i)=>`<li><div><strong>Reset ${i+1}</strong><span>${esc(credit.title||'Rate-limit reset')}</span></div><time>${esc(expiry(credit.expiresAt))}</time></li>`).join('')}</ul>`:'';
 const note=count===0?'No banked resets available.':count===null?'Banked-reset information was not supplied by the usage service.':details===null?'Expiry details are unavailable for this reading.':details.length<count?`Expiry details supplied for ${details.length} of ${count} resets.`:'';
 return `<article class="panel health-card codex-banked"><div class="codex-reset-heading"><h3>Banked resets</h3><strong>${status}</strong></div>${rows}${note?`<p class="backup-note">${esc(note)}</p>`:''}<p class="backup-note">Expiry times are shown in Toronto time.${stale?' Last confirmed reading; waiting for an update.':''}</p></article>`;
}
let codexLoading=false;
async function loadCodexUsage(){
 const el=document.getElementById('codex-usage'),button=document.getElementById('refresh-codex');if(!el||codexLoading)return;
 codexLoading=true;button.disabled=true;
 try{const d=await getJSON('/api/codex-usage');const stale=d.state==='cached';
 el.innerHTML=d.windows?.length?d.windows.map(w=>codexMeter(w,stale)).join('')+codexBankedResets(d.bankedResets,stale):`<article class="panel health-card"><h3>${d.state==='signin-required'?'Connect Codex':'Usage unavailable'}</h3><p>${esc(d.note)}</p></article>`;
 document.getElementById('codex-checked').textContent=(d.fetchedAt?'Last confirmed '+formatted(d.fetchedAt)+' · ':'')+d.note+' Checks every two minutes.';
 }catch{document.getElementById('codex-checked').textContent='Usage check unavailable. Retrying automatically.';if(!el.querySelector('.codex-card'))el.innerHTML='<p class="empty">Codex usage is unavailable.</p>';}
 finally{codexLoading=false;button.disabled=false;}
}
document.getElementById('refresh-codex')?.addEventListener('click',loadCodexUsage);loadCodexUsage();setInterval(loadCodexUsage,120000);

// Phone browsers can suspend polling while a tab is in the background.
document.addEventListener('visibilitychange',()=>{if(!document.hidden)loadCodexUsage();});
window.addEventListener('pageshow',loadCodexUsage);
window.addEventListener('online',loadCodexUsage);
