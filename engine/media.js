/* ============================================================================
   Media — ODO screenshot slider + ECO landing device toggle.
   Lazy-loads the landing iframe the first time its slide becomes active.
   ============================================================================ */
(function () {
  "use strict";

  /* ---- ODO screenshot slider -------------------------------------------- */
  function initSlider(root) {
    var frames = Array.prototype.slice.call(root.querySelectorAll(".frame"));
    var dots = Array.prototype.slice.call(root.querySelectorAll(".media-nav .dots button"));
    var cap = root.querySelector(".media-nav .cap");
    var prev = root.querySelector(".media-nav [data-slide='prev']");
    var next = root.querySelector(".media-nav [data-slide='next']");
    if (frames.length < 2 && !cap) return;
    var i = 0;
    function go(k) {
      i = (k + frames.length) % frames.length;
      frames.forEach(function (f, n) { f.classList.toggle("is-active", n === i); });
      dots.forEach(function (d, n) { d.classList.toggle("is-active", n === i); });
      if (cap) cap.textContent = frames[i].getAttribute("data-cap") || "";
    }
    dots.forEach(function (d, n) { d.addEventListener("click", function () { go(n); }); });
    if (prev) prev.addEventListener("click", function () { go(i - 1); });
    if (next) next.addEventListener("click", function () { go(i + 1); });
    go(0);
  }

  /* ---- ECO landing device toggle ---------------------------------------- */
  function initLanding(root) {
    var device = root.querySelector(".device");
    var seg = root.querySelector(".seg");
    if (device && seg) {
      seg.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-device]");
        if (!b) return;
        device.setAttribute("data-device", b.getAttribute("data-device"));
        seg.querySelectorAll("button").forEach(function (x) { x.classList.toggle("is-active", x === b); });
      });
    }
    // lazy-load iframe when the landing slide first activates
    var iframe = root.querySelector("iframe[data-src]");
    var loading = root.querySelector(".frame-loading");
    if (iframe) {
      var slide = root.closest(".slide");
      function load() {
        if (iframe.getAttribute("src")) return;
        iframe.setAttribute("src", iframe.getAttribute("data-src"));
        iframe.addEventListener("load", function () { if (loading) loading.style.display = "none"; });
      }
      document.addEventListener("deck:change", function (e) {
        if (e.detail && e.detail.slide === slide) load();
      });
      if (slide && slide.classList.contains("is-active")) load();
    }
  }

  function boot() {
    Array.prototype.slice.call(document.querySelectorAll(".media")).forEach(initSlider);
    Array.prototype.slice.call(document.querySelectorAll(".landing")).forEach(initLanding);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
