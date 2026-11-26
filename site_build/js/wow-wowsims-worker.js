/* BrokenMeta: one WoWSims Forever engine (github.com/wowsims/forever, MIT) per worker. The page compiles lib.wasm once and
   posts the WebAssembly.Module; each message {req} answers with the engine's JSON result (raidSimJson). */
let ready = null;
self.onmessage = async (e) => {
  const d = e.data;
  if (d.init) {
    importScripts(d.execUrl);                       // Go's wasm_exec.js: defines self.Go
    ready = (async () => {
      const go = new self.Go();
      self.wasmready = () => {};                    // the engine calls it once its functions are registered
      const inst = await WebAssembly.instantiate(d.module, go.importObject);
      go.run(inst);
    })();
    return;
  }
  try {
    await ready;
    self.postMessage({ id: d.id, out: self.raidSimJson(JSON.stringify(d.req)) });
  } catch (err) {
    self.postMessage({ id: d.id, error: String(err && err.message || err) });
  }
};
