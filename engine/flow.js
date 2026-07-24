/* ============================================================================
   Flow — interactive pipeline. Click a node or drag the scrubber; the active
   step's description rises into the caption zone. One instance per `.flow`.
   Node markup: <button class="flow-node" data-label data-title data-desc [data-cr]>
   ============================================================================ */
(function () {
  "use strict";

  function initFlow(flow) {
    var nodes = Array.prototype.slice.call(flow.querySelectorAll(".flow-node"));
    if (!nodes.length) return;
    var n = nodes.length;
    flow.querySelector(".flow-nodes").style.setProperty("--n", n);

    var cap = flow.querySelector(".flow-caption");
    var capStepNum = cap.querySelector(".fc-step .num");
    var capStepName = cap.querySelector(".fc-step .name");
    var capCr = cap.querySelector(".fc-step .cr");
    var capTitle = cap.querySelector(".fc-title");
    var capDesc = cap.querySelector(".fc-desc");

    var fill = flow.querySelector(".flow-track .fill");
    var scrub = flow.querySelector(".flow-scrub");
    var scrubFill = scrub ? scrub.querySelector(".rail-fill") : null;
    var knob = scrub ? scrub.querySelector(".knob") : null;

    var active = -1;

    function pct(i) { return n > 1 ? (i / (n - 1)) * 100 : 0; }

    function setActive(i, opts) {
      i = Math.max(0, Math.min(n - 1, i));
      if (i === active) return;
      active = i;
      nodes.forEach(function (nd, k) {
        nd.classList.toggle("is-active", k === i);
        nd.classList.toggle("done", k < i);
        nd.setAttribute("aria-selected", k === i ? "true" : "false");
      });
      var nd = nodes[i];
      if (capStepNum) capStepNum.textContent = String(i + 1).padStart(2, "0");
      if (capStepName) capStepName.textContent = nd.getAttribute("data-label") || "";
      if (capCr) capCr.hidden = !nd.hasAttribute("data-cr");
      if (capTitle) capTitle.innerHTML = nd.getAttribute("data-title") || nd.getAttribute("data-label") || "";
      if (capDesc) capDesc.textContent = nd.getAttribute("data-desc") || "";
      if (fill) fill.style.width = pct(i) + "%";
      if (scrubFill) scrubFill.style.width = pct(i) + "%";
      if (knob) knob.style.left = pct(i) + "%";
      // retrigger crossfade
      if (cap) { cap.classList.remove("swap"); void cap.offsetWidth; cap.classList.add("swap"); }
    }

    nodes.forEach(function (nd, i) {
      nd.setAttribute("role", "tab");
      nd.addEventListener("click", function () { setActive(i); });
      nd.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); setActive(i); }
      });
      nd.addEventListener("mouseenter", function () { /* hover preview handled by CSS; keep click as commit */ });
    });

    /* scrubber drag → snap to nearest node ---------------------------------- */
    if (scrub && knob) {
      var dragging = false;
      function ratioFromEvent(e) {
        var r = scrub.getBoundingClientRect();
        var x = (e.touches ? e.touches[0].clientX : e.clientX) - r.left;
        return Math.max(0, Math.min(1, x / r.width));
      }
      function toIndex(ratio) { return Math.round(ratio * (n - 1)); }
      function onMove(e) {
        if (!dragging) return;
        setActive(toIndex(ratioFromEvent(e)));
        if (e.cancelable) e.preventDefault();
      }
      function start(e) {
        dragging = true; scrub.classList.add("dragging");
        setActive(toIndex(ratioFromEvent(e)));
        window.addEventListener("pointermove", onMove);
        window.addEventListener("pointerup", end);
      }
      function end() {
        dragging = false; scrub.classList.remove("dragging");
        window.removeEventListener("pointermove", onMove);
        window.removeEventListener("pointerup", end);
      }
      scrub.addEventListener("pointerdown", start);
    }

    setActive(0);
  }

  function boot() {
    Array.prototype.slice.call(document.querySelectorAll(".flow")).forEach(initFlow);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
