const crypto = require('node:crypto');
const fs = require('node:fs/promises');
const path = require('node:path');
const zlib = require('node:zlib');
const { promisify } = require('node:util');

const pbkdf2 = promisify(crypto.pbkdf2);
const WEB = path.join(__dirname, '..', 'web');
let assets;
async function webAssets() {
  if (!assets) assets = fs.readFile(path.join(__dirname, 'web-assets.json.gz'))
    .then(raw => JSON.parse(zlib.gunzipSync(raw).toString('utf8')));
  return assets;
}
const COOKIE = '__Host-inxs_session';
const HOURS = 12 * 60 * 60;
const DATA_PATHS = new Set([
  '/api/acknowledgements', '/api/jobs', '/api/codex-usage', '/api/system-health', '/api/timeline', '/api/racing-performance',
  '/api/racing', '/api/woodbine-stats', '/api/stocks', '/api/stock-quotes',
  '/api/briefing', '/api/health', '/agco-document', '/racing-document',
  '/stats-document', '/stock-document',
]);
const PAGES = { '/': 'index.html', '/briefing': 'index.html', '/dashboard': 'dashboard.html', '/stocks': 'stocks.html',
  '/woodbine': 'woodbine.html', '/woodbine-stats': 'woodbine-stats.html', '/health': 'health.html' };
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.ico': 'image/x-icon', '.json': 'application/json; charset=utf-8', '.woff2': 'font/woff2' };
const attempts = new Map();

