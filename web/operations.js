'use strict';
const opsTime = value => value ? new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',hour:'numeric',minute:'2-digit'}).format(new Date(value)) : '—';
const opsDate = value => value ? (/^\d{4}-\d{2}-\d{2}$/.test(value) ? new Intl.DateTimeFormat('en-CA',{timeZone:'UTC',month:'short',day:'numeric',year:'numeric'}).format(new Date(value+'T12:00:00Z')) : formatted(value)) : 'Not available';
const bytes = n => n == null ? '—' : n >= 1024**3 ? (n/1024**3).toFixed(1)+' GB' : (n/1024**2).toFixed(0)+' MB';
function badge(state,text){return `<span class="ops-badge ${esc(state)}">${esc(text)}</span>`;}
function workflowCard(w){
 const labels={ran:w.jobs.length>1?'Latest step succeeded':'Run succeeded',attention:'Needs attention',scheduled:'Scheduled'};
 const time=w.repeating?'Recurring':w.dueTimes.length?opsTime(w.dueTimes[0]):opsTime(w.lastRun);
 const additional=w.nextToday?`Next ${opsTime(w.nextToday)}`:w.lastRun?`Last activity ${opsTime(w.lastRun)}`:'Run history unavailable';
 const report=w.report.url?`<a class="${esc(w.report.state)}" href="${esc(w.report.url)}">${esc(w.report.label)}${w.report.date?' · '+esc(opsDate(w.report.date)):''} ↗</a>`:esc(w.report.label);
 const delivery=w.delivery.state==='confirmed'||w.delivery.state==='recorded';
 const proof=w.report.state==='unknown'&&!delivery?'Report & delivery not independently tracked':`<span><strong>Report</strong> · ${report}</span><span class="${delivery?'confirmed':''}"><strong>Delivery</strong> · ${esc(w.delivery.label)}${delivery&&w.delivery.date?' · '+esc(opsTime(w.delivery.date)):''}</span>`;
 return `<article class="workflow-card"><div class="workflow-time">${esc(time)}<small>${esc(additional)}</small></div><div class="workflow-main"><h3>${esc(w.name)}</h3><p class="workflow-meta">${esc(w.platform==='Both'?'Hermes & OpenClaw':w.platform)} · ${w.jobs.length} schedule${w.jobs.length===1?'':'s'}${w.lastRun?' · '+esc(formatted(w.lastRun)):''}</p><div class="workflow-evidence">${proof}</div><details class="workflow-steps"><summary>${w.jobs.length>1?'Schedules & steps':'Schedule details'}</summary>${w.jobs.map(j=>`<div class="workflow-step"><strong>${esc(j.name)}</strong><span>${esc(j.source)} · ${esc(j.result==='unknown'?'History unavailable':j.result)}${j.lastRun?' · '+esc(formatted(j.lastRun)):''}</span></div>`).join('')}</details></div>${badge(w.state,labels[w.state]||'Activity recorded')}</article>`;
}
async function loadTimeline(){
 if(!$('timeline-items'))return;
 try{const data=await getJSON('/api/timeline');const upkeep=w=>/heartbeat|patch|cleanup|maintenance|memory dreaming|watchdog|skill-collection/i.test(w.name+' '+w.id+' '+w.jobs.map(j=>j.id).join(' '));const primary=data.workflows.filter(w=>!upkeep(w)),background=data.workflows.filter(upkeep);const upcoming=primary.filter(w=>w.nextToday||w.state==='attention'),earlier=primary.filter(w=>!w.nextToday&&w.state!=='attention');
 $('timeline-summary').textContent=`${primary.length} workflows for ${opsDate(data.date)} · Toronto time`;
 const next=primary.filter(w=>w.nextToday).sort((a,b)=>Date.parse(a.nextToday)-Date.parse(b.nextToday))[0];
 $('summary-next').textContent=next?next.name:'No more timed workflows today';$('summary-next-note').textContent=next?opsTime(next.nextToday)+' · '+next.platform:'Later schedules remain in All schedules';
 $('timeline-items').innerHTML=upcoming.map(workflowCard).join('')||'<p class="empty">No more timed workflows today. Earlier activity is below.</p>';
 $('earlier-items').innerHTML=earlier.map(workflowCard).join('');$('earlier-summary').textContent=`Earlier today · ${earlier.length} workflows`;$('earlier-work').hidden=!earlier.length;
 $('background-items').innerHTML=background.map(workflowCard).join('');$('background-summary').textContent=`Background upkeep · ${background.length} workflows`;document.querySelector('.background-work').hidden=!background.length;
 $('timeline-checked').textContent=`Checked ${formatted(data.checkedAt)}. A successful step does not confirm report delivery.${data.errors.length?' Some schedule sources are unavailable.':''}`;
 }catch{$('timeline-summary').textContent='Timeline unavailable. Use All schedules to inspect the current inventory.';$('summary-next').textContent='Schedule check unavailable';$('summary-next-note').textContent='Use All schedules to review the inventory';}
}
function switchOverview(view){const today=view==='today';document.body.classList.toggle('today-view',today);$('timeline-panel').hidden=!today;$('schedules-panel').hidden=today;document.querySelectorAll('[data-overview-view]').forEach(b=>{b.classList.toggle('selected',b.dataset.overviewView===view);b.setAttribute('aria-pressed',String(b.dataset.overviewView===view));});}
if($('timeline-panel')){document.querySelectorAll('[data-overview-view]').forEach(b=>b.addEventListener('click',()=>switchOverview(b.dataset.overviewView)));$('refresh-timeline').addEventListener('click',loadTimeline);window.addEventListener('hashchange',()=>{if((location.hash==='#automations'||location.hash.startsWith('#job=')))switchOverview('schedules');else if(location.hash==='#timeline-panel')switchOverview('today');});switchOverview((location.hash==='#automations'||location.hash.startsWith('#job='))?'schedules':'today');loadTimeline();setInterval(loadTimeline,60000);}
window.addEventListener('dashboard:attention',({detail:d})=>{
 if(!$('summary-racing'))return;
 const r=d.racing, offDay=r?.schedule?.scheduled===false&&!r.races.length, available=r?.sources?.filter(s=>s.available).length||0;
 $('summary-racing').textContent=!r?'Racing check unavailable':offDay?'No racing scheduled today':r.races.length?`${r.races.length} races · ${available}/2 agents ready`:'No saved card for today';
 $('summary-racing-note').textContent=!r?'Check Woodbine Racing for details':offDay?(r.schedule.nextRaceDate?'Next race day · '+opsDate(r.schedule.nextRaceDate):'No further dates in the approved calendar'):r.races.length?`${r.scratches.snapshot||r.scratches.error?'Scratch feed not confirmed':r.scratches.items.length+' reported scratches'} · ${r.refreshing?'Checking updates':'Checked '+opsTime(r.scratches.checkedAt)}`:'This does not confirm a non-racing day';
 $('summary-attention').textContent=d.notices.length?d.notices.length+' notice'+(d.notices.length===1?'':'s'):d.acknowledged?.length?d.acknowledged.length+' acknowledged':'No issues found';
 $('summary-attention-note').textContent=d.notices.length?'Tap for job failures, missing reports and feed checks':d.acknowledged?.length?'Awaiting next run · New failures will alert again':'Within the checks currently available';
});
if($('summary-attention'))$('summary-attention').closest('a').addEventListener('click',()=>{const details=$('attention-strip').querySelector('details');if(details)details.open=true;});
async function loadSystemHealth(){
 if(!$('health-services'))return;
 try{const d=await getJSON('/api/system-health');const alerts=[];
 $('health-services').innerHTML=d.services.map(s=>`<article class="panel health-card"><h3>${esc(s.name)}</h3>${badge(s.state,s.state==='active'?'Online':s.state)}<p>${s.restarts?s.restarts+' automatic restarts since startup':'No automatic restarts since startup'}</p></article>`).join('');
 for(const s of d.services)if(s.state!=='active')alerts.push(`${s.name} is ${s.state}.`);
 $('health-storage').innerHTML=`<article class="panel health-card"><h3>Linux storage</h3><div class="disk-value">${esc(d.disk.percent)}% <small>used</small></div><div class="disk-meter"><div id="disk-fill" class="disk-fill"></div></div><p>${bytes(d.disk.free)} free of ${bytes(d.disk.total)}</p></article><article class="panel health-card"><h3>Machine uptime</h3><div class="disk-value">${d.uptimeSeconds==null?'—':Math.floor(d.uptimeSeconds/86400)+'d '+Math.floor(d.uptimeSeconds%86400/3600)+'h'}</div><p>Health checks refresh every five minutes.</p></article><article class="panel health-card"><h3>OpenClaw session cleanup</h3>${badge(d.maintenance.state,d.maintenance.state==='clear'?'No recent errors':d.maintenance.state==='attention'?'Needs attention':'Not checked')}<p>${d.maintenance.errors==null?'Cleanup logs could not be checked.':d.maintenance.errors+' relevant errors in the last '+d.maintenance.periodMinutes+' minutes.'}</p></article>`;
 $('disk-fill').style.width=Math.min(100,d.disk.percent)+'%';if(d.disk.percent>=90)alerts.push('Linux storage is nearing capacity.');if(d.maintenance.state==='attention')alerts.push('OpenClaw session cleanup has recent errors.');
 const labels={verified:'Content verified',uploaded:'Uploaded · not verified','check-failed':'Check unavailable',mismatch:'Content mismatch',unavailable:'No backup',checking:'Backup changing'};
 $('backup-cards').innerHTML=d.backups.map(b=>`<article class="panel backup-card"><h3>${esc(b.name)}</h3>${badge(b.state,labels[b.state]||b.state)}<p class="backup-name">${esc(b.filename||'No archive found')}</p><dl class="backup-stats"><div><dt>Backup date</dt><dd>${esc(b.date?opsDate(b.date):'—')}</dd></div><div><dt>Size</dt><dd>${bytes(b.size)}</dd></div></dl><p class="backup-note">${esc(b.note)}</p><p class="backup-note">${b.verifiedAt?'Verified '+esc(formatted(b.verifiedAt))+' · '+esc(b.checksum)+' checksum match':b.lastVerifiedAt?'Previously verified '+esc(formatted(b.lastVerifiedAt))+'; current check unavailable.':'Content verification has not been confirmed.'}</p><p class="backup-note schedule-note">${esc(b.schedule)}${b.scheduled&&!b.timerActive?' · timer not running':''}</p></article>`).join('');
 for(const b of d.backups)if(['mismatch','check-failed','unavailable'].includes(b.state))alerts.push(b.name+': '+labels[b.state]+'.');
 for(const b of d.backups){if(b.overdue)alerts.push(b.name+': expected a backup dated '+b.expectedDate+'.');if(b.scheduled&&!b.timerActive)alerts.push(b.name+': weekly timer is not running.');}
 $('health-alert').hidden=!alerts.length;$('health-alert').textContent=alerts.join(' ');$('health-checked').textContent='Checked '+formatted(d.checkedAt)+' · Cached for up to five minutes';
 }catch{$('health-alert').hidden=false;$('health-alert').textContent='Health check unavailable. Retrying automatically.';}
}
if($('health-services')){loadSystemHealth();setInterval(loadSystemHealth,60000);$('refresh-health').addEventListener('click',loadSystemHealth);}
