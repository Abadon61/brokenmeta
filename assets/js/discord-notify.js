
(function () {
  var API = window.BM_DISCORD_API;
  var I = window.BM_I18N_DISCORD || {};
  var form = document.getElementById('discordForm');
  var input = document.getElementById('discordWebhookUrl');
  var statusEl = document.getElementById('discordStatus');
  if (!form || !API) return;

  function setStatus(text, isError) {
    if (!text) { statusEl.hidden = true; statusEl.textContent = ''; return; }
    statusEl.hidden = false;
    statusEl.textContent = text;
    statusEl.dataset.error = isError ? 'true' : 'false';
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var action = (e.submitter && e.submitter.dataset.action) || 'subscribe';
    var webhookUrl = input.value.trim();
    var games = [];
    form.querySelectorAll('input[name="game"]').forEach(function (c) { if (c.checked) games.push(c.value); });
    if (action === 'subscribe' && !games.length) { setStatus(I.errorNoGame, true); return; }
    var buttons = form.querySelectorAll('button');
    buttons.forEach(function (b) { b.disabled = true; });
    setStatus('', false);

    fetch(API + '/' + action, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(action === 'subscribe' ? { webhookUrl: webhookUrl, games: games } : { webhookUrl: webhookUrl }),
    })
      .then(function (res) { return res.json().then(function (data) { return { ok: res.ok, data: data }; }); })
      .then(function (r) {
        if (r.ok) {
          setStatus(action === 'subscribe' ? I.successSubscribed : I.successUnsubscribed, false);
          if (window.gtag) gtag('event', 'discord_' + action);
          form.reset();
        } else {
          setStatus((r.data && r.data.error) || I.errorGeneric, true);
        }
      })
      .catch(function () { setStatus(I.errorGeneric, true); })
      .finally(function () { buttons.forEach(function (b) { b.disabled = false; }); });
  });
})();
