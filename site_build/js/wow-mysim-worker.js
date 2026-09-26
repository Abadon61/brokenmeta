/* Runs site_build/wow_mysim.py (and the wow_dps_sim.py engine it wraps) inside Pyodide, off the
   page's main thread. The Python sources and the data files they read are published by
   build_site.py under assets/wowsim/, listed in manifest.json with a content hash each. */
'use strict';

var PYODIDE_VERSION = '0.29.5';
var PYODIDE_URL = 'https://cdn.jsdelivr.net/npm/pyodide@' + PYODIDE_VERSION + '/';
var ready = null;

function post(type, extra) {
  var msg = { type: type };
  for (var k in extra) msg[k] = extra[k];
  self.postMessage(msg);
}

function boot(base, manifestHash) {
  if (ready) return ready;
  ready = (async function () {
    post('status', { step: 'engine' });
    importScripts(PYODIDE_URL + 'pyodide.js');
    var pyodide = await loadPyodide({ indexURL: PYODIDE_URL });

    post('status', { step: 'files' });
    // ?h= from the page's own (network-fresh) HTML: the site's service worker serves assets
    // cache-first, so a fixed URL here would keep returning an old manifest.
    var manifest = await (await fetch(base + 'manifest.json?h=' + manifestHash)).json();
    // Mirror the repo layout (site_build/*.py next to data/...) so the modules' own
    // ROOT = parent.parent path logic finds the data exactly as it does locally.
    await Promise.all(manifest.files.map(async function (f) {
      var res = await fetch(base + f.path + '?h=' + f.hash);
      if (!res.ok) throw new Error('fetch ' + f.path + ' ' + res.status);
      var text = await res.text();
      var full = '/sim/' + f.path;
      var dir = full.slice(0, full.lastIndexOf('/'));
      pyodide.FS.mkdirTree(dir);
      pyodide.FS.writeFile(full, text, { encoding: 'utf8' });
    }));
    pyodide.runPython("import sys; sys.path.insert(0, '/sim/site_build'); import wow_mysim");
    return pyodide;
  })();
  ready.catch(function () { ready = null; });
  return ready;
}

self.onmessage = async function (e) {
  var m = e.data;
  try {
    var pyodide = await boot(m.base, m.manifest);
    post('status', { step: 'sim' });
    pyodide.globals.set('_bm_text', m.text);
    pyodide.globals.set('_bm_spec', m.spec || null);
    pyodide.globals.set('_bm_lang', m.lang);
    var out;
    if (m.action === 'personal') {
      // Personal stat weights + Top gear: ~10 simulation batches, progress reported after each.
      pyodide.globals.set('_bm_progress', function (done, total) { post('progress', { done: done, total: total }); });
      out = pyodide.runPython('wow_mysim.personal(_bm_text, _bm_spec, _bm_lang, _bm_progress)');
    } else {
      out = pyodide.runPython('wow_mysim.simulate(_bm_text, _bm_spec, _bm_lang)');
    }
    post('result', { action: m.action || 'sim', result: JSON.parse(out) });
  } catch (err) {
    post('error', { message: String(err && err.message || err) });
  }
};
