'use strict';
const stockMoney=v=>typeof v==='number'?v.toLocaleString('en-CA',{minimumFractionDigits:2,maximumFractionDigits:2}):'—';
const stockReportTime=v=>new Intl.DateTimeFormat('en-CA',{year:'numeric',month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZone:'America/Toronto',timeZoneName:'short'}).format(new Date(v));
async function loadStocks(){
 try{
  const data=await getJSON('/api/stocks');
  document.getElementById('stock-archive').innerHTML=data.archives?.map(r=>`<a href="${esc(r.document)}" target="_blank" rel="noopener noreferrer">${esc(r.date)} · ${r.slot==='morning'?'Morning':'Afternoon'} PDF ↗</a>`).join('')||'<p>No archived PDFs available yet.</p>';
  for(const slot of ['morning','afternoon']){
   const el=document.getElementById('stocks-'+slot), report=data.reports[slot],run=data.latestRuns?.[slot],pricesOpen=el.querySelector('.stock-prices')?.open;
   if(!report){el.innerHTML='<p class="stock-empty">'+freshnessBadge('unavailable')+' No saved report available yet. The next successful scheduled report will appear here.</p>';continue;}
   const overdue=report.date<expectedStockDate(slot);
   el.innerHTML=`<div class="stock-report-meta"><span>${freshnessBadge(overdue?'overdue':report.isToday?'current':'older')} Saved ${esc(stockReportTime(report.generatedAt))} · ${report.isToday?'Today’s report':'Older saved report'}</span>${report.document?`<a href="${safeURL(new URL(report.document,location.origin).href)}" target="_blank" rel="noopener noreferrer">Open PDF ↗</a>`:''}</div>${run?.date>report.date?`<p class="stock-archive-note">Latest scheduled report succeeded ${esc(stockReportTime(run.generatedAt))}, but its price snapshot was not archived. Showing the older saved prices below.</p>`:!report.isToday?'<p class="stock-archive-note">Showing the most recent saved report. New PDFs arrive Monday–Friday after the scheduled run.</p>':''}<p class="stock-source">${esc(report.source)} · ${report.stocks.length} symbols · Saved prices${report.recovered?' · Recovered from original PDF':''}</p><details class="stock-prices"${pricesOpen?' open':''}><summary>View ${report.stocks.length} saved stock prices</summary><div class="stock-columns"><span>Stock / company</span><span>Price · daily change</span></div>${report.stocks.map(s=>`<div class="stock-row"><div><strong>${esc(s.symbol.replace(/\.TO$/,''))}</strong><small>${esc(s.name)}</small></div><div class="stock-values"><strong>$${stockMoney(s.price)}</strong><small class="${s.change>0?'stock-up':s.change<0?'stock-down':'stock-flat'}">${s.change>0?'+':s.change<0?'−':''}$${stockMoney(Math.abs(s.change))}${typeof s.changePct==='number'?' · '+(s.changePct>0?'+':'')+s.changePct.toFixed(2)+'%':''}</small></div></div>`).join('')}</details>`;
  }
 }catch{for(const slot of ['morning','afternoon']){const el=document.getElementById('stocks-'+slot);markCached(el);if(!el.querySelector('.stock-row'))el.textContent='Saved reports temporarily unavailable. Retrying automatically.';}}
}
loadStocks();setInterval(loadStocks,30000);

