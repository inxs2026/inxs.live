"use strict";
function scoreTeamMarkup(team,side){
 const escape=value=>String(value??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
 const hex=value=>/^#[0-9a-f]{6}$/i.test(value||'')?value:'#8f8da4';
 let logo='';try{const u=new URL(team?.logo);if(u.protocol==='https:'&&u.hostname==='a.espncdn.com'&&!u.username&&!u.password)logo=u.href;}catch{}
 const name=escape(team?.name||'Team');
 return `<div class="game-team ${side==='home'?'home':'away'}" data-team-color="${hex(team?.color)}" data-team-alternate="${hex(team?.alternateColor||team?.color)}" title="${escape(team?.displayName||team?.name||'Team')}">${logo?`<img class="team-logo" src="${escape(logo)}" alt="" aria-hidden="true" width="44" height="44" loading="lazy" decoding="async" referrerpolicy="no-referrer">`:''}<strong>${name}</strong><span class="team-colors" aria-hidden="true"></span></div>`;
}
function applyScoreTeamColors(container){
 for(const team of container.querySelectorAll('[data-team-color]')){
  team.style.setProperty('--team-color',team.dataset.teamColor);team.style.setProperty('--team-alternate',team.dataset.teamAlternate);
  const game=team.closest('.game');if(game)game.style.setProperty(team.classList.contains('home')?'--home-color':'--away-color',team.dataset.teamColor+'24');
 }
 for(const image of container.querySelectorAll('.team-logo'))image.addEventListener('error',()=>{image.hidden=true;});
}

const officialLeagueLogos={NHL:'https://a.espncdn.com/i/teamlogos/leagues/500-dark/nhl.png',MLB:'https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500-dark/mlb.png&w=500&h=500&transparent=true',NFL:'https://a.espncdn.com/i/teamlogos/leagues/500-dark/nfl.png'};
function scoreLeagueMarkup(name,image,count){
 let logo=officialLeagueLogos[name]||'';try{const u=new URL(image);if(u.protocol==='https:'&&u.hostname==='a.espncdn.com'&&!u.username&&!u.password)logo=u.href;}catch{}
 const escape=value=>String(value??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 return `${logo?`<img class="league-logo" src="${escape(logo)}" alt="" aria-hidden="true" width="28" height="28" decoding="async" referrerpolicy="no-referrer">`:''}<span>${escape(name)}</span>${Number.isInteger(count)?`<span class="league-count" aria-hidden="true">${count}</span>`:''}`;
}
