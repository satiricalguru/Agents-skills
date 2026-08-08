const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
  console.log(`[Request] ${req.method} ${req.url}`);

  // Normalize path and set index.html as default
  let filePath = req.url === '/' ? '/index.html' : req.url;
  
  // Strip query string / hash and reject any traversal attempt
  filePath = decodeURIComponent(filePath.split('?')[0].split('#')[0]);
  filePath = path.normalize(path.join(__dirname, filePath));

  // Directory traversal guard: resolved file must stay inside docs root
  if (filePath !== __dirname && !filePath.startsWith(__dirname + path.sep)) {
    console.log(`[403] Forbidden: ${req.url}`);
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('403 Forbidden');
    return;
  }

  // Check if file exists
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    const ext = path.extname(filePath);
    const contentType = MIME_TYPES[ext] || 'text/plain';

    res.writeHead(200, { 'Content-Type': contentType });
    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
  } else {
    console.log(`[404] Not Found: ${req.url}`);
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 Not Found');
  }
});

server.listen(PORT, () => {
  console.log(`\n==================================================`);
  console.log(`🚀 AI Agent Skills Hub server running locally at:`);
  console.log(`   👉 http://localhost:${PORT}`);
  console.log(`==================================================\n`);
});
