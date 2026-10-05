'use strict';
// Notices never modify scheduler results. All notices link back to their underlying data.
function expectedStockDate(slot,now=new Date()){
 const parts=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(now).map(p=>[p.type,p.value]));
 const date=new Date(`${parts.year}-${parts.month}-${parts.day}T12:00:00Z`);
 if(Number(parts.hour)*60+Number(parts.minute)<(slot==='morning'?615:915))date.setUTCDate(date.getUTCDate()-1);
 while([0,6].includes(date.getUTCDay()))date.setUTCDate(date.getUTCDate()-1);
 return date.toISOString().slice(0,10);
}
function racingNotices(racing){
 const notices=[];
 if(racing.errors.length)notices.push('Saved racing picks need attention');
 if(racing.schedule?.scheduled===false&&!racing.races.length)return notices;
 if(racing.schedule?.scheduled===true&&!racing.races.length)notices.push('Racing is scheduled today; no saved picks are available yet');
 if(racing.scratches.error||racing.scratches.snapshot)notices.push('Latest daily scratch feed has not been confirmed');
 return notices;
}
function racingStatusText(racing){
 if(racing?.schedule?.scheduled===false&&!racing.races.length)return 'No racing scheduled today'+(racing.schedule.nextRaceDate?' · Next race day: '+racing.schedule.nextRaceDate:' · No further dates in the approved calendar');
 return '';
}
function jobFailureImpact(j){
 return j.unit==='81265f85-6e79-4379-a5d3-119ebbe43c7e'&&j.failureReason==='The model runtime changed before the job could start.'?'That attempt produced no Top 3 Beyer picks PDF. Smart Picks is a separate job.':'The failed run does not confirm its intended output or delivery.';
}
const noticeVerifications=new Map();
function jobFailureAction(j){
 const verified=noticeVerifications.get(noticeIdentity('', '/dashboard#job='+encodeURIComponent(j.id),jobFailureOccurrence(j)));
 if(verified)return verified+' Next full race-day run will verify report generation and delivery.';
 const reason=j.failureReason||'';
 if(reason.includes('runtime changed'))return 'Verify this job can start successfully before its next scheduled run. Its recovery is not yet verified.';
 if(reason.includes('authenticate'))return 'Repair this job’s service credentials, then verify a successful run.';
 if(reason.includes('allowed time'))return 'Investigate the slow step or timeout, then verify the expected report was produced.';
 if(reason.includes('limited requests'))return 'Check provider availability and verify the next retry succeeds.';
 if(reason.includes('delivery problem'))return 'Check the destination and delivery credentials, then confirm the report was delivered.';
 return 'Inspect this job’s run log, repair the reported failure, and verify its expected output.';
}
function noticeHistory(history){return `<details class="attention-history"><summary>Notice history${history.length?' ('+history.length+')':''}</summary>${history.length?history.map(n=>`<article class="notice-history-entry"><div class="notice-history-meta">${esc(n.resolved_at?'No longer reported':n.acknowledged_at?'Acknowledged':'Open')} · First seen ${esc(formatted(n.first_seen))}${n.acknowledged_at?' · Acknowledged '+esc(formatted(n.acknowledged_at)):''}${n.resolved_at?' · Cleared '+esc(formatted(n.resolved_at)):''}</div><a href="${esc(n.url)}">${esc(n.text)}</a>${n.verification?`<p>Technical check: ${esc(n.verification)} · ${esc(formatted(n.verified_at))}</p>`:''}</article>`).join(''):'<p>No recorded notices yet.</p>'}<p>History is retained after acknowledgement or recovery. Showing the latest 100 notices. “No longer reported” means the current checks no longer report this issue.</p></details>`;}
function noticeIdentity(text,url,occurrence){return JSON.stringify([url,occurrence||new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())+'|'+text]);}
function jobFailureOccurrence(j){return JSON.stringify([j.id,j.lastRun,j.result,j.failureReason]);}
async function loadAttention(){
 const notices=[];
 const results=await Promise.allSettled(['/api/jobs','/api/stocks','/api/briefing','/api/racing','/api/acknowledgements'].map(getJSON));
 const add=(text,url,occurrence)=>notices.push({text,url,key:noticeIdentity(text,url,occurrence)});
 results.slice(0,4).forEach((r,i)=>{if(r.status!=='fulfilled')add(['Job inventory','Stock reports','Briefing feeds','Racing data'][i]+' could not be checked',['/dashboard','/stocks','/','/woodbine'][i]);});
 noticeVerifications.clear();for(const item of results[4].value?.history||[])if(item.verification)noticeVerifications.set(item.identity,item.verification);
 const jobsData=results[0].value;
 if(jobsData){const failed=jobsData.jobs.filter(j=>j.status==='active'&&!j.archived&&isFailed(j));for(const j of failed)add(`${j.platform} · ${j.name} — last run failed ${formatted(j.lastRun)}. Cause: ${j.failureReason||'The scheduler did not provide a detailed cause.'} ${jobFailureImpact(j)} Action needed: ${jobFailureAction(j)} ${j.nextRun?'Next scheduled attempt: '+formatted(j.nextRun)+'.':''} Open this job’s details ↗`,'/dashboard#job='+encodeURIComponent(j.id),jobFailureOccurrence(j));
 const overdue=jobsData.jobs.filter(j=>j.status==='active'&&j.nextRun&&Number.isFinite(Date.parse(j.nextRun))&&Date.now()-Date.parse(j.nextRun)>900000);if(overdue.length)add(`${overdue.length} next-run timestamp${overdue.length===1?' is':'s are'} overdue — check schedules`,'/dashboard#automations');
 for(const [name,state] of Object.entries(jobsData.gateways||{}))if(state!=='active')add(name+' gateway: '+state,'/');
 if(jobsData.errors.length)add('Job inventory may be incomplete','/');}
 const stocksData=results[1].value;
 if(stocksData)for(const slot of ['morning','afternoon']){const expected=expectedStockDate(slot),r=stocksData.reports[slot];if(!r||r.date<expected){const run=stocksData.latestRuns?.[slot];add(`${slot==='morning'?'Morning':'Afternoon'} ${run?.date>=expected?'report succeeded; dashboard copy missing for ':'stock report missing for '}${expected}`,'/stocks#stock-watchlists');}}
 const feeds=results[2].value;
 if(feeds)for(const [key,f] of Object.entries(feeds)){if(f.error||f.stale||(f.data&&(!f.updatedAt||Date.now()-Date.parse(f.updatedAt)>1200000)))add(({weather:'Weather',news:'Canadian news',usnews:'U.S. news',sports:'Sports news',scores:'Sports scores'}[key]||key)+(f.data?' is using cached data':' is unavailable'),'/');}
 if(feeds?.scores?.data?.unavailable?.length)add('Some sports scoreboards are unavailable','/');
 const racing=results[3].value;
 if(racing){for(const text of racingNotices(racing))add(text,'/woodbine');
 if(racing.schedule?.scheduled!==false&&racing.scratches.available&&!racing.scratches.snapshot){const keys=racing.scratches.items.map(s=>`${s.race}|${s.pp}|${s.name}|${s.reason}`);let previous=null;try{previous=JSON.parse(localStorage.getItem('dashboard-scratches-'+racing.date));localStorage.setItem('dashboard-scratches-'+racing.date,JSON.stringify(keys));}catch{}
 const added=Array.isArray(previous)?keys.filter(k=>!previous.includes(k)).length:0;
 if(added)add(`${added} new scratch${added===1?'':'es'} since your last check`,'/woodbine');else if(keys.length)add(`${keys.length} reported scratch${keys.length===1?'':'es'} on today’s card`,'/woodbine');}}
 let log=results[4].status==='fulfilled'?results[4].value:null;
 try{const response=await fetch('/api/acknowledgements',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({notices:JSON.stringify(notices),complete:String(results.slice(0,4).every(r=>r.status==='fulfilled'))}).toString()});if(!response.ok)throw new Error('History unavailable');log=await response.json();}catch{log=null;}
 const saved=new Set(log?.keys||[]);
 const acknowledged=notices.filter(n=>saved.has(n.key)), active=notices.filter(n=>!saved.has(n.key));
 const el=document.getElementById('attention-strip');const wasOpen=el.querySelector('details')?.open;el.classList.toggle('has-notices',!!active.length);
 const message=active.length?active.length+' notice'+(active.length===1?'':'s'):acknowledged.length?acknowledged.length+' acknowledged · Awaiting next scheduled run':racingStatusText(racing)||'No issues found in the checks available';
 el.innerHTML=`<details${wasOpen?' open':''}><summary><span class="attention-heading">${active.length?'Needs attention':acknowledged.length?'Acknowledged':'Status check'}</span><span>${esc(message)} · tap for details</span></summary><div class="attention-items">${active.map((n,i)=>`<div class="attention-notice"><a href="${esc(n.url)}">${esc(n.text)} <span>↗</span></a><button type="button" data-acknowledge="${i}">Acknowledge</button></div>`).join('')}${!active.length&&!acknowledged.length?'<p>Checked active jobs, gateways, weekday stock reports, briefing feeds, and race-day scratches. Direct cron run history is unavailable.</p>':''}${acknowledged.length?'<p>Acknowledged notices are saved in the history below. New failures will raise a fresh bulletin.</p>':''}${racingStatusText(racing)?`<p>${esc(racingStatusText(racing))}. Picks and scratch checks are not expected on a non-racing day.</p>`:''}${!log?'<p role="alert">Notice history and acknowledgements are unavailable. Showing all notices until the connection recovers.</p>':''}${noticeHistory(log?.history||[])}<p id="acknowledgement-error" role="alert" hidden></p></div><p class="attention-checked">Checked ${esc(formatted(new Date().toISOString()))} · Acknowledgements are shared across your signed-in devices.</p></details>`;
 el.querySelectorAll('[data-acknowledge]').forEach(button=>button.addEventListener('click',async()=>{
   button.disabled=true;button.textContent='Saving…';
   try{const response=await fetch('/api/acknowledgements',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({key:active[Number(button.dataset.acknowledge)].key}).toString()});if(!response.ok)throw new Error('Save failed');await loadAttention();}
   catch{button.disabled=false;button.textContent='Acknowledge';const error=document.getElementById('acknowledgement-error');error.hidden=false;error.textContent='Acknowledgement could not be saved. Please retry.';}
 }));
 window.dispatchEvent(new CustomEvent('dashboard:attention',{detail:{notices:active,acknowledged,racing,stocks:stocksData,jobs:jobsData}}));
}
loadAttention();setInterval(loadAttention,60000);