function send(res, status, body, type = 'text/html; charset=utf-8') {
  res.statusCode = status;
  res.setHeader('Content-Type', type);
  res.end(body);
}
function redirect(res, target) {
  res.statusCode = 303;
  res.setHeader('Location', target);
  res.end();
}
function safeNext(value) {
  return typeof value === 'string' && value.startsWith('/') && !value.startsWith('//')
    && !/[\\\r\n]/.test(value) && !value.startsWith('/login') && !value.startsWith('/logout') ? value : '/';
}
function escape(value) {
  return value.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
}
function loginPage(next, error = '') {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Sign in · INXS</title><style>
  *{box-sizing:border-box}body{margin:0;min-height:100dvh;display:grid;place-items:center;padding:24px;background:radial-gradient(ellipse at top,#2d2042,#101017 65%);color:#eee9f7;font:16px system-ui,sans-serif}.card{width:min(100%,420px);padding:36px;border:1px solid #463750;border-radius:22px;background:#19151fe8;box-shadow:0 24px 90px #0005}.brand{font-size:12px;letter-spacing:3px;color:#bfa2ed}h1{font-size:30px;margin:20px 0 10px}p{color:#b5a8c6;line-height:1.6}label{display:block;margin:28px 0 9px}input,button{width:100%;font:inherit;border-radius:10px;padding:14px}input{background:#101017;border:1px solid #645174;color:#fff}input:focus{outline:2px solid #b99cec;outline-offset:2px}button{margin-top:18px;border:0;background:#b99cec;color:#19101f;font-weight:700;cursor:pointer}.error{color:#ffb4be;font-size:14px}.note{font-size:12px;margin-bottom:0}
  </style></head><body><main class="card"><div class="brand">INXS.LIVE</div><h1>Your workspace.</h1><p>Sign in to open your dashboard and tools.</p><form method="post" action="/login"><input type="hidden" name="next" value="${escape(safeNext(next))}"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required autofocus maxlength="256">${error ? `<p class="error" role="alert">${error}</p>` : ''}<button type="submit">Open dashboard →</button></form><p class="note">Your session lasts 12 hours. Sign out when you’re finished.</p></main></body></html>`;
}
function validSession(req, secret) {
  const cookie = (req.headers.cookie || '').split(';').map(x => x.trim()).find(x => x.startsWith(COOKIE + '='));
  if (!cookie) return false;
  const token = cookie.slice(COOKIE.length + 1);
  const [expires, nonce, signature, extra] = token.split('.');
  if (extra || !/^\d{10}$/.test(expires || '') || !/^[a-f0-9]{32}$/.test(nonce || '') || !/^[a-f0-9]{64}$/.test(signature || '')) return false;
  const now = Math.floor(Date.now() / 1000);
  if (+expires <= now || +expires > now + HOURS) return false;
  const expected = crypto.createHmac('sha256', secret).update(expires + '.' + nonce).digest();
  return crypto.timingSafeEqual(Buffer.from(signature, 'hex'), expected);
}
function session(secret) {
  const payload = `${Math.floor(Date.now() / 1000) + HOURS}.${crypto.randomBytes(16).toString('hex')}`;
  return payload + '.' + crypto.createHmac('sha256', secret).update(payload).digest('hex');
}
function sameOrigin(req) {
  try { return new URL(req.headers.origin).host === req.headers.host; } catch { return false; }
}
async function form(req, limit = 4096) {
  if (req.body && typeof req.body === 'object' && !Buffer.isBuffer(req.body)) return req.body;
  if (typeof req.body === 'string') return Object.fromEntries(new URLSearchParams(req.body));
  let body = '';
  for await (const chunk of req) {
    body += chunk.toString();
    if (body.length > limit) throw new Error('Body too large');
  }
  return Object.fromEntries(new URLSearchParams(body));
}
async function handler(req, res) {
  res.setHeader('Cache-Control', 'private, no-store, max-age=0');
  res.setHeader('Vercel-CDN-Cache-Control', 'no-store');
  res.setHeader('CDN-Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'same-origin');
  res.setHeader('Content-Security-Policy', "frame-ancestors 'none'; object-src 'none'; base-uri 'self'");
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  res.setHeader('Strict-Transport-Security', 'max-age=63072000; includeSubDomains');
  const secret = process.env.DASHBOARD_SESSION_SECRET;
  const hash = process.env.DASHBOARD_PASSWORD_HASH;
  if (!secret || secret.length < 32 || !/^[a-f0-9]{32}:[a-f0-9]{64}$/.test(hash || '')) {
    return send(res, 503, 'Workspace authentication is not configured.');
  }
  let url, pathname;
  try {
    url = new URL(req.url, 'https://' + req.headers.host);
    pathname = decodeURIComponent(url.pathname);
    if (pathname.includes('\\') || pathname.includes('\0') || pathname.split('/').some(x => x === '..' || x === '.')) throw new Error();
  } catch { return send(res, 400, 'Invalid request.'); }
  if (pathname === '/login') {
    if (req.method === 'GET') return send(res, 200, loginPage(url.searchParams.get('next') || '/'));
    if (req.method !== 'POST') return send(res, 405, 'Method not allowed.');
    if (!sameOrigin(req)) return send(res, 403, 'Please sign in from this website.');
    const ip = String(req.headers['x-vercel-forwarded-for'] || req.socket?.remoteAddress || 'unknown').split(',')[0];
    const now = Date.now();
    for (const [key, item] of attempts) if (item.until < now) attempts.delete(key);
    const item = attempts.get(ip) || { count: 0, until: now + 15 * 60 * 1000 };
    if (item.count >= 5 || attempts.size > 10000) {
      res.setHeader('Retry-After', '900');
      return send(res, 429, loginPage('/', 'Too many attempts. Please try again in 15 minutes.'));
    }
    let data;
    try { data = await form(req); } catch { return send(res, 400, loginPage('/', 'Please try again.')); }
    const password = typeof data.password === 'string' ? data.password : '';
    const [salt, expected] = hash.split(':');
    const actual = await pbkdf2(password.slice(0, 256), Buffer.from(salt, 'hex'), 210000, 32, 'sha256');
    if (password.length > 256 || !crypto.timingSafeEqual(actual, Buffer.from(expected, 'hex'))) {
      item.count++; attempts.set(ip, item);
      return send(res, 401, loginPage(data.next || '/', 'That password didn’t match. Please try again.'));
    }
    attempts.delete(ip);
    res.setHeader('Set-Cookie', `${COOKIE}=${session(secret)}; Path=/; Max-Age=${HOURS}; HttpOnly; Secure; SameSite=Lax`);
    return redirect(res, safeNext(data.next));
  }
  if (pathname === '/logout') {
    if (req.method !== 'POST') return send(res, 405, 'Method not allowed.');
    if (!sameOrigin(req)) return send(res, 403, 'Invalid request.');
    res.setHeader('Set-Cookie', `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`);
    return redirect(res, '/login');
  }
  if (!validSession(req, secret)) {
    if (pathname.startsWith('/api/') || DATA_PATHS.has(pathname)) return send(res, 401, JSON.stringify({ error: 'Please sign in.' }), 'application/json');
    return redirect(res, '/login?next=' + encodeURIComponent(safeNext(url.pathname + url.search)));
  }
  let acknowledgementBody;
  if (pathname === '/api/acknowledgements' && req.method === 'POST') {
    if (!sameOrigin(req)) return send(res, 403, 'Invalid request origin.');
    try { const input = await form(req, 65536); if (typeof input.notices === 'string') { if (input.notices.length > 60000 || !Array.isArray(JSON.parse(input.notices))) throw new Error('Invalid notices'); acknowledgementBody = new URLSearchParams({ notices: input.notices, complete: input.complete === 'true' ? 'true' : 'false' }).toString(); } else { if (typeof input.key !== 'string' || !input.key || input.key.length > 2048) throw new Error('Invalid key'); acknowledgementBody = new URLSearchParams({ key: input.key }).toString(); } }
    catch { return send(res, 400, 'Invalid acknowledgement.'); }
  }
  if (!['GET', 'HEAD'].includes(req.method) && acknowledgementBody === undefined) return send(res, 405, 'Method not allowed.');
  if (DATA_PATHS.has(pathname)) {
    const origin = process.env.DASHBOARD_ORIGIN;
    const token = process.env.DASHBOARD_ORIGIN_TOKEN;
    if (!origin || !token) return send(res, 503, JSON.stringify({ error: 'The Linux data connection is not configured.' }), 'application/json');
    try {
      const upstream = await fetch(new URL(pathname + url.search, origin), {
        method: req.method === 'HEAD' ? 'GET' : req.method, body: acknowledgementBody,
        headers: { Authorization: 'Bearer ' + token, ...(acknowledgementBody !== undefined ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}) }, redirect: 'error', signal: AbortSignal.timeout(25000),
      });
      const body = Buffer.from(await upstream.arrayBuffer());
      res.statusCode = upstream.status;
      res.setHeader('Content-Type', upstream.headers.get('content-type') || 'application/octet-stream');
      if (req.method === 'HEAD') return res.end();
      return res.end(body);
    } catch (error) {
      console.error('Dashboard origin request failed:', error.name, error.cause?.code || error.code || 'unknown');
      return send(res, 502, JSON.stringify({ error: 'The Linux dashboard is temporarily unavailable.' }), 'application/json');
    }
  }
  let name = PAGES[pathname.replace(/\/$/, '') || '/'] || pathname.replace(/^\//, '');
  if (['tools', 'invoice', 'mortgage', 'leasescan', 'leasecreate'].includes(name.replace(/\/$/, ''))) name = name.replace(/\/$/, '') + '/index.html';
  const file = path.resolve(WEB, name);
  if (!file.startsWith(WEB + path.sep) || !TYPES[path.extname(file)] || name.split('/').some(x => x.startsWith('.'))) return send(res, 404, 'Page not found.');
  try {
    const entry = (await webAssets())[name];
    if (!entry) return send(res, 404, 'Page not found.');
    const body = Buffer.from(entry, 'base64');
    res.setHeader('Content-Type', TYPES[path.extname(file)]);
    res.statusCode = 200;
    if (req.method === 'HEAD') return res.end();
    res.end(body);
  } catch { return send(res, 404, 'Page not found.'); }
}
module.exports = handler;
