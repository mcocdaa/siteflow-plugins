(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  var LANG_LABELS = {
    js: "JavaScript",
    javascript: "JavaScript",
    jsx: "JSX",
    ts: "TypeScript",
    typescript: "TypeScript",
    tsx: "TSX",
    py: "Python",
    python: "Python",
    sh: "Shell",
    bash: "Bash",
    zsh: "Zsh",
    shell: "Shell",
    html: "HTML",
    xml: "XML",
    css: "CSS",
    scss: "SCSS",
    json: "JSON",
    yaml: "YAML",
    yml: "YAML",
    toml: "TOML",
    md: "Markdown",
    markdown: "Markdown",
    sql: "SQL",
    go: "Go",
    rs: "Rust",
    rust: "Rust",
    c: "C",
    cpp: "C++",
    cxx: "C++",
    java: "Java",
    kt: "Kotlin",
    swift: "Swift",
    rb: "Ruby",
    php: "PHP",
    dockerfile: "Docker",
    docker: "Docker",
    diff: "Diff",
    text: "Text",
    txt: "Text",
    plaintext: "Text"
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

  function createSvgIcon(kind) {
    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "sf-code-icon sf-code-icon-" + kind);
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");

    if (kind === "copy") {
      var rect = document.createElementNS(SVG_NS, "rect");
      rect.setAttribute("x", "9");
      rect.setAttribute("y", "9");
      rect.setAttribute("width", "13");
      rect.setAttribute("height", "13");
      rect.setAttribute("rx", "2");
      rect.setAttribute("ry", "2");
      var path = document.createElementNS(SVG_NS, "path");
      path.setAttribute("d", "M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1");
      svg.appendChild(rect);
      svg.appendChild(path);
    } else {
      var check = document.createElementNS(SVG_NS, "path");
      check.setAttribute("d", "M20 6 9 17l-5-5");
      svg.appendChild(check);
    }
    return svg;
  }

  function detectLanguage(codeEl) {
    var classes = (codeEl.className || "").split(/\s+/);
    for (var i = 0; i < classes.length; i += 1) {
      var match = /^(?:language|lang)-([a-z0-9_+-]+)$/i.exec(classes[i]);
      if (match) {
        var raw = match[1].toLowerCase();
        return LANG_LABELS[raw] || raw.toUpperCase();
      }
    }
    return "";
  }

  function fallbackCopy(text) {
    return new Promise(function (resolve, reject) {
      var textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "");
      textarea.className = "sf-code-copy-fallback";
      document.body.appendChild(textarea);
      textarea.select();
      try {
        var ok = document.execCommand("copy");
        document.body.removeChild(textarea);
        if (ok) {
          resolve();
        } else {
          reject(new Error("copy_failed"));
        }
      } catch (err) {
        document.body.removeChild(textarea);
        reject(err);
      }
    });
  }

  function writeClipboard(text) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function" && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () {
        return fallbackCopy(text);
      });
    }
    return fallbackCopy(text);
  }

  function init() {
    var mount = document.querySelector('[data-sf-pack-plugin$=".code_copy_badge"]');
    if (!mount || mount.dataset.sfInit === "1") {
      return;
    }
    mount.dataset.sfInit = "1";

    var cfg = parseConfig(mount);
    var showLanguage = cfg.show_language !== false;
    var mode = cfg.button_style === "always" ? "always" : "hover";
    var copyLabel = typeof cfg.copy_label === "string" && cfg.copy_label.trim() ? cfg.copy_label.trim() : "复制";
    var copiedLabel =
      typeof cfg.copied_label === "string" && cfg.copied_label.trim() ? cfg.copied_label.trim() : "已复制";
    var resetDelay = Number(cfg.reset_delay_ms);
    if (!Number.isFinite(resetDelay) || resetDelay < 600 || resetDelay > 5000) {
      resetDelay = 1800;
    }

    var blocks = document.querySelectorAll(".post-body pre > code");
    for (var i = 0; i < blocks.length; i += 1) {
      var codeEl = blocks[i];
      var preEl = codeEl.parentElement;
      if (!preEl || preEl.dataset.sfCodeEnhanced === "1" || !preEl.parentNode) {
        continue;
      }
      preEl.dataset.sfCodeEnhanced = "1";

      var wrap = document.createElement("div");
      wrap.className = "sf-code-wrap";
      wrap.dataset.sfCcMode = mode;

      var toolbar = document.createElement("div");
      toolbar.className = "sf-code-toolbar";

      if (showLanguage) {
        var langName = detectLanguage(codeEl);
        if (langName) {
          var langSpan = document.createElement("span");
          langSpan.className = "sf-code-lang";
          langSpan.textContent = langName;
          toolbar.appendChild(langSpan);
        }
      }

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sf-code-copy-btn";
      btn.setAttribute("aria-label", copyLabel);

      var textSpan = document.createElement("span");
      textSpan.className = "sf-code-copy-label";
      textSpan.textContent = copyLabel;

      btn.appendChild(createSvgIcon("copy"));
      btn.appendChild(createSvgIcon("check"));
      btn.appendChild(textSpan);

      (function (targetCode, targetBtn, targetLabel) {
        var timerId = 0;
        targetBtn.addEventListener("click", function () {
          var content = targetCode.textContent || "";
          writeClipboard(content).then(function () {
            if (timerId) {
              window.clearTimeout(timerId);
            }
            targetBtn.classList.add("is-copied");
            targetBtn.setAttribute("aria-label", copiedLabel);
            targetLabel.textContent = copiedLabel;
            timerId = window.setTimeout(function () {
              targetBtn.classList.remove("is-copied");
              targetBtn.setAttribute("aria-label", copyLabel);
              targetLabel.textContent = copyLabel;
              timerId = 0;
            }, resetDelay);
          }).catch(function () {});
        });
      })(codeEl, btn, textSpan);

      toolbar.appendChild(btn);
      preEl.parentNode.insertBefore(wrap, preEl);
      wrap.appendChild(toolbar);
      wrap.appendChild(preEl);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
