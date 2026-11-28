// Runs one exported RaidSimRequest through the browser build of the WoWSims engine (lib.wasm + Go's wasm_exec.js) in Node,
// to check the WASM gives the CLI's numbers. usage: node wasm_check.mjs <wasm_exec.js> <lib.wasm> <page_x.json> <label> [iterations]
import fs from 'node:fs';
import { createRequire } from 'node:module';
const [, , execJs, wasmPath, pageFile, label, iters = '2000'] = process.argv;
createRequire(import.meta.url)(execJs);          // defines globalThis.Go
const go = new globalThis.Go();
const { instance } = await WebAssembly.instantiate(fs.readFileSync(wasmPath), go.importObject);
globalThis.wasmready = () => {};         // the engine calls it once its functions are registered
go.run(instance);
await new Promise(r => setTimeout(r, 200));
const req = JSON.parse(fs.readFileSync(pageFile, 'utf8'))[label];
delete req._bm; delete req.requestId;
req.simOptions = { iterations: +iters, randomSeed: '101' };
const t0 = Date.now();
const out = JSON.parse(globalThis.raidSimJson(JSON.stringify(req)));
if (!out.raidMetrics) { console.log('ERROR', JSON.stringify(out.error || out).slice(0, 600)); process.exit(1); }
console.log(label, 'dps', out.raidMetrics.dps.avg.toFixed(1), '+-', out.raidMetrics.dps.stdev.toFixed(1), (Date.now() - t0) + ' ms', out.error ? 'ERROR ' + JSON.stringify(out.error) : '');
process.exit(0);
