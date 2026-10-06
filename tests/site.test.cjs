const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const handler = require('../api/site.js');
let server, upstream, base, cookie;
const password = 'Fixture password with spaces';
before(async () => {
  const salt = crypto.randomBytes(16);
  process.env.DASHBOARD_PASSWORD_HASH = salt.toString('hex') + ':' + crypto.pbkdf2Sync(password, salt, 210000, 32, 'sha256').toString('hex');
  process.env.DASHBOARD_SESSION_SECRET = crypto.randomBytes(32).toString('hex');
  process.env.DASHBOARD_ORIGIN_TOKEN = crypto.randomBytes(32).toString('hex');
  upstream = http.createServer(async (req, res) => {
    assert.equal(req.headers.authorization, 'Bearer ' + process.env.DASHBOARD_ORIGIN_TOKEN);
    res.setHeader('Content-Type', 'application/json');
    let body='';for await(const chunk of req)body+=chunk.toString();
    res.end(JSON.stringify({ path: req.url, status: 'ok', ...(req.method==='POST'?{method:req.method,body}:{}) }));
  });
  await new Promise(r => upstream.listen(0, '127.0.0.1', r));
  process.env.DASHBOARD_ORIGIN = 'http://127.0.0.1:' + upstream.address().port;
  server = http.createServer((req, res) => handler(req, res).catch(err => { res.statusCode = 500; res.end(String(err)); }));
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  base = 'http://127.0.0.1:' + server.address().port;
});
after(async () => { await Promise.all([new Promise(r => server.close(r)), new Promise(r => upstream.close(r))]); });
const request = (route, options = {}) => fetch(base + route, { redirect: 'manual', ...options });
const login = (password, next = '/') => request('/login', { method: 'POST', headers: { Origin: base, 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ password, next }).toString() });
test('pages, tools, scripts, and reports are protected before sign-in', async () => {
  for (const route of ['/', '/tools', '/invoice', '/leasecreate/js/app.js', '/index.html', '/app.js', '/cameras']) {
    const res = await request(route); assert.equal(res.status, 303); assert.match(res.headers.get('location'), /^\/login/);
    assert.match(res.headers.get('cache-control'), /no-store/);
  }
  for (const route of ['/api/jobs', '/api/cameras', '/camera-stream/1/index.m3u8', '/camera-stream/1/segment_123.ts', '/stock-document?report=private.pdf']) assert.equal((await request(route)).status, 401);
});
test('wrong passwords and cross-origin sign-ins fail', async () => {
  assert.equal((await login('incorrect')).status, 401);
  const res = await request('/login', { method: 'POST', headers: { Origin: 'https://other.example' }, body: 'password=x' });
  assert.equal(res.status, 403);
});
test('spaces in the password work and session cookie is secure', async () => {
  const res = await login(password, '/tools'); assert.equal(res.status, 303); assert.equal(res.headers.get('location'), '/tools');
  const set = res.headers.get('set-cookie');
  for (const flag of ['HttpOnly', 'Secure', 'SameSite=Lax', 'Path=/']) assert.ok(set.includes(flag));
  cookie = set.split(';')[0];
});
test('dashboard and every existing tool page serve after sign-in', async () => {
  for (const route of ['/', '/dashboard', '/briefing', '/stocks', '/woodbine', '/woodbine-stats', '/health', '/cameras', '/tools', '/invoice', '/mortgage', '/leasescan', '/leasecreate/', '/leasecreate/js/app.js']) {
    const res = await request(route, { headers: { Cookie: cookie } }); assert.equal(res.status, 200, route);
  }
  const html = await (await request('/', { headers: { Cookie: cookie } })).text();
  assert.ok(html.includes('href="/tools"'));
});
test('authenticated API forwards only fixed origin with server-side token and original query', async () => {
  const res = await request('/api/racing?date=2026-10-05', { headers: { Cookie: cookie } });
  assert.equal(res.status, 200); assert.deepEqual(await res.json(), { path: '/api/racing?date=2026-10-05', status: 'ok' });
  assert.equal((await request('/api/unknown', { headers: { Cookie: cookie } })).status, 404);
});
test('browser ES modules are served byte-for-byte without server transpilation', async () => {
  for (const route of ['/leasescan/js/ai.js', '/leasecreate/js/app.js', '/leasecreate/js/provinces/ontario.js']) {
    const res = await request(route, { headers: { Cookie: cookie } });
    assert.equal(res.status, 200);
    assert.equal(await res.text(), fs.readFileSync(path.join(__dirname, '..', 'web', route), 'utf8'));
  }
});
test('source, credentials, encoded traversal, and tampered sessions are inaccessible', async () => {
  for (const route of ['/api/site.js', '/.vercel/project.json', '/package.json', '/deploy/dashboard_bridge.py', '/apps/video-downloader/app.py', '/%2e%2e%2fpackage.json']) {
    assert.ok([400, 404].includes((await request(route, { headers: { Cookie: cookie } })).status), route);
  }
  assert.equal((await request('/', { headers: { Cookie: cookie + 'x' } })).status, 303);
});
test('open redirects are rejected and logout clears the cookie', async () => {
  assert.equal((await login(password, '//evil.example')).headers.get('location'), '/');
  assert.equal((await login(password, '/\\evil.example')).headers.get('location'), '/');
  const res = await request('/logout', { method: 'POST', headers: { Origin: base, Cookie: cookie } });
  assert.equal(res.status, 303); assert.match(res.headers.get('set-cookie'), /Max-Age=0/);
});
test('missing authentication configuration fails closed', async () => {
  const secret = process.env.DASHBOARD_SESSION_SECRET; delete process.env.DASHBOARD_SESSION_SECRET;
  assert.equal((await request('/', { headers: { Cookie: cookie } })).status, 503);
  process.env.DASHBOARD_SESSION_SECRET = secret;
});

