'use strict';
// Read-only overview. All notices link back to their underlying data.
function expectedStockDate(slot,now=new Date()){
 const parts=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(now).map(p=>[p.type,p.value]));
 const date=new Date(`${parts.year}-${parts.month}-${parts.day}T12:00:00Z`);
 if(Number(parts.hour)*60+Number(parts.minute)<(slot==='morning'?615:915))date.setUTCDate(date.getUTCDate()-1);
 while([0,6].includes(date.getUTCDay()))date.setUTCDate(date.getUTCDate()-1);
 return date.toISOString().slice(0,10);
}
async function loadAttention(){
 const notices=[];
 const results=await Promise.allSettled(['/api/jobs','/api/stocks','/api/briefing','/api/racing'].map(getJSON));
 const add=(text,url)=>notices.push({text,url});
 results.forEach((r,i)=>{if(r.status!=='fulfilled')add(['Job inventory','Stock reports','Briefing feeds','Racing data'][i]+' could not be checked',['/dashboard','/stocks','/','/woodbine'][i]);});
 const jobsData=results[0].value;
 if(jobsData){const failed=jobsData.jobs.filter(j=>j.status==='active'&&!j.archived&&isFailed(j));for(const j of failed)add(`${j.platform} · ${j.name}: ${j.failureReason||'Last run reported '+j.result+'. The scheduler did not provide a detailed cause.'} Last attempt ${formatted(j.lastRun)}. ${j.nextRun?'Next scheduled attempt '+formatted(j.nextRun)+'. Check the next result; recovery is not yet confirmed.':'No next attempt is available. Needs a schedule check.'}`,'/#automations');
 const overdue=jobsData.jobs.filter(j=>j.status==='active'&&j.nextRun&&Number.isFinite(Date.parse(j.nextRun))&&Date.now()-Date.parse(j.nextRun)>900000);if(overdue.length)add(`${overdue.length} next-run timestamp${overdue.length===1?' is':'s are'} overdue — check schedules`,'/#automations');
 for(const [name,state] of Object.entries(jobsData.gateways||{}))if(state!=='active')add(name+' gateway: '+state,'/');
 if(jobsData.errors.length)add('Job inventory may be incomplete','/');}
 const stocksData=results[1].value;
 if(stocksData)for(const slot of ['morning','afternoon']){const expected=expectedStockDate(slot),r=stocksData.reports[slot];if(!r||r.date<expected){const run=stocksData.latestRuns?.[slot];add(`${slot==='morning'?'Morning':'Afternoon'} ${run?.date>=expected?'report succeeded; dashboard copy missing for ':'stock report missing for '}${expected}`,'/stocks#stock-watchlists');}}
 const feeds=results[2].value;
 if(feeds)for(const [key,f] of Object.entries(feeds)){if(f.error||f.stale||(f.data&&(!f.updatedAt||Date.now()-Date.parse(f.updatedAt)>1200000)))add(({weather:'Weather',news:'Canadian news',usnews:'U.S. news',sports:'Sports news',scores:'Sports scores'}[key]||key)+(f.data?' is using cached data':' is unavailable'),'/');}
 if(feeds?.scores?.data?.unavailable?.length)add('Some sports scoreboards are unavailable','/');
 const racing=results[3].value;
 if(racing){if(racing.errors.length)add('Saved racing picks need attention','/woodbine');if(racing.scratches.error||racing.scratches.snapshot)add('Latest daily scratch feed has not been confirmed','/woodbine');
 if(racing.scratches.available&&!racing.scratches.snapshot){const keys=racing.scratches.items.map(s=>`${s.race}|${s.pp}|${s.name}|${s.reason}`);let previous=null;try{previous=JSON.parse(localStorage.getItem('dashboard-scratches-'+racing.date));localStorage.setItem('dashboard-scratches-'+racing.date,JSON.stringify(keys));}catch{}
 const added=Array.isArray(previous)?keys.filter(k=>!previous.includes(k)).length:0;
 if(added)add(`${added} new scratch${added===1?'':'es'} since your last check`,'/woodbine');else if(keys.length)add(`${keys.length} reported scratch${keys.length===1?'':'es'} on today’s card`,'/woodbine');}}
 const el=document.getElementById('attention-strip');const wasOpen=el.querySelector('details')?.open;el.classList.toggle('has-notices',!!notices.length);el.innerHTML=`<details${wasOpen?' open':''}><summary><span class="attention-heading">${notices.length?'Needs attention':'Status check'}</span><span>${notices.length?notices.length+' notice'+(notices.length===1?'':'s'):'No issues found in the checks available'} · tap for details</span></summary><div class="attention-items">${notices.length?notices.map(n=>`<a href="${n.url}">${esc(n.text)} <span>↗</span></a>`).join(''):'<p>Checked active jobs, gateways, weekday stock reports, briefing feeds, and today’s scratches. Direct cron run history is unavailable. Stock deadlines allow 15 minutes after their scheduled time.</p>'}</div><p class="attention-checked">Checked ${esc(formatted(new Date().toISOString()))}</p></details>`;
 window.dispatchEvent(new CustomEvent('dashboard:attention',{detail:{notices,racing,stocks:stocksData,jobs:jobsData}}));
}
loadAttention();setInterval(loadAttention,60000);
