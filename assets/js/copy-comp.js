
(function () {
  var CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
  async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
  document.querySelectorAll('.copy-comp-btn').forEach(function (btn) {
    var originalHTML = btn.innerHTML;
    var originalTitle = btn.title;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      copyToClipboard(btn.dataset.code).then(function () {
        btn.dataset.copied = 'true';
        btn.innerHTML = CHECK_SVG;
        btn.title = btn.dataset.copiedTitle;
      }, function () {
        btn.title = btn.dataset.failedTitle;
      });
      setTimeout(function () {
        btn.dataset.copied = 'false';
        btn.innerHTML = originalHTML;
        btn.title = originalTitle;
      }, 2200);
    });
  });
})();
