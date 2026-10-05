const {test}=require('node:test'),assert=require('node:assert/strict'),{EventEmitter}=require('node:events'),{originRead}=require('../lib/origin-read.cjs');
test('failed relay read tries alternate DNS address without weakening hostname verification',async()=>{
 const attempted=[];const deps={fetch:async()=>{throw new Error('TLS failed')},lookup:async()=>[{address:'192.0.2.1',family:4},{address:'192.0.2.2',family:4}],request:(url,options,onResponse)=>{
  assert.equal(options.servername,'origin.example');assert.equal(url.hostname,'origin.example');assert.equal(options.rejectUnauthorized,undefined);assert.equal(options.headers.Authorization,'Bearer private');
  const req=new EventEmitter();req.end=()=>options.lookup(url.hostname,{},(_,ip)=>{attempted.push(ip);queueMicrotask(()=>{if(ip==='192.0.2.1')req.emit('error',new Error('TLS failed'));else{const res=new EventEmitter();res.statusCode=200;res.headers={'content-type':'application/json'};onResponse(res);res.emit('data',Buffer.from('{"state":"current"}'));res.emit('end');}})});return req;
 }};
 const out=await originRead(new URL('https://origin.example/api/codex-usage'),{method:'GET',headers:{Authorization:'Bearer private'}},deps);assert.equal(out.status,200);assert.deepEqual(attempted,['192.0.2.1','192.0.2.2']);assert.equal(JSON.parse(out.body).state,'current');
});
test('writes are never replayed after uncertain connection errors',async()=>{let looked=false;await assert.rejects(originRead(new URL('https://origin.example/api/acknowledgements'),{method:'POST'},{fetch:async()=>{throw new Error('failed')},lookup:async()=>{looked=true}}));assert.equal(looked,false);});
