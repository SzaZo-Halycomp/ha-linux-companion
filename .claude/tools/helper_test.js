// Run top-level helper functions from src/main.js outside Electron.
//   node .claude/tools/helper_test.js <fn,fn,...> '<js using them>'
// e.g. runShell,findBacklight,writeSysfs,setDisplayPower,getDisplayState
// Globals the helpers expect (fs, path, os, execSync, log, audioBackend) are provided.
const fs = require('fs'), path = require('path'), os = require('os');
const { execSync } = require('child_process');
const log = m => console.log('  log:', m);
let audioBackend = 'unknown';

const src = fs.readFileSync(path.join(__dirname, '..', '..', 'src', 'main.js'), 'utf8');
const grab = n => {
  const m = src.match(new RegExp('(async )?function ' + n + '\\([\\s\\S]*?\\n}\\n'));
  if (!m) throw new Error('function not found: ' + n);
  return m[0];
};
const names = (process.argv[2] || '').split(',').filter(Boolean);
eval(names.map(grab).join('\n') + '\n' + (process.argv[3] || ''));
