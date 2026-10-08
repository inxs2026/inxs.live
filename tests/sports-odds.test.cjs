const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
test('odds show their source and time, and stale score responses hide prices',()=>{
 const source=fs.readFileSync('web/sports.js','utf8'),a=source.indexOf('function sportsOdds('),b=source.indexOf('async function loadSportsScores');
 const target={innerHTML:''};const ctx={esc:String,Intl,Date,encodeURIComponent,formatted:String,standingLeague:'NHL',torontoDate:()=> '2026-10-08',$:()=>target,applyScoreTeamColors(){},scoreLeagueMarkup:()=>'',scoreTeamMarkup:()=>''};vm.createContext(ctx);vm.runInContext(source.slice(a,b),ctx);
 const game={id:'1',state:'pre',league:'NHL',date:'2026-10-08T23:00Z',teams:[{name:'TOR'},{name:'VGK'}],odds:{url:'https://www.scoresandodds.com/nhl',updatedAt:'2026-10-08T12:00Z',markets:{away:{moneyline:'+140'},home:{moneyline:'-165'}}}};
 assert.match(ctx.sportsOdds(game),/ScoresAndOdds/);assert.match(ctx.sportsOdds(game),/Checked/);assert.match(ctx.sportsOdds(game),/\+140/);
 assert.equal(ctx.sportsOdds({...game,state:'post'}),'');
 ctx.renderSportsScores({leagues:[{league:'NHL',events:[game]}]},'2026-10-08',true);assert.doesNotMatch(target.innerHTML,/\+140|-165/);assert.match(target.innerHTML,/temporarily unavailable/);
});
