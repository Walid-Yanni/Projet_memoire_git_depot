(function () {
  var sb = document.getElementById('sidebar'), sc = document.getElementById('scrim'), btn = document.getElementById('menuBtn');
  function toggle(open) { if (!sb) return; sb.classList.toggle('open', open); sc.classList.toggle('open', open); }
  if (btn) btn.addEventListener('click', function () { toggle(!sb.classList.contains('open')); });
  if (sc) sc.addEventListener('click', function () { toggle(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') toggle(false); });
  document.querySelectorAll('[data-close]').forEach(function (b) { b.addEventListener('click', function () { b.closest('.toast').remove(); }); });
  setTimeout(function () { document.querySelectorAll('.toast').forEach(function (t) { t.style.transition = 'opacity .4s'; t.style.opacity = 0; setTimeout(function () { t.remove(); }, 450); }); }, 6000);
})();
