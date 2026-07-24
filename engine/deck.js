/* ============================================================================
   Deck engine — navigation, fullscreen, auto-hiding controls, progress.
   Classic script (no modules) so it runs when served or opened directly.
   Emits `deck:change` on document with { index, slide } when the slide changes.
   ============================================================================ */
(function () {
  "use strict";

  var deck = document.getElementById("deck");
  if (!deck) return;
  var slides = Array.prototype.slice.call(deck.querySelectorAll(".slide"));
  if (!slides.length) return;

  var idx = 0;
  var els = {
    counterCur: document.querySelector("[data-counter-cur]"),
    counterTot: document.querySelector("[data-counter-tot]"),
    bar: document.querySelector(".progress .bar"),
    controls: document.querySelector(".controls"),
    btnFs: document.querySelector("[data-action='fullscreen']"),
  };

  function clamp(i) { return Math.max(0, Math.min(slides.length - 1, i)); }

  function show(i, opts) {
    i = clamp(i);
    idx = i;
    slides.forEach(function (s, n) {
      s.classList.toggle("is-active", n === i);
      s.classList.toggle("is-past", n < i);
    });
    if (els.counterCur) els.counterCur.textContent = String(i + 1);
    if (els.bar) els.bar.style.width = (slides.length > 1 ? (i / (slides.length - 1)) * 100 : 100) + "%";
    if (!opts || !opts.silentHash) {
      try { history.replaceState(null, "", "#" + (i + 1)); } catch (e) {}
    }
    document.dispatchEvent(new CustomEvent("deck:change", { detail: { index: i, slide: slides[i] } }));
  }

  function next() { if (idx < slides.length - 1) show(idx + 1); }
  function prev() { if (idx > 0) show(idx - 1); }

  /* ---- keyboard ---------------------------------------------------------- */
  document.addEventListener("keydown", function (e) {
    var t = e.target;
    var onControl = t && (t.tagName === "BUTTON" || t.tagName === "A" || t.tagName === "INPUT" || t.tagName === "IFRAME");
    switch (e.key) {
      case "ArrowRight": case "PageDown": e.preventDefault(); next(); break;
      case "ArrowLeft":  case "PageUp":   e.preventDefault(); prev(); break;
      case " ": case "Spacebar":
        if (onControl) return;           /* let a focused button/link handle Space */
        e.preventDefault(); next(); break;
      case "Home": e.preventDefault(); show(0); break;
      case "End":  e.preventDefault(); show(slides.length - 1); break;
      case "f": case "F": e.preventDefault(); toggleFs(); break;
      default: return;
    }
    poke();
  });

  /* ---- controls ---------------------------------------------------------- */
  var nextBtn = document.querySelector("[data-action='next']");
  var prevBtn = document.querySelector("[data-action='prev']");
  if (nextBtn) nextBtn.addEventListener("click", function () { next(); poke(); });
  if (prevBtn) prevBtn.addEventListener("click", function () { prev(); poke(); });
  if (els.btnFs) els.btnFs.addEventListener("click", function () { toggleFs(); poke(); });

  /* ---- fullscreen -------------------------------------------------------- */
  function toggleFs() {
    var d = document;
    if (!d.fullscreenElement && !d.webkitFullscreenElement) {
      var el = deck;
      (el.requestFullscreen || el.webkitRequestFullscreen || function () {}).call(el);
    } else {
      (d.exitFullscreen || d.webkitExitFullscreen || function () {}).call(d);
    }
  }
  function syncFsIcon() {
    var fs = !!(document.fullscreenElement || document.webkitFullscreenElement);
    if (els.btnFs) els.btnFs.setAttribute("aria-label", fs ? "Salir de pantalla completa" : "Pantalla completa");
    if (els.btnFs) els.btnFs.classList.toggle("is-fs", fs);
  }
  document.addEventListener("fullscreenchange", syncFsIcon);
  document.addEventListener("webkitfullscreenchange", syncFsIcon);

  /* ---- auto-hide controls + cursor -------------------------------------- */
  var hideT;
  function poke() {
    deck.classList.remove("cursor-hidden");
    if (els.controls) els.controls.classList.remove("hidden");
    clearTimeout(hideT);
    hideT = setTimeout(function () {
      deck.classList.add("cursor-hidden");
      if (els.controls) els.controls.classList.add("hidden");
    }, 2600);
  }
  deck.addEventListener("mousemove", poke);
  deck.addEventListener("mousedown", poke);
  window.addEventListener("touchstart", poke, { passive: true });

  /* ---- boot -------------------------------------------------------------- */
  if (els.counterTot) els.counterTot.textContent = String(slides.length);
  var start = 0;
  if (location.hash) { var h = parseInt(location.hash.slice(1), 10); if (!isNaN(h)) start = clamp(h - 1); }
  show(start, { silentHash: true });
  poke();

  window.Deck = { next: next, prev: prev, go: show, get index() { return idx; }, get count() { return slides.length; } };
})();
