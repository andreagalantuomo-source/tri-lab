/* JS condiviso delle pagine pilastro: reveal, anno, marquee, contatori. */
/* ============================================================
   TRI LAB — JS condiviso delle pagine pilastro
   Nessuna dipendenza esterna: reveal on scroll + anno corrente.
   ============================================================ */
(function () {
  'use strict';

  /* Reveal on scroll */
  var els = document.querySelectorAll('.reveal');
  function revealAll() { els.forEach(function (el) { el.classList.add('in'); }); }

  if ('IntersectionObserver' in window && els.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });

    /* Rete di sicurezza: se dopo il load nulla si è rivelato (tab aperta in
       background → l'observer non scatta), mostra tutto senza animazione.
       Se anche solo un elemento è già .in, l'animazione scroll è viva → non tocca. */
    window.addEventListener('load', function () {
      setTimeout(function () {
        if (!document.querySelector('.reveal.in')) revealAll();
      }, 600);
    });
  } else {
    revealAll();
  }

  /* Anno corrente nel footer */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  /* Marquee (come in home): duplica il contenuto una volta, poi
     l'animazione CSS trasla di -50% per il loop senza stacchi. */
  var mt = document.querySelector('.hub-marquee-track');
  if (mt) mt.innerHTML += mt.innerHTML;

  /* Contatori stats (come in home, senza GSAP): parte quando la
     stat entra in viewport, easing cubic-out, rispetta reduced-motion. */
  var counters = document.querySelectorAll('.hub-stat [data-count]');
  if (counters.length) {
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var run = function (el) {
      var end = +el.getAttribute('data-count');
      if (reduced || !('requestAnimationFrame' in window)) { el.textContent = end; return; }
      var t0 = null;
      var step = function (t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / 1300, 1);
        p = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(end * p);
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    if ('IntersectionObserver' in window) {
      var cio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          cio.unobserve(en.target);
          run(en.target);
        });
      }, { threshold: 0.4 });
      counters.forEach(function (el) { cio.observe(el); });
    } else {
      counters.forEach(run);
    }
  }
})();
