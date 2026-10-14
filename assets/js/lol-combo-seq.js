// Illustrated combo sequences (LoL combo pages): the "play" button lights the steps one after the other and writes each step's cooldown and cost
// in a caption. Nothing starts by itself; hovering or focusing a step shows its details. The strip works without this script.
(function () {
  'use strict';
  var wraps = document.querySelectorAll('.sq-wrap');
  if (!wraps.length) return;
  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { /* old browser */ }
  var STEP_MS = reduce ? 1400 : 850;

  wraps.forEach(function (wrap) {
    var steps = [].slice.call(wrap.querySelectorAll('.sq-step'));
    var btn = wrap.querySelector('.sq-play'), cap = wrap.querySelector('.sq-cap');
    if (!steps.length || !btn || !cap) return;
    var timer = null, running = false;

    function text(step, i) {
      var parts = [btn.getAttribute('data-step') + ' ' + (i + 1) + '/' + steps.length + ' · ' + step.getAttribute('data-key') + ' ' + step.getAttribute('data-name')];
      var cd = step.getAttribute('data-cd'), cost = step.getAttribute('data-cost');
      if (cd) parts.push(btn.getAttribute('data-cd') + ' ' + cd + ' s');
      if (cost) parts.push(btn.getAttribute('data-cost') + ' ' + cost);
      return parts.join(' · ');
    }
    function clear() { steps.forEach(function (s) { s.classList.remove('is-on', 'is-done'); }); }
    function show(i) {
      steps.forEach(function (s, j) { s.classList.toggle('is-on', j === i); s.classList.toggle('is-done', j < i); });
      cap.textContent = text(steps[i], i);
    }
    function stop(finished) {
      if (timer) { clearTimeout(timer); timer = null; }
      running = false;
      btn.textContent = finished ? btn.getAttribute('data-replay') : btn.getAttribute('data-play');
      if (finished) { steps.forEach(function (s) { s.classList.remove('is-on'); s.classList.add('is-done'); }); cap.textContent = btn.getAttribute('data-done'); }
    }
    function run(i) {
      if (i >= steps.length) { stop(true); return; }
      show(i);
      timer = setTimeout(function () { run(i + 1); }, STEP_MS);
    }
    btn.addEventListener('click', function () {
      if (running) { stop(false); clear(); cap.textContent = ''; return; }
      clear(); running = true; btn.textContent = '■';
      run(0);
    });
    steps.forEach(function (s, i) {
      var info = function () { if (!running) cap.textContent = text(s, i); };
      s.addEventListener('mouseenter', info); s.addEventListener('focus', info);
    });
  });
})();
