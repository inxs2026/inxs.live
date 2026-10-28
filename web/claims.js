'use strict';
let claimsSnapshot = null, claimsLoading = false;
const claimsMoney = value => 'C$' + Number(value).toLocaleString('en-CA', {maximumFractionDigits:0});
const claimsDate = value => new Intl.DateTimeFormat('en-CA', {timeZone:'UTC',month:'long',day:'numeric',year:'numeric'}).format(new Date(value+'T12:00:00Z'));
function claimsTrainer(value){const text=String(value||'');if(!text.includes(','))return text;const at=text.lastIndexOf(',');return (text.slice(at+1).trim()+' '+text.slice(0,at).trim());}
function claimsFinish(value){if(!Number.isInteger(value))return String(value||'N/A');const tens=value%100;const suffix=tens>=11&&tens<=13?'th':({1:'st',2:'nd',3:'rd'}[value%10]||'th');return value+suffix;}
function claimItem(c){return `<article class="claims-item"><p class="claims-previous"><strong class="claims-horse">Race ${esc(c.race)} - ${esc(c.horse)}</strong> · Previous owner: ${esc(c.previous_owner)}; trainer: ${esc(claimsTrainer(c.previous_trainer))}</p><p class="claims-new"><strong>Finish: ${esc(claimsFinish(c.finish_position))} · Claim: ${esc(claimsMoney(c.claim_price_cad))}</strong> · New owner: ${esc(c.new_owner)}; trainer: ${esc(c.new_trainer)}</p></article>`;}
// Woodbine price pairs offer a lower tag for a weight allowance.
// Group the price statistics only; individual claims and dollar totals retain actual prices.
function claimsPriceLevel(value){
 const amount=Number(value);
 const levels=[[7500,7000],[10000,9500],[15000,14000],[25000,23500]];
 const pair=levels.find(level=>level.includes(amount));
 return pair?{price:pair[0],label:claimsMoney(pair[0])+'–'+claimsMoney(pair[1])}:{price:amount,label:claimsMoney(amount)};
}
function claimsTopCounts(claims,field,price=false){
 const counts=new Map();
 for(const claim of claims){
  const raw=price?Number(claim[field]):String(claim[field]||'').replace(/\s+/g,' ').trim();
  const level=price?claimsPriceLevel(raw):null;
  const label=price?level.label:(raw||'Not reported');
  const key=price?String(level.price):label.normalize('NFKC').toLocaleLowerCase('en-CA');
  const item=counts.get(key)||{label,count:0,price:price?level.price:null};item.count++;counts.set(key,item);
 }
 return [...counts.values()].sort((a,b)=>b.count-a.count||(price?b.price-a.price:a.label.localeCompare(b.label,'en-CA'))).slice(0,7);
}
function renderClaimLeaders(claims){
 for(const [id,field,price] of [['claims-top-trainers','new_trainer',false],['claims-top-owners','new_owner',false],['claims-top-prices','claim_price_cad',true]]){
  const rows=claimsTopCounts(claims,field,price);
  $(id).innerHTML=rows.length?rows.map((row,index)=>`<li><span class="claims-rank">${index+1}</span><span>${esc(row.label)}</span><strong aria-label="${row.count} claims">${row.count}</strong></li>`).join(''):'<li class="claims-leaders-empty">No claims recorded.</li>';
 }
}
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
 renderClaimLeaders(data.claims);
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
