(function () {
  'use strict';
  // "Share my data": reads the addon's SavedVariables file (BrokenMetaWeights.lua) IN THE
  // BROWSER, keeps only BrokenMetaWeightsDB.data (measurements + auction scans: no character
  // name, no settings), shows exactly what will be sent, and uploads it to wow-worker only after
  // the player ticks the consent box. Each upload returns a deletion code.
  var root = document.getElementById('shApp');
  if (!root) return;
  var T = JSON.parse(document.getElementById('shI18n').textContent);
  var $ = function (id) { return document.getElementById(id); };
  var drop = $('shDrop'), fileInput = $('shFile'), preview = $('shPreview'), consent = $('shConsent'),
      sendBtn = $('shSend'), status = $('shStatus'), result = $('shResult');
  var payload = null;
  var CODES_KEY = 'bm-share-codes';

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function say(text, isError) {
    status.textContent = text || '';
    status.className = 'ms-status' + (isError ? ' is-error' : '');
  }

  // ---- Minimal parser for WoW SavedVariables (a restricted Lua table-literal syntax).
  function parseSavedVariables(src) {
    var i = 0, n = src.length;
    function ws() {
      for (;;) {
        while (i < n && /\s/.test(src[i])) i++;
        if (src[i] === '-' && src[i + 1] === '-') { while (i < n && src[i] !== '\n') i++; continue; }
        return;
      }
    }
    function fail(msg) { throw new Error(msg + ' @' + i); }
    function str() {
      var q = src[i++], out = '';
      while (i < n && src[i] !== q) {
        var c = src[i++];
        if (c === '\\') {
          var e = src[i++];
          if (e === 'n') out += '\n';
          else if (e === 't') out += '\t';
          else if (/[0-9]/.test(e)) {
            var d = e;
            while (d.length < 3 && /[0-9]/.test(src[i])) d += src[i++];
            out += String.fromCharCode(parseInt(d, 10));
          } else out += e;
        } else out += c;
      }
      if (src[i++] !== q) fail('unterminated string');
      return out;
    }
    function num() {
      var m = /^-?(?:0x[0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?|inf|nan)/.exec(src.slice(i, i + 64));
      if (!m) fail('bad number');
      i += m[0].length;
      return Number(m[0]);
    }
    function value() {
      ws();
      var c = src[i];
      if (c === '{') return table();
      if (c === '"' || c === "'") return str();
      if (c === '-' || c === '.' || /[0-9]/.test(c)) return num();
      var w = /^[A-Za-z_]\w*/.exec(src.slice(i, i + 16));
      if (w) {
        i += w[0].length;
        if (w[0] === 'true') return true;
        if (w[0] === 'false') return false;
        if (w[0] === 'nil') return null;
      }
      fail('unexpected token');
    }
    function table() {
      i++; // {
      var arr = [], obj = {}, isArray = true, next = 1;
      for (;;) {
        ws();
        if (src[i] === '}') { i++; break; }
        var key = null;
        if (src[i] === '[') {
          i++;
          key = value();
          ws();
          if (src[i++] !== ']') fail('expected ]');
          ws();
          if (src[i++] !== '=') fail('expected =');
        } else {
          var m = /^[A-Za-z_]\w*\s*=(?!=)/.exec(src.slice(i, i + 80));
          if (m) { key = m[0].replace(/\s*=$/, ''); i += m[0].length; }
        }
        var v = value();
        if (key === null) key = next;
        if (key === next) next++; else isArray = false;
        obj[key] = v;
        arr.push(v);
        ws();
        if (src[i] === ',' || src[i] === ';') i++;
      }
      return isArray ? arr : obj;
    }
    var out = {};
    for (;;) {
      ws();
      if (i >= n) break;
      var name = /^[A-Za-z_]\w*/.exec(src.slice(i, i + 80));
      if (!name) fail('expected variable name');
      i += name[0].length;
      ws();
      if (src[i++] !== '=') fail('expected =');
      out[name[0]] = value();
    }
    return out;
  }

  // Text copied from the addon (Data tab > "Copy for the site"), see ns.BuildShareString in
  // Collect.lua. Returns the same shape as the SavedVariables table so load() handles both.
  function parseShareText(text) {
    function dec(v) { try { return decodeURIComponent(v); } catch (e) { return v; } }
    function val(v) { v = dec(v); return /^-?\d+(\.\d+)?$/.test(v) ? Number(v) : v; }
    function fields(str) {
      var o = {};
      (str || '').split(';').forEach(function (kv) {
        var i = kv.indexOf('=');
        if (i > 0) o[dec(kv.slice(0, i))] = val(kv.slice(i + 1));
      });
      return o;
    }
    var lines = text.replace(/\r/g, '').split('\n').map(function (l) { return l.trim(); }).filter(Boolean);
    if (!lines.length || lines[0].slice(0, 4) !== 'BMD1') return null;
    var head = fields(lines[0].slice(5));
    var data = { addon: head.addon, client: head.client, meas: [], ah: [] }, scan = null;
    lines.slice(1).forEach(function (l) {
      var tag = l.slice(0, 2), rest = l.slice(2);
      if (tag === 'M ') data.meas.push(fields(rest));
      else if (tag === 'A ') { scan = fields(rest); scan.prices = {}; data.ah.push(scan); }
      else if (tag === 'P ' && scan) {
        rest.split(';').forEach(function (e) {
          var n = e.split(',').map(Number);
          if (n.length === 4 && n.every(isFinite)) scan.prices[n[0]] = [n[1], n[2], n[3]];
        });
      }
    });
    // The addon only produces this text when sharing is on.
    return { BrokenMetaWeightsDB: { share: true, data: data, chars: {} } };
  }

  function asArray(v) { return Array.isArray(v) ? v : (v && typeof v === 'object' ? Object.values(v) : []); }

  function load(text) {
    payload = null;
    sendBtn.disabled = true;
    result.hidden = true;
    var db;
    try {
      var trimmed = text.replace(/^\s+/, '');
      db = (trimmed.slice(0, 4) === 'BMD1' ? parseShareText(trimmed) : parseSavedVariables(text)).BrokenMetaWeightsDB;
    } catch (e) { console.error(e); db = null; }
    if (!db || typeof db !== 'object') { preview.hidden = true; return say(T.err_file, true); }
    var data = db.data && typeof db.data === 'object' ? db.data : null;
    var meas = data ? asArray(data.meas) : [];
    var ah = data ? asArray(data.ah) : [];
    if (!meas.length && !ah.length) { preview.hidden = true; return say(T.err_nodata, true); }

    var kinds = {}, prices = 0, scans = [];
    meas.forEach(function (m) { if (m && m.k) kinds[m.k] = (kinds[m.k] || 0) + 1; });
    ah.forEach(function (s) {
      if (!s || !s.prices) return;
      var n = Object.keys(s.prices).length;
      prices += n;
      scans.push(esc(s.realm || '?') + ' (' + esc(s.faction || '?') + ') · ' + n + ' ' + esc(T.items));
    });
    var names = db.chars && typeof db.chars === 'object' ? Object.keys(db.chars).length : 0;
    // Only these fields leave the browser; the worker whitelists them again server-side.
    payload = {
      format: 'BMD1', addon: data.addon || '', client: data.client || '',
      meas: meas,
      ah: ah.map(function (s) { return { t: s.t, realm: s.realm, faction: s.faction, mode: s.mode, listings: s.listings, prices: s.prices }; })
    };
    preview.innerHTML =
      '<h2 class="fiche-section-title">' + esc(T.preview_h2) + '</h2>' +
      '<ul class="ms-limits">' +
        '<li>' + esc(T.p_meas.replace('{n}', meas.length)) + ' — ' + Object.keys(kinds).map(function (k) {
          return esc((T['kind_' + k] || k) + ' : ' + kinds[k]);
        }).join(', ') + '</li>' +
        '<li>' + esc(T.p_ah.replace('{n}', scans.length).replace('{p}', prices)) + (scans.length ? '<br>' + scans.join('<br>') : '') + '</li>' +
        '<li>' + esc(T.p_not_sent.replace('{n}', names)) + '</li>' +
        '<li>' + esc(T.p_version.replace('{v}', data.addon || '?').replace('{c}', data.client || '?')) + '</li>' +
      '</ul>' +
      (db.share === true ? '' : '<p class="wow-note">' + esc(T.share_off) + '</p>');
    preview.hidden = false;
    if (db.share !== true) { payload = null; return say(''); }
    say('');
    sendBtn.disabled = !consent.checked;
  }

  function readFile(file) {
    if (!file) return;
    if (file.size > 20e6) return say(T.err_file, true);
    var reader = new FileReader();
    reader.onload = function () { load(String(reader.result || '')); };
    reader.onerror = function () { say(T.err_file, true); };
    reader.readAsText(file);
  }

  function rememberCode(code) {
    try {
      var list = JSON.parse(localStorage.getItem(CODES_KEY) || '[]');
      list.push({ code: code, at: new Date().toISOString() });
      localStorage.setItem(CODES_KEY, JSON.stringify(list.slice(-20)));
    } catch (e) {}
  }

  fileInput.addEventListener('change', function () { readFile(fileInput.files[0]); });
  var pasteTimer = null;
  $('shPaste').addEventListener('input', function () {
    clearTimeout(pasteTimer);
    var v = this.value;
    pasteTimer = setTimeout(function () { if (v.trim()) load(v); }, 250);
  });
  ['dragenter', 'dragover'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('is-over'); });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('is-over'); });
  });
  drop.addEventListener('drop', function (e) { readFile(e.dataTransfer.files[0]); });
  consent.addEventListener('change', function () { sendBtn.disabled = !(payload && consent.checked); });

  sendBtn.addEventListener('click', function () {
    if (!payload || !consent.checked) return;
    sendBtn.disabled = true;
    say(T.sending);
    fetch(window.BM_WOW_API + '/v1/submit', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    }).then(function (r) { return r.json().then(function (j) { return { status: r.status, body: j }; }); })
      .then(function (res) {
        if (!res.body.ok) {
          sendBtn.disabled = false;
          return say(T['err_' + res.body.error] || T.err_server, true);
        }
        say('');
        rememberCode(res.body.deletion_code);
        result.innerHTML = '<p class="ms-diff is-up">' + esc(T.sent.replace('{m}', res.body.measurements).replace('{p}', res.body.prices)) + '</p>' +
          '<p>' + esc(T.code_intro) + '</p><p><code class="sh-code">' + esc(res.body.deletion_code) + '</code></p>';
        result.hidden = false;
        payload = null;
      })
      .catch(function () { sendBtn.disabled = false; say(T.err_network, true); });
  });

  $('shDelete').addEventListener('click', function () {
    var code = $('shDeleteCode').value.trim().toLowerCase();
    var out = $('shDeleteStatus');
    if (!/^[0-9a-f]{32}$/.test(code)) { out.textContent = T.del_bad; return; }
    out.textContent = T.sending;
    fetch(window.BM_WOW_API + '/v1/submission', {
      method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code: code })
    }).then(function (r) { return r.json(); })
      .then(function (j) { out.textContent = j.ok ? T.del_ok : (j.error === 'not_found' ? T.del_notfound : T.err_server); })
      .catch(function () { out.textContent = T.err_network; });
  });
})();
