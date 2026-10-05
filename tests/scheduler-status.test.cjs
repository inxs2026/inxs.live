const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../web/app.js'),'utf8');
const ctx={};vm.createContext(ctx);vm.runInContext(source.split('\n').find(line=>line.startsWith('function isFailed(')),ctx);
test('normal scheduler states do not raise failure alerts',()=>{for(const result of ['ok','success','skipped','running','pending','unknown','never','none','',null])assert.equal(ctx.isFailed({result}),false,result);});
test('confirmed scheduler and systemd failures remain visible',()=>{for(const result of ['error','failed','timeout','exit-code','signal','oom-kill','start-limit-hit','resources'])assert.equal(ctx.isFailed({result}),true,result);});
