const https = require('node:https');
const dns = require('node:dns/promises');
// Retry read-only requests across DNS addresses while retaining hostname TLS validation.
async function originRead(url, options, deps = {}) {
  const fetcher = deps.fetch || fetch;
  try {
    const response = await fetcher(url, options);
    return { status: response.status, type: response.headers.get('content-type'), body: Buffer.from(await response.arrayBuffer()) };
  } catch (firstError) {
    if (options.method !== 'GET' || url.protocol !== 'https:') throw firstError;
    const addresses = await (deps.lookup || dns.lookup)(url.hostname, { all: true });
    for (const address of addresses.slice(0, 4)) {
      try {
        return await new Promise((resolve, reject) => {
          const req = (deps.request || https.request)(url, {
            method: 'GET', headers: options.headers, servername: url.hostname,
            lookup: (_host, opts, callback) => opts.all
              ? callback(null, [address]) : callback(null, address.address, address.family),
            signal: AbortSignal.timeout(6000),
          }, response => {
            const parts = [];
            response.on('data', part => parts.push(part));
            response.on('error', reject);
            response.on('end', () => {
              if (response.statusCode >= 300 && response.statusCode < 400) return reject(new Error('Origin redirect refused'));
              resolve({status: response.statusCode, type: response.headers['content-type'], body: Buffer.concat(parts)});
            });
          });
          req.on('error', reject); req.end();
        });
      } catch { /* Try the next DNS address, using the same verified hostname. */ }
    }
    throw firstError;
  }
}
module.exports = { originRead };
