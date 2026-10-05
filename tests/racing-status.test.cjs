const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const ctx={Intl,Date};vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'../web/attention.js'),'utf8').replace('loadAttention();setInterval(loadAttention,60000);',''),ctx);
const fixture=scheduled=>({schedule:{scheduled,nextRaceDate:'2026-10-08'},races:[],errors:[],scratches:{error:'No feed',snapshot:true}});
test('offday has a clear normal status and no missing-picks or scratch alert',()=>{assert.equal(ctx.racingNotices(fixture(false)).length,0);assert.match(ctx.racingStatusText(fixture(false)),/No racing scheduled today.*2026-10-08/);});
test('scheduled racing without picks preserves missing output and feed alerts',()=>{const n=ctx.racingNotices(fixture(true));assert.equal(n.length,2);assert.match(n[0],/Racing is scheduled today; no saved picks/);});
test('unknown schedules and corrupt sources still raise alerts',()=>{assert.equal(ctx.racingNotices(fixture(null)).length,1);const f=fixture(false);f.errors=['Corrupt source'];assert.equal(ctx.racingNotices(f).length,1);});
test('existing race cards cannot be hidden by offday metadata',()=>{const f=fixture(false);f.races=[{number:1}];assert.equal(ctx.racingNotices(f).length,1);assert.equal(ctx.racingStatusText(f),'');});

test('startup failure states the affected report and required technical check',()=>{const j={unit:'81265f85-6e79-4379-a5d3-119ebbe43c7e',failureReason:'The model runtime changed before the job could start.'};assert.match(ctx.jobFailureImpact(j),/no Top 3 Beyer picks PDF/);assert.match(ctx.jobFailureAction(j),/Verify this job can start/);assert.match(ctx.jobFailureAction(j),/not yet verified/);});
test('different causes have different actions',()=>{assert.match(ctx.jobFailureAction({failureReason:'The service could not authenticate.'}),/credentials/);assert.match(ctx.jobFailureAction({failureReason:null}),/run log/);});
