// Web Worker: runs a slice of fights. Protocol:
//   in : {id, kind:'init', data}                       -> stores spells data
//   in : {id, kind:'run', job:{player,target,fightLen,kitName,kitBuild}, iterations, seedBase}
//   out: {id, raw}
import { runBatchRaw } from './run.js';
import { makeKit } from './kits.js';

let data = null;
self.onmessage = (ev) => {
  const m = ev.data;
  if (m.kind === 'init') { data = m.data; self.postMessage({ id: m.id, ok: true }); return; }
  if (m.kind === 'run') {
    const j = m.job;
    const cfg = { fightLen: j.fightLen, player: j.player, target: j.target, kitFactory: () => makeKit(j.kitName, j.kitBuild, data) };
    self.postMessage({ id: m.id, raw: runBatchRaw(cfg, m.iterations, m.seedBase) });
  }
};
