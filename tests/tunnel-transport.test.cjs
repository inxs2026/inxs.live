const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
test('media tunnel explicitly uses TCP HTTP/2 rather than unstable QUIC', () => {
  const compose = fs.readFileSync('deploy/docker-compose.yml', 'utf8');
  assert.match(compose, /cloudflare\/cloudflared:2026\.10\.5@sha256:[a-f0-9]{64}/);
  assert.match(compose, /tunnel --protocol http2 --no-autoupdate run/);
});
