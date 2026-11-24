(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";

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

  function buildDotSvg() {
    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "sf-swb-dot-svg");
    svg.setAttribute("viewBox", "0 0 12 12");
    svg.setAttribute("aria-hidden", "true");

    var halo = document.createElementNS(SVG_NS, "circle");
    halo.setAttribute("class", "sf-swb-dot-halo");
    halo.setAttribute("cx", "6");
    halo.setAttribute("cy", "6");
    halo.setAttribute("r", "4");

    var core = document.createElementNS(SVG_NS, "circle");
    core.setAttribute("class", "sf-swb-dot-core");
    core.setAttribute("cx", "6");
    core.setAttribute("cy", "6");
    core.setAttribute("r", "3");

    svg.appendChild(halo);
    svg.appendChild(core);
    return svg;
  }

  function buildGridIcon() {
    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "sf-swb-count-icon");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");

    var rects = [
      ["3", "3", "7", "7"],
      ["14", "3", "7", "7"],
      ["14", "14", "7", "7"],
      ["3", "14", "7", "7"]
    ];
    for (var i = 0; i < rects.length; i += 1) {
      var rect = document.createElementNS(SVG_NS, "rect");
      rect.setAttribute("x", rects[i][0]);
      rect.setAttribute("y", rects[i][1]);
      rect.setAttribute("width", rects[i][2]);
      rect.setAttribute("height", rects[i][3]);
      rect.setAttribute("rx", "1.5");
      svg.appendChild(rect);
    }
    return svg;
  }

  function init() {
    var mount = document.querySelector('[data-sf-pack-plugin$=".space_welcome_badge"]');
    if (!mount || mount.dataset.sfInit === "1") {
      return;
    }
    mount.dataset.sfInit = "1";

    var cfg = parseConfig(mount);
    var statusLabel = typeof cfg.status_label === "string" ? cfg.status_label.trim() : "持续更新中";
    var tagline = typeof cfg.tagline === "string" ? cfg.tagline.trim() : "";
    var tone =
      cfg.tone === "emerald" || cfg.tone === "amber" || cfg.tone === "neutral" ? cfg.tone : "accent";
    var showCount = cfg.show_count !== false;
    var countSuffix =
      typeof cfg.count_suffix === "string" && cfg.count_suffix.trim() ? cfg.count_suffix.trim() : "个作品";
    var showPulse = cfg.show_pulse !== false;

    if (!statusLabel && !tagline && !showCount) {
      mount.hidden = true;
      return;
    }

    mount.dataset.sfSwbTone = tone;
    mount.dataset.sfSwbPulse = showPulse ? "1" : "0";

    var mainGroup = document.createElement("div");
    mainGroup.className = "sf-swb-main";

    if (statusLabel) {
      var pill = document.createElement("span");
      pill.className = "sf-swb-pill";

      var dotWrap = document.createElement("span");
      dotWrap.className = "sf-swb-dot-wrap";
      dotWrap.appendChild(buildDotSvg());

      var pillText = document.createElement("span");
      pillText.textContent = statusLabel;

      pill.appendChild(dotWrap);
      pill.appendChild(pillText);
      mainGroup.appendChild(pill);
    }

    if (tagline) {
      var tagEl = document.createElement("p");
      tagEl.className = "sf-swb-tagline";
      tagEl.textContent = tagline;
      mainGroup.appendChild(tagEl);
    }

    if (mainGroup.childNodes.length > 0) {
      mount.appendChild(mainGroup);
    }

    if (showCount) {
      var cardCount = document.querySelectorAll("main .grid > .card").length;
      var countEl = document.createElement("div");
      countEl.className = "sf-swb-count";

      var numEl = document.createElement("span");
      numEl.className = "sf-swb-count-num";
      numEl.textContent = String(cardCount);

      var suffixEl = document.createElement("span");
      suffixEl.textContent = countSuffix;

      countEl.appendChild(buildGridIcon());
      countEl.appendChild(numEl);
      countEl.appendChild(suffixEl);
      mount.appendChild(countEl);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
