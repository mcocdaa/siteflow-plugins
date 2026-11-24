(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  var RING_RADIUS = 6;
  var RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

  function parseConfig(mount) {
    var node = mount.querySelector("[data-sf-pack-config]");
    if (!node || !node.textContent) {
      return {};
    }
    try {
      var parsed = JSON.parse(node.textContent);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (_) {
      return {};
    }
  }

  function clampInt(value, min, max, fallback) {
    var num = Number(value);
    if (!Number.isFinite(num)) {
      return fallback;
    }
    return Math.min(max, Math.max(min, Math.round(num)));
  }

  function buildRingSvg() {
    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "sf-rp-ring");
    svg.setAttribute("viewBox", "0 0 16 16");
    svg.setAttribute("aria-hidden", "true");

    var bg = document.createElementNS(SVG_NS, "circle");
    bg.setAttribute("class", "sf-rp-ring-bg");
    bg.setAttribute("cx", "8");
    bg.setAttribute("cy", "8");
    bg.setAttribute("r", String(RING_RADIUS));

    var fg = document.createElementNS(SVG_NS, "circle");
    fg.setAttribute("class", "sf-rp-ring-fg");
    fg.setAttribute("cx", "8");
    fg.setAttribute("cy", "8");
    fg.setAttribute("r", String(RING_RADIUS));
    fg.setAttribute("stroke-dasharray", RING_CIRCUMFERENCE.toFixed(2));
    fg.setAttribute("stroke-dashoffset", RING_CIRCUMFERENCE.toFixed(2));

    svg.appendChild(bg);
    svg.appendChild(fg);
    return { svg: svg, fg: fg };
  }

  function computeProgress() {
    var article = document.querySelector(".post") || document.querySelector(".post-body");
    var viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
    var scrollTop = window.scrollY || document.documentElement.scrollTop || 0;

    if (article) {
      var rect = article.getBoundingClientRect();
      var articleTop = rect.top + scrollTop;
      var scrollable = article.offsetHeight - viewportHeight * 0.7;
      if (scrollable > 40) {
        var raw = (scrollTop - articleTop + viewportHeight * 0.15) / scrollable;
        return Math.min(1, Math.max(0, raw));
      }
    }

    var doc = document.documentElement;
    var maxScroll = Math.max(0, (doc.scrollHeight || 0) - viewportHeight);
    if (maxScroll <= 0) {
      return 0;
    }
    return Math.min(1, Math.max(0, scrollTop / maxScroll));
  }

  function init() {
    var mount = document.querySelector('[data-sf-pack-plugin$=".reading_progress"]');
    if (!mount || mount.dataset.sfInit === "1") {
      return;
    }
    mount.dataset.sfInit = "1";

    var cfg = parseConfig(mount);
    var heightPx = clampInt(cfg.height_px, 2, 6, 3);
    var colorStyle =
      cfg.color_style === "gradient" || cfg.color_style === "mono" ? cfg.color_style : "accent";
    var showPercentage = cfg.show_percentage !== false;
    var pillPosition =
      cfg.pill_position === "bottom-left" || cfg.pill_position === "top-right"
        ? cfg.pill_position
        : "bottom-right";
    var hideAtTop = cfg.hide_at_top !== false;

    mount.dataset.sfRpHeight = String(heightPx);
    mount.dataset.sfRpStyle = colorStyle;
    mount.dataset.sfRpPillPos = pillPosition;

    var track = document.createElement("div");
    track.className = "sf-rp-track";
    track.setAttribute("role", "progressbar");
    track.setAttribute("aria-label", "Reading progress");
    track.setAttribute("aria-valuemin", "0");
    track.setAttribute("aria-valuemax", "100");
    track.setAttribute("aria-valuenow", "0");

    var bar = document.createElement("div");
    bar.className = "sf-rp-bar";
    track.appendChild(bar);
    mount.appendChild(track);

    var pillText = null;
    var ringFg = null;

    if (showPercentage) {
      var pill = document.createElement("button");
      pill.type = "button";
      pill.className = "sf-rp-pill";
      pill.setAttribute("aria-label", "Back to top");
      pill.title = "Back to top";

      var ring = buildRingSvg();
      ringFg = ring.fg;
      pillText = document.createElement("span");
      pillText.className = "sf-rp-pct";
      pillText.textContent = "0%";

      pill.appendChild(ring.svg);
      pill.appendChild(pillText);
      pill.addEventListener("click", function () {
        var reduced =
          typeof window.matchMedia === "function" &&
          window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
      });
      mount.appendChild(pill);
    }

    var rafId = 0;

    function update() {
      rafId = 0;
      var ratio = computeProgress();
      var pct = Math.round(ratio * 100);
      var scrollTop = window.scrollY || document.documentElement.scrollTop || 0;

      bar.style.setProperty("--sf-rp-scale", ratio.toFixed(4));
      track.setAttribute("aria-valuenow", String(pct));

      if (pillText && ringFg) {
        pillText.textContent = pct + "%";
        var offset = RING_CIRCUMFERENCE * (1 - ratio);
        ringFg.setAttribute("stroke-dashoffset", offset.toFixed(2));
      }

      var isIdle = hideAtTop && scrollTop < 24;
      mount.classList.toggle("is-idle", isIdle);
    }

    function scheduleUpdate() {
      if (!rafId) {
        rafId = window.requestAnimationFrame(update);
      }
    }

    window.addEventListener("scroll", scheduleUpdate, { passive: true });
    window.addEventListener("resize", scheduleUpdate, { passive: true });
    update();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