test('acknowledgement writes require session and same origin and forward only to the fixed origin',async()=>{const route='/api/acknowledgements',body=new URLSearchParams({key:'fixture-job|2026-10-04|error'}).toString();assert.equal((await request(route,{method:'POST',body,headers:{Origin:base}})).status,401);const fresh=await login(password);const auth=fresh.headers.get('set-cookie').split(';')[0];assert.equal((await request(route,{method:'POST',body,headers:{Cookie:auth,Origin:'https://other.example'}})).status,403);assert.equal((await request(route,{method:'POST',body:'key=',headers:{Cookie:auth,Origin:base}})).status,400);const res=await request(route,{method:'POST',body,headers:{Cookie:auth,Origin:base,'Content-Type':'application/x-www-form-urlencoded'}});assert.equal(res.status,200);const d=await res.json();assert.equal(d.method,'POST');assert.equal(d.path,route);assert.equal(d.body,body);assert.equal((await request('/api/jobs',{method:'POST',headers:{Cookie:auth,Origin:base}})).status,405);});

test('camera reads use the authenticated fixed bridge and reject arbitrary stream paths',async()=>{
 const fresh=await login(password),auth=fresh.headers.get('set-cookie').split(';')[0];
 for(const route of ['/api/cameras?channels=1,2,3,4,5,6','/camera-stream/1/index.m3u8','/camera-stream/6/segment_123.ts']){
  const res=await request(route,{headers:{Cookie:auth}});assert.equal(res.status,200);assert.equal((await res.json()).path,route);assert.match(res.headers.get('cache-control'),/no-store/);
 }
 for(const route of ['/camera-stream/7/index.m3u8','/camera-stream/1/private.json','/camera-stream/1/config.env','/cameras.json'])assert.equal((await request(route,{headers:{Cookie:auth}})).status,404);
 assert.equal((await request('/api/cameras',{method:'POST',headers:{Cookie:auth}})).status,405);
});
