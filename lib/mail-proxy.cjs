const crypto = require('node:crypto');
const { originRead } = require('./origin-read.cjs');
const READS = new Set(['status', 'unread', 'messages', 'message', 'attachment']);
const WRITES = new Set(['connect', 'callback', 'modify', 'send', 'disconnect', 'empty-trash']);
async function mailProxy(req, res, url) {
  const pathname = url.pathname;
  if (!pathname.startsWith('/api/mail/')) return false;
  const finish = (status, body) => {
    res.statusCode = status;
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(body));
    return true;
  };
  const action = pathname.slice('/api/mail/'.length);
  if (!READS.has(action) && !WRITES.has(action)) return finish(404, {error: 'Mail endpoint not found.'});
  if (!(req.method === 'GET' && READS.has(action)) && !(req.method === 'POST' && WRITES.has(action)))
    return finish(405, {error: 'Method not allowed.'});
  let body;
  if (req.method === 'POST') {
    try {
      const origin = new URL(req.headers.origin);
      if (origin.host !== req.headers.host || origin.protocol !== 'https:' && origin.hostname !== '127.0.0.1')
        return finish(403, {error: 'Invalid request origin.'});
    } catch { return finish(403, {error: 'Invalid request origin.'}); }
    if (!(req.headers['content-type'] || '').toLowerCase().startsWith('application/json'))
      return finish(415, {error: 'JSON required.'});
    try {
      let raw = '';
      if (req.body !== undefined) raw = typeof req.body === 'string' ? req.body : Buffer.isBuffer(req.body) ? req.body.toString() : JSON.stringify(req.body);
      else for await (const chunk of req) { raw += chunk.toString(); if (Buffer.byteLength(raw) > 3100000) throw new Error(); }
      if (Buffer.byteLength(raw) > 3100000) throw new Error();
      const data = JSON.parse(raw);
      if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error();
      body = JSON.stringify(data);
    } catch { return finish(400, {error: 'Invalid or oversized email request.'}); }
  }
  const origin = process.env.DASHBOARD_ORIGIN, token = process.env.DASHBOARD_ORIGIN_TOKEN;
  if (!origin || !token) return finish(503, {error: 'The Linux email connection is not configured.'});
  const session = (req.headers.cookie || '').split(';').map(x => x.trim()).find(x => x.startsWith('__Host-inxs_session='));
  const binding = crypto.createHmac('sha256', process.env.DASHBOARD_SESSION_SECRET).update('mail-session:' + session).digest('hex');
  try {
    const upstream = await originRead(new URL(pathname + url.search, origin), {
      method: req.method, body,
      headers: {Authorization: 'Bearer ' + token, 'X-Mail-Session': binding,
        ...(body ? {'Content-Type': 'application/json'} : {})},
      redirect: 'error', signal: AbortSignal.timeout(25000),
    });
    res.statusCode = upstream.status;
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(upstream.body);
    return true;
  } catch { return finish(502, {error: req.method === 'POST' && action === 'send'
    ? 'The send result could not be confirmed. Check Sent before trying again.'
    : 'The Linux email connection is temporarily unavailable.'}); }
}
module.exports = { mailProxy };
