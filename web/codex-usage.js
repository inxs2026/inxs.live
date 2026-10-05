"use strict";
function codexWindowLabel(w){const m=w.windowDurationMins;return m===300?'5-hour limit':m===10080?'Weekly limit':m?`${m>=1440?m/1440+'-day':m>=60?m/60+'-hour':m+'-minute'} limit`:(w.slot==='primary'?'Primary limit':'Secondary limit');}
function codexMeter(w,stale){
 const known=typeof w.remainingPercent==='number'&&Number.isFinite(w.remainingPercent);
 const remaining=known?Math.max(0,Math.min(100,w.remainingPercent)):null;
 const reset=w.resetsAt?new Date(w.resetsAt*1000).toISOString():null;
 return `<article class="panel health-card codex-card"><h3>${esc(codexWindowLabel(w))}</h3><p class="codex-bucket">${esc(w.name)}</p><div class="disk-value">${known?remaining.toFixed(0)+'%':'—'} <small>${known?'remaining':'unavailable'}</small></div>${known?`<meter class="codex-meter${remaining<=10?' low':''}" min="0" max="100" value="${remaining}" aria-label="${esc(codexWindowLabel(w))} remaining allowance">${remaining.toFixed(0)}%</meter><p>${w.usedPercent.toFixed(0)}% used${stale?' · Last confirmed reading':''}</p>`:''}<p class="backup-note">${reset?'Resets '+esc(formatted(reset)):'Reset time unavailable'}</p></article>`;
}
async function loadCodexUsage(){
 const el=document.getElementById('codex-usage'),button=document.getElementById('refresh-codex');if(!el)return;
 button.disabled=true;
 try{const d=await getJSON('/api/codex-usage');const stale=d.state==='cached';
 el.innerHTML=d.windows?.length?d.windows.map(w=>codexMeter(w,stale)).join(''):`<article class="panel health-card"><h3>${d.state==='signin-required'?'Connect Codex':'Usage unavailable'}</h3><p>${esc(d.note)}</p></article>`;
 document.getElementById('codex-checked').textContent=(d.fetchedAt?'Last confirmed '+formatted(d.fetchedAt)+' · ':'')+d.note+' Checks every two minutes.';
 }catch{document.getElementById('codex-checked').textContent='Usage check unavailable. Retrying automatically.';if(!el.querySelector('.codex-card'))el.innerHTML='<p class="empty">Codex usage is unavailable.</p>';}
 finally{button.disabled=false;}
}
document.getElementById('refresh-codex')?.addEventListener('click',loadCodexUsage);loadCodexUsage();setInterval(loadCodexUsage,120000);
