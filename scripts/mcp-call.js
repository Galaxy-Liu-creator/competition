'use strict';
/* Minimal MCP stdio client to drive the stitch proxy from the command line.
   Usage: node mcp-call.js list
          node mcp-call.js call <toolName> '<jsonArgs>'   (args may also be a @file.json) */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const proxy = path.join(process.env.USERPROFILE, '.claude', 'mcp-servers', 'stitch-proxy.js');
const child = spawn('node', [proxy], { env: process.env, stdio: ['pipe', 'pipe', 'inherit'] });

let buf = '';
const pending = new Map();
let nextId = 1;

child.stdout.on('data', (d) => {
  buf += d.toString();
  let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (!line) continue;
    let msg; try { msg = JSON.parse(line); } catch { continue; }
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  }
});

function rpc(method, params) {
  const id = nextId++;
  return new Promise((res, rej) => {
    pending.set(id, res);
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); rej(new Error('timeout ' + method)); } }, 300000);
  });
}

(async () => {
  await rpc('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'cli', version: '1' } });
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');

  const [, , cmd, tool, argsRaw] = process.argv;
  if (cmd === 'list') {
    const r = await rpc('tools/list', {});
    for (const t of r.result.tools) {
      console.log('###', t.name);
      console.log((t.description || '').slice(0, 400));
      console.log('input:', JSON.stringify(t.inputSchema));
      console.log();
    }
  } else if (cmd === 'call') {
    let args = {};
    if (argsRaw) args = JSON.parse(argsRaw.startsWith('@') ? fs.readFileSync(argsRaw.slice(1), 'utf8') : argsRaw);
    const r = await rpc('tools/call', { name: tool, arguments: args });
    console.log(JSON.stringify(r.result ?? r.error, null, 2));
  }
  child.kill();
  process.exit(0);
})().catch(e => { console.error('ERR', e.message); child.kill(); process.exit(1); });
