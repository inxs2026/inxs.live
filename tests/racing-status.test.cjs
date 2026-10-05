const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const ctx={Intl,Date};vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'../web/attention.js'),'utf8').replace('loadAttention();setInterval(loadAttention,60000);',''),ctx);
const fixture=scheduled=>({schedule:{scheduled,nextRaceDate:'2026-10-08'},races:[],errors:[],scratches:{error:'No feed',snapshot:true}});
test('offday has a clear normal status and no missing-picks or scratch alert',()=>{assert.equal(ctx.racingNotices(fixture(false)).length,0);assert.match(ctx.racingStatusText(fixture(false)),/No racing scheduled today.*2026-10-08/);});
test('scheduled racing without picks preserves missing output and feed alerts',()=>{const n=ctx.racingNotices(fixture(true));assert.equal(n.length,2);assert.match(n[0],/Racing is scheduled today; no saved picks/);});
test('unknown schedules and corrupt sources still raise alerts',()=>{assert.equal(ctx.racingNotices(fixture(null)).length,1);const f=fixture(false);f.errors=['Corrupt source'];assert.equal(ctx.racingNotices(f).length,1);});
test('existing race cards cannot be hidden by offday metadata',()=>{const f=fixture(false);f.races=[{number:1}];assert.equal(ctx.racingNotices(f).length,1);assert.equal(ctx.racingStatusText(f),'');});
