importScripts('sim60.7dda14cfcd.js');
let data = null;
self.onmessage = (ev) => {
  const m = ev.data, S = self.Sim60;
  if (m.kind === 'init') { data = m.data; self.postMessage({ id: m.id, ok: true }); return; }
  if (m.kind === 'run') {
    const j = m.job;
    const cfg = { fightLen: j.fightLen, player: j.player, target: j.target, kitFactory: () => S.makeKit(j.kitName, j.kitBuild, data) };
    self.postMessage({ id: m.id, raw: S.runBatchRaw(cfg, m.iterations, m.seedBase) });
  } else if (m.kind === 'weights') {
    const j = m.job;
    const cfg = { fightLen: j.fightLen, player: j.player, target: j.target, kitFactory: () => S.makeKit(j.kitName, j.kitBuild, data) };
    self.postMessage({ id: m.id, result: S.statWeights(cfg, m.iterations, m.seedBase) });
  } else if (m.kind === 'optimize') {
    const j = m.job, pool = new S.ItemPool(m.items, m.proficiency);
    const res = S.optimizeGear({ pool, character: m.character, kit: () => S.makeKit(j.kitName, j.kitBuild, data), fightLen: j.fightLen, iterations: m.iterations,
      prefilter: m.prefilter, maxPasses: m.maxPasses, seed: m.seedBase, onProgress: (p) => self.postMessage({ id: m.id, progress: p }) });
    self.postMessage({ id: m.id, result: res });
  }
};
