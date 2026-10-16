// Rasterizes #card (must be exactly 1080x1350) and sends it straight to the
// local serve.py, which writes it to D:\Site internet\RS\<filename>.png.
// Add ?preview to the page URL to write to social_content/out/ instead (used
// to check a template change without touching the RS folder).
// (Not using a browser <a download> click here: Chrome silently blocks the
// 2nd+ automatic download from the same origin in a session, so a real save
// button click only reliably works once per page load.)
// Waits for web fonts and for window.__ready (a Promise a data-driven card can
// set while it fetches/renders its data) before capturing.
function exportCard() {
  const btn = document.getElementById('exportBtn');
  if (btn) btn.textContent = 'Export en cours...';
  const filename = document.getElementById('card').dataset.filename || 'brokenmeta-post';
  const preview = new URLSearchParams(location.search).has('preview');
  Promise.resolve(window.__ready)
    .then(function () { return document.fonts && document.fonts.ready; })
    .then(function () {
      return html2canvas(document.getElementById('card'), {
        width: 1080,
        height: 1350,
        scale: 1,
        backgroundColor: '#070a2b',
        useCORS: true,
      });
    }).then(function (canvas) {
      const dataUrl = canvas.toDataURL('image/png');
      const base64 = dataUrl.slice(dataUrl.indexOf(',') + 1);
      return fetch('/save-png', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: filename, data: base64, preview: preview }),
      });
    }).then(function (res) { return res.json(); }).then(function (json) {
      if (btn) btn.textContent = 'Exporté ✔ (' + json.path + ')';
      window.__exportDone = true;
      window.__exportPath = json.path;
    }).catch(function (err) {
      if (btn) btn.textContent = 'Erreur export';
      window.__exportError = String(err);
    });
}

window.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('exportBtn');
  if (btn) btn.addEventListener('click', exportCard);
});
