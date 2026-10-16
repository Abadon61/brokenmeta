// Shared helpers for the card_wow_*.html templates.
// WOW.digest resolves to wow_digest.json (written by build_wow_digest.py); each card sets
// window.__ready to the promise that renders it, so export.js waits for the data before capturing.
window.WOW = {
  digest: fetch('wow_digest.json').then(function (r) { return r.json(); }),
  // French number formats: 628 / 497,9 / +3,9 %
  n0: function (n) { return String(Math.round(n)); },
  n1: function (n) { return n.toFixed(1).replace('.', ','); },
  pct1: function (n) { return (n >= 0 ? '+' : '') + n.toFixed(1).replace('.', ',') + ' %'; },
  months: ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
  frDate: function (iso) {
    var d = new Date(iso + 'T12:00:00Z');
    return d.getUTCDate() + ' ' + WOW.months[d.getUTCMonth()];
  },
};
