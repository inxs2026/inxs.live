const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const ctx={document:{getElementById:()=>null,addEventListener:()=>{}},window:{addEventListener:()=>{}},setInterval:()=>{},esc:s=>String(s).replaceAll('<','&lt;'),formatted:s=>s};vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'../web/codex-usage.js'),'utf8'),ctx);
test('usage meter labels match durations and unknown readings show no invented zero',()=>{assert.equal(ctx.codexWindowLabel({windowDurationMins:300}),'5-hour limit');assert.equal(ctx.codexWindowLabel({windowDurationMins:10080}),'Weekly limit');const html=ctx.codexMeter({name:'Codex',slot:'primary',remainingPercent:null},false);assert.match(html,/unavailable/);assert.doesNotMatch(html,/<meter/);});
test('usage meter shows remaining allowance and identifies cached readings',()=>{const html=ctx.codexMeter({name:'Codex',windowDurationMins:300,remainingPercent:75,usedPercent:25,resetsAt:1791230000},true);assert.match(html,/75%/);assert.match(html,/value="75"/);assert.match(html,/Last confirmed reading/);assert.match(html,/Resets/);});

test('resuming and reconnecting refresh usage without overlapping requests',async()=>{
 const listeners={},elements={'codex-usage':{innerHTML:'',querySelector:()=>null},'refresh-codex':{disabled:false,addEventListener:()=>{}},'codex-checked':{textContent:''}};
 let calls=0,resolve;
 const c={document:{hidden:false,getElementById:id=>elements[id],addEventListener:(name,fn)=>listeners[name]=fn},window:{addEventListener:(name,fn)=>listeners[name]=fn},setInterval:()=>{},getJSON:()=>{calls++;return new Promise(r=>resolve=r);},esc:String,formatted:String};
 vm.createContext(c);vm.runInContext(fs.readFileSync(path.join(__dirname,'../web/codex-usage.js'),'utf8'),c);
 assert.equal(calls,1);listeners.pageshow();listeners.online();assert.equal(calls,1);
 resolve({windows:[],note:'Ready'});await new Promise(setImmediate);
 c.document.hidden=true;listeners.visibilitychange();assert.equal(calls,1);
 c.document.hidden=false;listeners.visibilitychange();assert.equal(calls,2);
 resolve({windows:[],note:'Ready'});await new Promise(setImmediate);
 listeners.online();assert.equal(calls,3);resolve({windows:[],note:'Ready'});await new Promise(setImmediate);
 listeners.pageshow();assert.equal(calls,4);resolve({windows:[],note:'Ready'});await new Promise(setImmediate);assert.equal(elements['refresh-codex'].disabled,false);
});
