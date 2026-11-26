// Character sheet of each preset (final stats, after gear, talents, buffs and consumables) from the WoWSims Forever engine
// (github.com/wowsims/forever, MIT): its WebAssembly build's computeStatsJson, run in Node.
// usage: node stats.mjs <wasm_exec.js> <lib.wasm> <in.json: {label: RaidSimRequest}> <out.json>
import fs from 'node:fs';
import { createRequire } from 'node:module';
const [, , execJs, wasmPath, inFile, outFile] = process.argv;
createRequire(import.meta.url)(execJs);
const go = new globalThis.Go();
const { instance } = await WebAssembly.instantiate(fs.readFileSync(wasmPath), go.importObject);
globalThis.wasmready = () => {};
go.run(instance);
await new Promise(r => setTimeout(r, 200));
const reqs = JSON.parse(fs.readFileSync(inFile, 'utf8'));
const out = {};
for (const [label, req] of Object.entries(reqs)) {
  const res = JSON.parse(globalThis.computeStatsJson(JSON.stringify({ raid: req.raid, encounter: req.encounter })));
  if (res.errorResult) { console.log(label, 'ERROR', res.errorResult); continue; }
  out[label] = res.raidStats.parties[0].players[0];
}
fs.writeFileSync(outFile, JSON.stringify(out));
console.log(Object.keys(out).length, 'presets');
process.exit(0);
