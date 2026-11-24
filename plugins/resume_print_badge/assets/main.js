(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  var STATUS_DEFAULTS = {
    open: "正在看新机会",
    consulting: "开放顾问 / 合作",
    passive: "暂不求职，欢迎交流",
    custom: "开放交流"
  };

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

  function buildStatusIcon(state) {
    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "sf-rpb-icon");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");

    if (state === "open") {
      var circle = document.createElementNS(SVG_NS, "circle");
      circle.setAttribute("cx", "12");
      circle.setAttribute("cy", "12");
      circle.setAttribute("r", "9");
      var check = document.createElementNS(SVG_NS, "path");
      check.setAttribute("d", "m9 12 2 2 4-4");
      svg.appendChild(circle);
      svg.appendChild(check);
    } else if (state === "consulting") {
      var rect = document.createElementNS(SVG_NS, "rect");
      rect.setAttribute("x", "2");
      rect.setAttribute("y", "7");
      rect.setAttribute("width", "20");
      rect.setAttribute("height", "14");
      rect.setAttribute("rx", "2");
      var handle = document.createElementNS(SVG_NS, "path");
      handle.setAttribute("d", "M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16");
      svg.appendChild(rect);
      svg.appendChild(handle);
    } else {
      var outer = document.createElementNS(SVG_NS, "circle");
      outer.setAttribute("cx", "12");
      outer.setAttribute("cy", "12");
      outer.setAttribute("r", "9");
      var inner = document.createElementNS(SVG_NS, "circle");
      inner.setAttribute("cx", "12");
      inner.setAttribute("cy", "12");
      inner.setAttribute("r", "3");
      inner.setAttribute("fill", "currentColor");
      svg.appendChild(outer);
      svg.appendChild(inner);
    }
    return svg;
  }

  function init() {
    var mount = document.querySelector('[data-sf-pack-plugin$=".resume_print_badge"]');
    if (!mount || mount.dataset.sfInit === "1") {
      return;
    }
    mount.dataset.sfInit = "1";

    var cfg = parseConfig(mount);
    var availability = Object.prototype.hasOwnProperty.call(STATUS_DEFAULTS, cfg.availability)
      ? cfg.availability
      : "open";
    var customLabel = typeof cfg.custom_label === "string" ? cfg.custom_label.trim() : "";
    var label =
      availability === "custom"
        ? customLabel || STATUS_DEFAULTS.custom
        : STATUS_DEFAULTS[availability];
    var note = typeof cfg.note === "string" ? cfg.note.trim() : "";
    var updatedTag = typeof cfg.updated_tag === "string" ? cfg.updated_tag.trim() : "";
    var showInPrint = cfg.show_in_print === true;

    if (!label && !note && !updatedTag) {
      mount.hidden = true;
      return;
    }

    mount.dataset.sfRpbState = availability;
    mount.classList.toggle("sf-rpb-show-print", showInPrint);
    mount.classList.toggle("sf-rpb-hide-print", !showInPrint);

    var lead = document.createElement("div");
    lead.className = "sf-rpb-lead";

    var statusEl = document.createElement("span");
    statusEl.className = "sf-rpb-status";
    statusEl.appendChild(buildStatusIcon(availability));

    var labelEl = document.createElement("span");
    labelEl.textContent = label;
    statusEl.appendChild(labelEl);
    lead.appendChild(statusEl);

    if (note) {
      var noteEl = document.createElement("p");
      noteEl.className = "sf-rpb-note";
      noteEl.textContent = note;
      lead.appendChild(noteEl);
    }

    mount.appendChild(lead);

    if (updatedTag) {
      var tagEl = document.createElement("span");
      tagEl.className = "sf-rpb-updated";
      tagEl.textContent = updatedTag;
      mount.appendChild(tagEl);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
