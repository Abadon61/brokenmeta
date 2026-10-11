// node run_logs_real.mjs <log file>  : parses a real combat log and prints a summary WITHOUT player names (sanity check of the BrokenLogs parser).
import { createReadStream } from 'node:fs';
import { createInterface } from 'node:readline';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { Parser } = require('../js/wow-logs-core.js');

const file = process.argv[2];
const p = new Parser();
const t0 = Date.now();
const rl = createInterface({ input: createReadStream(file, { encoding: 'utf8' }), crlfDelay: Infinity });
for await (const line of rl) p.line(line);
const r = p.finish();
const dt = (Date.now() - t0) / 1000;
console.log(`lines ${r.meta.lines} in ${dt.toFixed(1)}s (${Math.round(r.meta.lines / dt)} lines/s), version ${r.meta.version}, build ${r.meta.build}`);
console.log('fights', r.fights.length, 'bosses', r.fights.filter((f) => f.kind === 'boss').length);
for (const f of r.fights.slice(0, 14)) {
  const top = f.players[0];
  const sumP = f.players.reduce((s, x) => s + x.dmg, 0);
  console.log(`#${f.id} ${f.kind.padEnd(6)} ${String(f.name).slice(0, 22).padEnd(22)} ${f.success === null ? '-' : f.success ? 'kill' : 'wipe'} ${String(f.dur).padStart(6)}s players ${String(f.players.length).padStart(2)} raidDPS ${Math.round(sumP / f.dur)} topDPS ${top ? top.dps : 0} (${top ? top.spec || '?' : ''} ilvl ${top ? top.ilvl : 0}) deaths ${f.deaths} pets ${f.players.filter((x) => x.pets.length).length}`);
}
const b = r.fights.find((f) => f.kind === 'boss') || r.fights[0];
if (b) {
  const x = b.players[0];
  console.log('top player spells:', x.spells.slice(0, 4).map((s) => `${s.n} ${Math.round(s.d / x.dmg * 100)}%`).join(' | '));
  console.log('timeline buckets', x.tl.length, 'sum check', x.tl.reduce((s, v) => s + v * 5, 0), 'vs dmg', x.dmg);
}
