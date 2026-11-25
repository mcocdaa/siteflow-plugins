(function () {
  "use strict";

  function parseConfig(mount) {
    var node = mount.querySelector("[data-sf-pack-config]");
    if (!node || !node.textContent) return {};
    try {
      var parsed = JSON.parse(node.textContent);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (_) {
      return {};
    }
  }

  function enhanceMount(mount) {
    if (!mount || mount.dataset.sfInit === "1") return;
    mount.dataset.sfInit = "1";

    var cfg = parseConfig(mount);
    var assetBase = mount.dataset.sfAssetBase || "";
    var badgeText = typeof cfg.badge_text === "string" ? cfg.badge_text.trim() : "大肥鱼";
    var badgeStyle = cfg.badge_style === "compact" ? "compact" : "pill";
    var showBubbles = cfg.show_bubbles !== false;
    var showWave = cfg.show_wave !== false;

    mount.dataset.dfyStyle = badgeStyle;
    mount.dataset.dfyBubbles = showBubbles ? "1" : "0";
    mount.dataset.dfyWave = showWave ? "1" : "0";

    var img = document.createElement("img");
    img.className = "sf-dfy-emblem";
    img.src = assetBase + "badge-whale.svg";
    img.width = 22;
    img.height = 22;
    img.alt = "";
    img.setAttribute("aria-hidden", "true");
    mount.appendChild(img);

    if (badgeStyle !== "compact" && badgeText) {
      var label = document.createElement("span");
      label.className = "sf-dfy-label";
      label.textContent = badgeText;
      mount.appendChild(label);
    }

    if (showBubbles) {
      var bubbles = document.createElement("span");
      bubbles.className = "sf-dfy-bubbles";
      bubbles.setAttribute("aria-hidden", "true");
      ["sf-dfy-b1", "sf-dfy-b2", "sf-dfy-b3"].forEach(function (cls) {
        var dot = document.createElement("span");
        dot.className = "sf-dfy-bubble " + cls;
        bubbles.appendChild(dot);
      });
      mount.appendChild(bubbles);
    }

    if (showWave) {
      var wave = document.createElement("span");
      wave.className = "sf-dfy-wave";
      wave.setAttribute("aria-hidden", "true");
      mount.appendChild(wave);
    }

    mount.addEventListener("click", function () {
      mount.classList.remove("is-boop");
      void mount.offsetWidth;
      mount.classList.add("is-boop");
      window.setTimeout(function () {
        mount.classList.remove("is-boop");
      }, 480);
    });
  }

  function init() {
    var mounts = document.querySelectorAll('[data-sf-pack-plugin$=".dafeiyu_theme"]');
    mounts.forEach(enhanceMount);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