let quoteData=null;
const quoteState=s=>({REGULAR:'Market open',CLOSED:'Market closed',PRE:'Pre-market',PREPRE:'Before market',POST:'After market',POSTPOST:'Market closed'}[s]||'Market status unavailable');
function quoteDelay(q){return q.delayMinutes==null?'Delay not supplied':q.delayMinutes>0?`${q.delayMinutes} min delayed`:'No reported delay';}
function renderQuotes(){
 const d=quoteData;if(!d)return;
 const symbols=d.quotes||[],query=document.getElementById('quote-search').value.trim().toLowerCase(),sort=document.getElementById('quote-sort').value;
 const rows=symbols.filter(q=>[q.symbol,q.name].some(v=>String(v).toLowerCase().includes(query))).slice();
 rows.sort((a,b)=>sort==='symbol'?a.symbol.localeCompare(b.symbol):(a.changePct==null)-(b.changePct==null)||(sort==='gainers'?-1:1)*((a.changePct||0)-(b.changePct||0))||a.symbol.localeCompare(b.symbol));
 const states=[...new Set(symbols.filter(q=>q.available).map(q=>q.marketState))];
 const state=states.length===1?quoteState(states[0]):states.length?'Mixed market sessions':'Market status unavailable';
 document.getElementById('quote-status').innerHTML=`${freshnessBadge(d.cached?'cached':symbols.length?'current':'unavailable',d.cached?'Cached quotes':symbols.length?'Auto-updating':'Fetching quotes')} ${esc(d.cached?'Last reported: '+state:state)}${d.fetchedAt?' · Fetched '+esc(stockReportTime(d.fetchedAt)):''}<span class="quote-status-note">${d.error?esc(d.error):d.refreshing?'Checking the provider…':`Next check ${esc(formatted(d.nextCheckAt))} · ${d.refreshSeconds===180?'Every 3 minutes during trading':'Slower checks while markets are closed'}`}</span>`;
 const up=symbols.filter(q=>q.change>0).length,down=symbols.filter(q=>q.change<0).length,flat=symbols.filter(q=>q.change===0).length;
 document.getElementById('quote-summary').innerHTML=`<span><strong>${symbols.length}</strong> stocks</span><span class="stock-up"><strong>${up}</strong> up</span><span class="stock-down"><strong>${down}</strong> down</span><span><strong>${flat}</strong> unchanged</span>${symbols.some(q=>!q.available)?'<span>Some quotes unavailable</span>':''}`;
 document.getElementById('quote-list').innerHTML=rows.map(q=>{
  const amount=q.change,percent=q.changePct,tone=amount>0?'stock-up':amount<0?'stock-down':'stock-flat';
  const older=q.quoteAt&&q.marketState==='REGULAR'&&Date.now()-Date.parse(q.quoteAt)>((q.delayMinutes||0)+15)*60000;
  return `<article class="quote-row"><div class="quote-company"><h3>${esc(q.symbol.replace(/\.TO$/,''))} <span>${esc(q.currency||'Currency unavailable')}</span></h3><p>${esc(q.name)}</p><small>${esc(q.exchange||'Exchange unavailable')}</small></div><div class="quote-values"><strong>${q.available?'$'+stockMoney(q.price):'—'}</strong><span class="${tone}">${typeof amount==='number'?(amount>0?'+':amount<0?'−':'')+'$'+stockMoney(Math.abs(amount)):'Change unavailable'}${typeof percent==='number'?' · '+(percent>0?'+':'')+percent.toFixed(2)+'%':''}</span></div><div class="quote-timing"><span>${freshnessBadge(!q.available?'unavailable':d.cached?'cached':older?'older':q.delayMinutes>0?'older':'current',!q.available?'Quote unavailable':d.cached?'Cached':older?'Older quote':quoteDelay(q))}</span><small>${q.quoteAt?'Quote '+esc(stockReportTime(q.quoteAt)):'Quote time not supplied'}</small>${older||d.cached?`<small>${esc(quoteDelay(q))}</small>`:''}<small>${esc((d.cached?'Last reported: ':' ')+quoteState(q.marketState))}</small></div></article>`;
 }).join('')||`<p class="stock-empty">${symbols.length?'No stocks match your search.':d.error?esc(d.error):'Fetching quotes for your full watchlist…'}</p>`;
}
async function loadQuotes(){
 const button=document.getElementById('quote-refresh');button.classList.add('busy');
 try{quoteData=await getJSON('/api/stock-quotes');renderQuotes();}catch{if(quoteData){quoteData.cached=true;quoteData.error='Dashboard connection lost. Showing the last loaded quotes; retrying automatically.';renderQuotes();}else document.getElementById('quote-status').textContent='Quotes could not be loaded. Retrying automatically.';}finally{button.classList.remove('busy');}
}
document.getElementById('quote-search').addEventListener('input',renderQuotes);document.getElementById('quote-sort').addEventListener('change',renderQuotes);document.getElementById('quote-refresh').addEventListener('click',loadQuotes);
loadQuotes();setInterval(loadQuotes,30000);
