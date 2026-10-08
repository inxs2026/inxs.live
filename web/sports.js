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
function renderStandings(data){const cols=standingColumns[data.league];$('sports-standings').innerHTML=data.groups.map(group=>`<section class="panel standing-group"><h3>${esc(group.name)}</h3><div class="standing-scroll" tabindex="0" role="region" aria-label="${esc(group.name)} standings; scroll for more statistics"><table class="standing-table"><thead><tr><th scope="col">Team</th>${cols.map(([label,,description])=>`<th scope="col" title="${esc(description)}">${label}</th>`).join('')}</tr></thead><tbody>${group.rows.map(row=>`<tr><th scope="row">${scoreTeamMarkup(row.team,'away')}<span class="standing-name">${esc(row.team.displayName||row.team.name)}</span></th>${cols.map(([,key])=>`<td>${esc(row.stats[key]??'—')}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`).join('');applyScoreTeamColors($('sports-standings'));}
async function loadSportsStandings(){const league=standingLeague,request=++standingRequest;
 try{const f=await getJSON('/api/sports-standings?league='+league);if(request!==standingRequest)return;if(!f.data)throw new Error('Unavailable');renderStandings(f.data);$('standings-updated').textContent=league+' · '+(f.data.season||'Current season')+' · ESPN · '+(f.stale?'Last confirmed ':'Updated ')+formatted(f.updatedAt)+(f.error?' · '+f.error:'');}
 catch{if(request!==standingRequest)return;$('standings-updated').textContent=league+' standings unavailable. Retrying automatically.';}
}
$('sports-date').value=torontoDate();$('sports-date').addEventListener('change',()=>{if($('sports-date').checkValidity())loadSportsScores();});
for(const [id,offset] of [['sports-today',0],['sports-yesterday',-1],['sports-tomorrow',1]])$(id).addEventListener('click',()=>{$('sports-date').value=moveSportsDate(torontoDate(),offset);loadSportsScores();});
for(const [id,offset] of [['sports-previous',-1],['sports-next',1]])$(id).addEventListener('click',()=>{$('sports-date').value=moveSportsDate($('sports-date').value,offset);loadSportsScores();});
function selectSportsLeague(league,updateURL=true){
 if(!sportsLeagues.includes(league))return;standingLeague=league;
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
