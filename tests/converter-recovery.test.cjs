const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
function fixture(fetch){
 const html=fs.readFileSync('apps/video-converter/templates/index.html','utf8');
 const start=html.indexOf('    const requestWithRecovery ='),end=html.indexOf('    const updateUploadProgress =',start);
 const context={fetch,AbortController,batchCancelled:false,activeChunkController:null,readApiResponse:async r=>r.data,setTimeout:(fn,ms)=>{if(ms<=10000)queueMicrotask(fn);return 1;},clearTimeout(){}};
 vm.createContext(context);vm.runInContext(html.slice(start,end)+'\nthis.recover=requestWithRecovery;',context);return context;
}
test('a network interruption retries the same chunk body and recovers',async()=>{
 let calls=0,retries=0;const body={chunk:12};const c=fixture(async(url,options)=>{assert.equal(url,'/api/upload-chunk');assert.equal(options.body,body);if(calls++===0)throw new TypeError('Failed to fetch');return {ok:true,data:{ok:true}};});
 const result=await c.recover('/api/upload-chunk',{method:'POST',body},()=>retries++);assert.equal(result.data.ok,true);assert.equal(calls,2);assert.equal(retries,0);assert.equal(c.activeChunkController,null);
});
test('temporary tunnel errors recover but permanent errors are not replayed',async()=>{
 let calls=0;let c=fixture(async()=>calls++===0?{ok:false,status:502,data:{}}:{ok:true,data:{status:'done'}});assert.equal((await c.recover('/api/progress/x')).data.status,'done');
 calls=0;c=fixture(async()=>{calls++;return {ok:false,status:404,data:{error:'Job not found'}};});await assert.rejects(c.recover('/api/progress/x'),/Job not found/);assert.equal(calls,1);
});
test('retries are bounded and cancellation prevents another chunk write',async()=>{
 let calls=0;const c=fixture(async()=>{calls++;throw new TypeError('Failed to fetch');});await assert.rejects(c.recover('/api/upload-chunk',{method:'POST'}),/Could not reconnect/);assert.equal(calls,12);
 c.batchCancelled=true;await assert.rejects(c.recover('/api/upload-chunk',{method:'POST'}),/Upload cancelled/);assert.equal(calls,12);
 calls=0;await assert.rejects(fixture(async()=>{calls++;throw new TypeError('Failed to fetch');}).recover('/api/progress/x'),/Could not reconnect/);assert.equal(calls,6);
});
test('isolated antivirus resets are retried silently; only sustained failure shows reconnecting',async()=>{
 let calls=0,retries=0;let c=fixture(async()=>{if(calls++<2)throw new TypeError('Failed to fetch');return {ok:true,data:{ok:true}};});
 await c.recover('/api/upload-chunk',{method:'POST',body:{}},()=>retries++);assert.equal(calls,3);assert.equal(retries,0);
 calls=0;retries=0;c=fixture(async()=>{if(calls++<4)throw new TypeError('Failed to fetch');return {ok:true,data:{ok:true}};});
 await c.recover('/api/upload-chunk',{method:'POST',body:{}},()=>retries++);assert.equal(calls,5);assert.equal(retries,2);
});
