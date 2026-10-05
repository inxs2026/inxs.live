// Keep browser modules byte-for-byte intact: the Node builder otherwise transpiles included .js files.
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const root = path.join(__dirname, '..', 'web');
const files = {};
const allowed = new Set(['.html', '.js', '.css', '.svg', '.png', '.ico', '.json', '.woff2']);
function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.') || entry.isSymbolicLink()) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.isFile() && allowed.has(path.extname(full))) {
      files[path.relative(root, full).split(path.sep).join('/')] = fs.readFileSync(full).toString('base64');
    }
  }
}
walk(root);
fs.writeFileSync(path.join(__dirname, '..', 'api', 'web-assets.json.gz'), zlib.gzipSync(JSON.stringify(files), { level: 9 }));
console.log(`Packaged ${Object.keys(files).length} original browser assets.`);
