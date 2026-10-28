'use strict';
let claimsSnapshot = null, claimsLoading = false;
const claimsMoney = value => 'C$' + Number(value).toLocaleString('en-CA', {maximumFractionDigits:0});
const claimsDate = value => new Intl.DateTimeFormat('en-CA', {timeZone:'UTC',month:'long',day:'numeric',year:'numeric'}).format(new Date(value+'T12:00:00Z'));
function claimsTrainer(value){const text=String(value||'');if(!text.includes(','))return text;const at=text.lastIndexOf(',');return (text.slice(at+1).trim()+' '+text.slice(0,at).trim());}
function claimsFinish(value){if(!Number.isInteger(value))return String(value||'N/A');const tens=value%100;const suffix=tens>=11&&tens<=13?'th':({1:'st',2:'nd',3:'rd'}[value%10]||'th');return value+suffix;}
function claimItem(c){return `<article class="claims-item"><p class="claims-previous"><strong class="claims-horse">Race ${esc(c.race)} - ${esc(c.horse)}</strong> · Previous owner: ${esc(c.previous_owner)}; trainer: ${esc(claimsTrainer(c.previous_trainer))}</p><p class="claims-new"><strong>Finish: ${esc(claimsFinish(c.finish_position))} · Claim: ${esc(claimsMoney(c.claim_price_cad))}</strong> · New owner: ${esc(c.new_owner)}; trainer: ${esc(c.new_trainer)}</p></article>`;}
function renderClaims(data){
 if(data.complete!==true||data.track!=='Woodbine'||!Array.isArray(data.claims)||!data.daily)throw new Error('Unverified claims report');
 const daily=data.daily;
 $('claims-daily-title').textContent='Latest Completed Card - '+claimsDate(daily.date);
 $('claims-daily-meta').textContent=daily.races_checked.length+' races checked. All amounts in Canadian dollars.';
 $('claims-daily').innerHTML=daily.claims.length?daily.claims.map(claimItem).join(''):'<p class="claims-empty">No Claims on Todays Card</p>';
 $('claims-daily-total').textContent=daily.total_claims+' claims | '+claimsMoney(daily.total_claim_value_cad)+' total';
 $('claims-year-title').textContent='All '+data.year+' Claims';
 $('claims-year-total').textContent=data.total_claims+' claims | '+claimsMoney(data.total_claim_value_cad)+' total';
 $('claims-year-meta').textContent=data.completed_cards+' completed cards checked, '+data.coverage_start+' through '+data.coverage_through+'. Newest date first; race numbers in order. All amounts CAD.';
 let previous=null, html='';
 for(const c of data.claims){if(previous!==c.date){html+='<h3>'+esc(claimsDate(c.date))+'</h3>';previous=c.date;}html+=claimItem(c);}
 $('claims-year').innerHTML=html||'<p class="claims-empty">No claims recorded for this year.</p>';
 $('claims-coverage').textContent='Coverage through '+claimsDate(data.coverage_through)+'. '+data.cancelled_cards.length+' fully cancelled cards checked separately.';
 const checked=data.refresh?.last_checked_at||data.checked_at;
 const stale=Boolean(data.refresh?.stale);
 $('claims-status').textContent=(stale?(data.refresh?.error||'The update check is overdue; showing the last complete report.')+' ':'')+'Results through '+claimsDate(data.coverage_through)+'. Last checked '+formatted(checked)+'. Updates hourly Thursday-Sunday, 3 pm through midnight (Toronto).';
 $('claims-status').classList.toggle('claims-warning',stale);
 claimsSnapshot=data;
}
async function loadClaims(){
 if(claimsLoading)return;claimsLoading=true;$('claims-refresh').classList.add('busy');
 try{renderClaims(await getJSON('/api/woodbine-claims'));}
 catch(error){$('claims-status').textContent=claimsSnapshot?'The connection is unavailable; showing the last loaded report. Retrying automatically.':'Claims could not be loaded. Retrying automatically.';$('claims-status').classList.add('claims-warning');}
 finally{claimsLoading=false;$('claims-refresh').classList.remove('busy');}
}
$('claims-refresh').addEventListener('click',loadClaims);
loadClaims();setInterval(loadClaims,60000);
