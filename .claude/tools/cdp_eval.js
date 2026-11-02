// Evaluate JS in the running app's HA page over the Chrome DevTools Protocol.
// Start the app with --remote-debugging-address=127.0.0.1 --remote-debugging-port=9333
//   node .claude/tools/cdp_eval.js '<expression>' [port]
const path = require('path');
const WebSocket = require(path.join(__dirname, '..', '..', 'node_modules', 'ws'));

(async () => {
  const expression = process.argv[2] || 'location.href';
  const port = process.argv[3] || 9333;
  const targets = await (await fetch('http://127.0.0.1:' + port + '/json')).json();
  const page = targets.find(t => t.type === 'page' && !t.url.startsWith('about:')) || targets.find(t => t.type === 'page');
  if (!page) { console.error('no page target'); process.exit(1); }
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r => ws.on('open', r));
  ws.send(JSON.stringify({ id: 1, method: 'Runtime.evaluate', params: { expression, returnByValue: true, awaitPromise: true } }));
  ws.on('message', m => {
    const d = JSON.parse(m);
    if (d.id !== 1) return;
    const r = d.result || {};
    console.log(r.exceptionDetails ? 'EXCEPTION: ' + JSON.stringify(r.exceptionDetails.exception || r.exceptionDetails) : JSON.stringify(r.result && r.result.value));
    ws.close();
  });
})();
