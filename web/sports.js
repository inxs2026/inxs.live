"use strict";
const sportsLeagues=['NHL','MLB','NFL'];let standingLeague=(location.pathname.match(/\/sports\/(nhl|mlb|nfl)/i)?.[1]||'NHL').toUpperCase(),scoreRequest=0,standingRequest=0;
function torontoDate(){return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());}
function moveSportsDate(value,days){const d=new Date(value+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+days);return d.toISOString().slice(0,10);}
function sportsDateLabel(value){return new Intl.DateTimeFormat('en-CA',{timeZone:'UTC',weekday:'long',month:'short',day:'numeric',year:'numeric'}).format(new Date(value+'T12:00:00Z'));}
function sportsOdds(g){
 if(g.state==='post'||!g.odds)return '';
 const o=g.odds,markets=o.markets;
 if(!markets)return '<div class="game-odds-unavailable">Odds '+(o.stale?'temporarily unavailable':'not posted for this game')+'</div>';
 const row=(label,key)=>`<div class="game-odds-row"><span>${label}</span><strong>${esc(markets.away?.[key]||'—')}</strong><strong>${esc(markets.home?.[key]||'—')}</strong></div>`;
 return `<section class="game-odds" aria-label="Game odds"><div class="game-odds-head"><span>Odds · Vegas</span><span>${esc(g.teams[0]?.name)}</span><span>${esc(g.teams[1]?.name)}</span></div>${row('Moneyline','moneyline')}${row(g.league==='NHL'?'Puck line':g.league==='MLB'?'Run line':'Spread','spread')}${row('Total','total')}<div class="game-odds-foot"><a href="${esc(o.url)}" target="_blank" rel="noopener noreferrer">ScoresAndOdds ↗</a><span>Checked ${esc(new Intl.DateTimeFormat('en-CA',{hour:'numeric',minute:'2-digit',timeZone:'America/Toronto'}).format(new Date(o.updatedAt)))}</span></div></section>`;
}
function sportsGame(g){return `<article class="game"><a class="game-matchup" href="https://www.espn.com/${({NHL:'nhl',MLB:'mlb',NFL:'nfl'})[g.league]||''}/game/_/gameId/${encodeURIComponent(g.id)}" target="_blank" rel="noopener noreferrer"><div class="game-title ${g.state==='in'?'live':''}"><span>${g.state==='in'?'● LIVE':g.state==='post'?'FINAL':esc(formatted(g.date))}</span><span>${esc(g.status)}</span></div><div class="game-teams">${scoreTeamMarkup(g.teams[0],'away')}<div class="game-middle"><span class="game-score ${g.state==='pre'?'pregame':''}">${g.state==='pre'?'VS':esc(g.teams[0]?.score)+' – '+esc(g.teams[1]?.score)}</span>${g.league==='MLB'&&g.seriesSummary?`<span class="game-series">${esc(g.seriesSummary)}</span>`:''}</div>${scoreTeamMarkup(g.teams[1],'home')}</div></a>${sportsOdds(g)}</article>`;}
function renderSportsScores(data,date,stale=false){
 $('sports-scoreboards').innerHTML=[standingLeague].map(name=>{const league=data.leagues.find(l=>l.league===name);return `<section class="panel sports-panel"><header class="sports-league-heading">${scoreLeagueMarkup(name,league?.logo,league?.events.length)}</header><div class="score-list">${!league?'<p class="empty">This league’s scores are unavailable. Retrying automatically.</p>':league.events.map(g=>sportsGame({...g,league:name,odds:stale&&g.odds?{...g.odds,markets:null,stale:true}:g.odds})).join('')||`<p class="empty">${date>torontoDate()?'No games listed for this date yet.':'No games listed for this date.'}</p>`}</div></section>`;}).join('');applyScoreTeamColors($('sports-scoreboards'));
}
async function loadSportsScores(){
 const date=$('sports-date').value,request=++scoreRequest;
 $('sports-previous').disabled=date<='2000-01-01';$('sports-next').disabled=date>='2099-12-31';
 for(const [id,offset] of [['sports-today',0],['sports-yesterday',-1],['sports-tomorrow',1]]){$(id).classList.toggle('selected',date===moveSportsDate(torontoDate(),offset));$(id).setAttribute('aria-pressed',String(date===moveSportsDate(torontoDate(),offset)));}
 if($('sports-scoreboards').dataset.date!==date){$('sports-scoreboards').innerHTML='<p class="empty">Loading games for this date…</p>';$('sports-scoreboards').dataset.date=date;}
 try{const f=await getJSON('/api/sports-scores?date='+encodeURIComponent(date));if(request!==scoreRequest)return;
  if(!f.data)throw new Error('Unavailable');renderSportsScores(f.data,date,f.stale);
  $('scores-updated').textContent=sportsDateLabel(date)+' · '+(f.stale?'Last confirmed scores · ':'Updated ')+formatted(f.updatedAt)+(f.error?' · '+f.error:'')+(f.data.unavailable?.includes(standingLeague)?' · '+standingLeague+' unavailable':'');
 }catch{if(request!==scoreRequest)return;$('scores-updated').textContent=sportsDateLabel(date)+' · Scores unavailable. Retrying automatically.';if(!$('sports-scoreboards').querySelector('.sports-panel'))$('sports-scoreboards').innerHTML='<p class="empty">Could not load games for this date.</p>';}
}
const standingColumns={
 NHL:[['GP','gamesPlayed','Games played'],['W','wins','Wins'],['L','losses','Losses'],['OTL','otLosses','Overtime losses'],['PTS','points','Points'],['RW','regWins','Regulation wins'],['ROW','rotWins','Regulation and overtime wins'],['GF','pointsFor','Goals for'],['GA','pointsAgainst','Goals against'],['DIFF','pointDifferential','Goal differential'],['HOME','Home','Home record'],['AWAY','Road','Away record'],['L10','Last Ten Games','Last ten games'],['STRK','streak','Current streak']],
 MLB:[['GP','gamesPlayed','Games played'],['W','wins','Wins'],['L','losses','Losses'],['PCT','winPercent','Winning percentage'],['GB','gamesBehind','Games behind'],['RS','pointsFor','Runs scored'],['RA','pointsAgainst','Runs allowed'],['DIFF','pointDifferential','Run differential'],['HOME','Home','Home record'],['AWAY','Road','Away record'],['L10','Last Ten Games','Last ten games'],['STRK','streak','Current streak']],
 NFL:[['W','wins','Wins'],['L','losses','Losses'],['T','ties','Ties'],['PCT','winPercent','Winning percentage'],['PF','pointsFor','Points for'],['PA','pointsAgainst','Points against'],['DIFF','pointDifferential','Point differential'],['HOME','Home','Home record'],['AWAY','Road','Away record'],['DIV','divisionRecord','Division record'],['CONF','vs. Conf.','Conference record'],['STRK','streak','Current streak']]
};
const standingViews={NHL:[['eastern','Eastern'],['western','Western'],['wildcard','Wild Card'],['playoffs','Playoffs']],MLB:[['american','American League'],['national','National League'],['expanded','Expanded'],['wildcard','Wild Card'],['playoffs','Playoffs']],NFL:[['afc','AFC'],['nfc','NFC'],['wildcard','Wild Card'],['playoffs','Playoffs']]};
const savedStandingViews={};let standingView=standingViews[standingLeague][0][0],standingData=null;
function renderStandingTabs(){
 $('standings-tabs').innerHTML=standingViews[standingLeague].map(([key,label])=>`<button type="button" data-standing-view="${key}" class="${standingView===key?'selected':''}" aria-pressed="${standingView===key}">${label}</button>`).join('');
 for(const button of $('standings-tabs').querySelectorAll('[data-standing-view]'))button.addEventListener('click',()=>selectStandingView(button.dataset.standingView));
}
function selectStandingView(view){
 if(!standingViews[standingLeague].some(([key])=>key===view))return;
 standingView=view;savedStandingViews[standingLeague]=view;renderStandingTabs();
 if(standingData?.league===standingLeague&&(view!=='playoffs'||Object.hasOwn(standingData,'postseason')))renderStandings(standingData);
 else{$('sports-standings').innerHTML='<p class="empty">Loading standings…</p>';loadSportsStandings();}
}
function renderStandings(data){
 const wildcard=standingView==='wildcard',playoffs=standingView==='playoffs',conferenceView=data.league==='NFL'&&['afc','nfc'].includes(standingView)&&!!data.views?.wildcard;
 let cols=standingColumns[data.league];
 if(wildcard&&data.league==='MLB')cols=cols.map(c=>c[0]==='GB'?['WCGB','wildCardBehind','Games behind the final wild-card spot; + means ahead']:c);
 let groups=data.views?.[standingView]||data.groups;
 if(conferenceView){const conference=standingView==='afc'?'American Football Conference':'National Football Conference';groups=data.views.wildcard.filter(g=>g.name.startsWith(conference+' · '));}
 let html=wildcard||playoffs||conferenceView?`<p class="sports-note">${esc(data.wildCardNote||'Current playoff picture. Qualification is not yet confirmed.')}${wildcard?' · Holding a spot = currently inside the cutoff. Chasing = currently outside. All teams are listed: division positions first, then wild-card spots and teams below the cutoff.':''}</p>`:'';
 if(playoffs){
  const games=data.postseason||[],rounds=[...new Set(games.map(g=>g.round))];
  html+=games.length?`<div class="postseason-games sports-scoreboards">${rounds.map(round=>`<section class="panel sports-panel"><h3 class="sports-league-heading">${esc(round)}</h3><div class="score-list">${games.filter(g=>g.round===round).sort((a,b)=>a.date.localeCompare(b.date)).map(sportsGame).join('')}</div></section>`).join('')}</div>`:'<p class="empty postseason-empty">No confirmed postseason matchups for this season yet. The current playoff picture is below; playoff rounds and championship games will appear when scheduled.</p>';
 }
 html+=wildcard||conferenceView?wildCardMarkup(data,groups,cols,!conferenceView):groups.map(group=>`<section class="panel standing-group"><h3>${esc(group.name)}</h3><div class="standing-scroll" tabindex="0" role="region" aria-label="${esc(group.name)} standings; scroll for more statistics"><table class="standing-table"><thead><tr><th scope="col">Team</th>${cols.map(([label,,description])=>`<th scope="col" title="${esc(description)}">${label}</th>`).join('')}</tr></thead><tbody>${group.rows.map((row,index)=>`<tr class="${group.cutoff&&index===group.cutoff?'wildcard-cutoff':''}"><th scope="row"><span class="standing-rank">${index+1}</span>${scoreTeamMarkup(row.team,'away')}<span class="standing-name">${esc(row.team.displayName||row.team.name)}</span>${row.inSpot?'<span class="standing-spot" title="Currently in a wild-card position">WC</span>':''}</th>${cols.map(([,key])=>`<td>${esc(row.stats[key]??'—')}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`).join('');
 $('sports-standings').innerHTML=html;applyScoreTeamColors($('sports-standings'));
}
function wildCardMarkup(data,groups,cols,showSummary=true){
 const races=groups.filter(g=>g.cutoff),automatic=groups.filter(g=>!g.cutoff);
 const record=row=>data.league==='NHL'?`${row.stats.points??'—'} points`:`${row.stats.wins??'—'}–${row.stats.losses??'—'}${data.league==='NFL'?'–'+(row.stats.ties??'0'):''}`;
 const teamName=row=>row.team.displayName||row.team.name;
 const eliminated=row=>String(row.stats.clincher||'').toLowerCase()==='e';
 const clinched=row=>/^[xyz*]$/i.test(String(row.stats.clincher||''));
 const gap=(row,group,index)=>{
  if(eliminated(row))return 'Eliminated from playoff contention';
  if(index<group.cutoff)return `WC${index+1}${index===group.cutoff-1?' · FINAL WILD-CARD SPOT':''} · ${clinched(row)?'Clinched playoff berth':'Holding a spot'}`;
  const last=group.rows[group.cutoff-1];
  if(data.league==='NHL'&&row.values?.points!=null&&last?.values?.points!=null){const difference=last.values.points-row.values.points;return difference===0?'Tied on points · outside on tiebreaker':`${difference} point${difference===1?'':'s'} behind final spot`;}
  if(data.league==='MLB'&&row.stats.wildCardBehind!=null){const value=row.stats.wildCardBehind;return value==='—'?'Tied · outside on tiebreaker':`${value} games behind final spot`;}
  return `${index-group.cutoff+1} place${index===group.cutoff?'':'s'} outside cutoff`;
 };
 return races.map(group=>{
  const conference=group.name.replace(/ · Wild card race$/,'');
  const inRows=group.rows.slice(0,group.cutoff),last=inRows.at(-1);
  const chaseClosed=group.rows.slice(group.cutoff).length>0&&group.rows.slice(group.cutoff).every(eliminated);
 const leaders=automatic.find(g=>g.name.startsWith(conference+' · '));
  const leaderRows=leaders?`<tr class="wildcard-section"><th colspan="${cols.length+1}">${data.league==='NHL'?'TOP THREE IN EACH DIVISION':'DIVISION LEADERS'} · AUTOMATIC PLAYOFF POSITIONS</th></tr>`+leaders.rows.map((row,index)=>`<tr class="wildcard-division"><th scope="row"><span class="standing-rank">${index+1}</span>${scoreTeamMarkup(row.team,'away')}<span class="standing-name">${esc(teamName(row))}</span><span class="wildcard-row-status">${data.league==='NHL'?'Division playoff position':'Division leader'} · ${clinched(row)?'Clinched playoff berth':'Currently in'} · Does not use a wild-card spot</span></th>${cols.map(([,key])=>`<td>${esc(row.stats[key]??'—')}</td>`).join('')}</tr>`).join(''):'';
  const tableRows=leaderRows+group.rows.map((row,index)=>`${index===0||index===group.cutoff||(eliminated(row)&&!eliminated(group.rows[index-1]))?`<tr class="wildcard-section ${index===group.cutoff?'wildcard-cutoff-label':''}"><th colspan="${cols.length+1}">${index===0?'HOLDING THE '+group.cutoff+' WILD-CARD SPOTS':eliminated(row)?'ELIMINATED · OUT OF PLAYOFF CONTENTION':'WILD-CARD CUTOFF ↑ · TEAMS BELOW ARE OUTSIDE THE PLAYOFF SPOTS'}</th></tr>`:''}<tr class="${index===group.cutoff?'wildcard-cutoff ':''}${index<group.cutoff?'wildcard-inside':eliminated(row)?'wildcard-eliminated':'wildcard-chasing'}"><th scope="row"><span class="standing-rank">${(leaders?.rows.length||0)+index+1}</span>${scoreTeamMarkup(row.team,'away')}<span class="standing-name">${esc(teamName(row))}</span><span class="wildcard-row-status">${esc(gap(row,group,index))}</span></th>${cols.map(([,key])=>`<td>${esc(row.stats[key]??'—')}</td>`).join('')}</tr>`).join('');
  return `<section class="panel standing-group wildcard-group"><h3>${esc(conference)} · ${showSummary?'Wild card race':'Playoff standings · All 16 teams'}</h3>${showSummary?`<div class="wildcard-summary"><p class="wildcard-summary-label">Holding the ${group.cutoff} wild-card spots</p><div class="wildcard-spots">${inRows.map((row,index)=>`<article class="wildcard-spot"><span class="wildcard-slot">WC ${index+1}${index===group.cutoff-1?' · FINAL SPOT':''}</span><div>${scoreTeamMarkup(row.team,'away')}<strong>${esc(teamName(row))}</strong></div><span>${esc(record(row))}${clinched(row)?' · Clinched playoff berth':''}</span></article>`).join('')}</div><p class="wildcard-cutoff-note">${last?`The team to catch: <strong>${esc(teamName(last))}</strong> (${esc(record(last))}). `:''}${chaseClosed?'The wild-card field is settled: all remaining teams are eliminated. Open Playoffs for current postseason progress.':`Chasing teams must move into the top ${group.cutoff}. Eliminated teams can no longer qualify.`} Tied records follow the provider’s tiebreaker ranking.</p></div>`:''}<div class="standing-scroll" tabindex="0" role="region" aria-label="${esc(conference)} wild-card standings"><table class="standing-table"><thead><tr><th scope="col">Team / race status</th>${cols.map(([label,,description])=>`<th scope="col" title="${esc(description)}">${label}</th>`).join('')}</tr></thead><tbody>${tableRows}</tbody></table></div></section>`;
 }).join('');
}
async function loadSportsStandings(){const league=standingLeague,request=++standingRequest;
 try{const f=await getJSON('/api/sports-standings?league='+league+(standingView==='playoffs'?'&view=playoffs':''));if(request!==standingRequest)return;if(!f.data)throw new Error('Unavailable');standingData=f.data;renderStandings(f.data);$('standings-updated').textContent=league+' · '+(f.data.season||'Current season')+' · ESPN · '+(f.stale?'Last confirmed ':'Updated ')+formatted(f.updatedAt)+(f.error?' · '+f.error:'');}
 catch{if(request!==standingRequest)return;$('standings-updated').textContent=league+' standings unavailable. Retrying automatically.';}
}
$('sports-date').value=torontoDate();$('sports-date').addEventListener('change',()=>{if($('sports-date').checkValidity())loadSportsScores();});
for(const [id,offset] of [['sports-today',0],['sports-yesterday',-1],['sports-tomorrow',1]])$(id).addEventListener('click',()=>{$('sports-date').value=moveSportsDate(torontoDate(),offset);loadSportsScores();});
for(const [id,offset] of [['sports-previous',-1],['sports-next',1]])$(id).addEventListener('click',()=>{$('sports-date').value=moveSportsDate($('sports-date').value,offset);loadSportsScores();});
function selectSportsLeague(league,updateURL=true){
 if(!sportsLeagues.includes(league))return;standingLeague=league;standingView=savedStandingViews[league]||standingViews[league][0][0];standingData=null;renderStandingTabs();
 for(const button of document.querySelectorAll('[data-standing-league]')){const selected=button.dataset.standingLeague===league;button.classList.toggle('selected',selected);button.setAttribute('aria-pressed',String(selected));}
 $('league-scores-heading').textContent=league+' scores';$('league-standings-heading').textContent=league+' standings';
 if(updateURL)history.pushState({},'', '/sports/'+league.toLowerCase());
 $('sports-scoreboards').innerHTML='<p class="empty">Loading '+league+' games…</p>';$('sports-standings').innerHTML='<p class="empty">Loading '+league+' standings…</p>';
 $('standings-updated').textContent='Loading '+league+' standings…';loadSportsScores();loadSportsStandings();
}
for(const button of document.querySelectorAll('[data-standing-league]')){button.innerHTML=scoreLeagueMarkup(button.dataset.standingLeague);button.addEventListener('click',()=>selectSportsLeague(button.dataset.standingLeague));}
window.addEventListener('popstate',()=>selectSportsLeague((location.pathname.split('/')[2]||'NHL').toUpperCase(),false));
selectSportsLeague(standingLeague,false);
setInterval(()=>{if(!document.hidden)loadSportsScores();},60000);setInterval(()=>{if(!document.hidden)loadSportsStandings();},600000);document.addEventListener('visibilitychange',()=>{if(!document.hidden){loadSportsScores();loadSportsStandings();}});
