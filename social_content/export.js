// Rasterizes #card (must be exactly 1080x1350) and sends it straight to the
// local serve.py, which writes it to social_content/out/<filename>.png.
// (Not using a browser <a download> click here: Chrome silently blocks the
// 2nd+ automatic download from the same origin in a session, so a real save
// button click only reliably works once per page load.)
function exportCard() {
  const btn = document.getElementById('exportBtn');
  if (btn) btn.textContent = 'Export en cours...';
  const filename = document.getElementById('card').dataset.filename || 'brokenmeta-post';
  html2canvas(document.getElementById('card'), {
    width: 1080,
    height: 1350,
    scale: 1,
    backgroundColor: '#0b0221',
    useCORS: true,
  }).then(function (canvas) {
    const dataUrl = canvas.toDataURL('image/png');
    const base64 = dataUrl.slice(dataUrl.indexOf(',') + 1);
    return fetch('/save-png', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: filename, data: base64 }),
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
