/* BrokenLogs worker: reads the dropped file by chunks (a combat log can be several hundred MB), feeds every line to the parser and posts progress.
 * Receives { file, core } where core is the URL of wow-logs-core.js (versioned by the page). Nothing is sent anywhere. */
self.onmessage = function (e) {
  var file = e.data.file;
  importScripts(e.data.core);
  var parser = new self.WowLogs.Parser();
  var total = file.size, read = 0, lastPost = 0, buf = '', decoder = new TextDecoder('utf-8');
  var t0 = Date.now(), sawCombat = false, advanced = true;
  function eat(chunk, final) {
    buf += chunk;
    var start = 0, i, line;
    while ((i = buf.indexOf('\n', start)) >= 0) {
      line = buf.slice(start, i);
      start = i + 1;
      if (line.charCodeAt(line.length - 1) === 13) line = line.slice(0, -1);
      if (!sawCombat && line.indexOf('_DAMAGE') > 0) sawCombat = true;
      if (line.indexOf('COMBAT_LOG_VERSION') > 0 && line.indexOf('ADVANCED_LOG_ENABLED,0') > 0) advanced = false;
      parser.line(line);
    }
    buf = buf.slice(start);
    if (final && buf) { parser.line(buf); buf = ''; }
  }
  var reader = file.stream().getReader();
  (function pump() {
    reader.read().then(function (r) {
      if (r.done) {
        eat(decoder.decode(), true);
        var result = parser.finish();
        result.meta.seconds = Math.round((Date.now() - t0) / 100) / 10;
        result.meta.advanced = advanced;
        result.meta.sawCombat = sawCombat;
        self.postMessage({ type: 'done', result: result });
        return;
      }
      read += r.value.length;
      eat(decoder.decode(r.value, { stream: true }), false);
      if (Date.now() - lastPost > 120) { lastPost = Date.now(); self.postMessage({ type: 'progress', read: read, total: total, lines: parser.lines }); }
      pump();
    }, function (err) { self.postMessage({ type: 'error', message: String(err && err.message || err) }); });
  })();
};
