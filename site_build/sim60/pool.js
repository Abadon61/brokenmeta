// Worker pool (browser): splits N iterations across workers and merges. Falls back to the main thread.
import { mergeRaw, finalize } from './run.js';

export class SimPool {
  constructor(workerUrl, size, data) {
    this.workers = []; this.nextId = 1; this.pending = new Map();
    const n = Math.max(1, size || Math.max(1, (navigator.hardwareConcurrency || 4) - 1));
    for (let i = 0; i < n; i++) {
      const w = new Worker(workerUrl, { type: 'module' });
      w.onmessage = (ev) => { const p = this.pending.get(ev.data.id); if (p) { this.pending.delete(ev.data.id); p(ev.data); } };
      this.workers.push(w);
    }
    this.ready = Promise.all(this.workers.map((w) => this._call(w, { kind: 'init', data })));
  }
  _call(w, msg) { return new Promise((res) => { msg.id = this.nextId++; this.pending.set(msg.id, res); w.postMessage(msg); }); }
  get size() { return this.workers.length; }
  async run(job, iterations, seedBase = 1, onProgress) {
    await this.ready;
    const n = this.workers.length, chunks = [];
    const chunk = 250;               // small chunks keep the progress bar moving and balance the load
    for (let off = 0; off < iterations; off += chunk) chunks.push([off, Math.min(chunk, iterations - off)]);
    const parts = []; let done = 0, idx = 0;
    await Promise.all(this.workers.map(async (w) => {
      while (idx < chunks.length) {
        const [off, cnt] = chunks[idx++];
        const r = await this._call(w, { kind: 'run', job, iterations: cnt, seedBase: seedBase + off });
        parts.push(r.raw); done += cnt;
        if (onProgress) onProgress(done / iterations);
      }
    }));
    return finalize(mergeRaw(parts), job.fightLen);
  }
  terminate() { for (const w of this.workers) w.terminate(); }
}
