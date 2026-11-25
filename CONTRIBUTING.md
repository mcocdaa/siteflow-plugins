# 贡献指南 (Contributing Guide)

欢迎为 **SiteFlow 官方声明式插件包（`siteflow-plugins`）** 贡献新插件、主题或改进！本文档以中文为主并附英文要点（EN Key Points），涵盖架构原则、目录与清单规范、主题扩展、本地校验与 PR/CI 流程。

> **EN Summary**: `siteflow-plugins` uses a zero-build, declarative-only Vanilla JS/CSS/SVG architecture (`schema_version: 1`). Every contribution must pass local validation (`python3 scripts/validate_pack.py` and `node --check`) and GitHub Actions CI without introducing bundlers, CDNs, symlinks, or unsafe SVG/DOM patterns.

---

## 1. 为什么采用零构建原生 JS 插件架构（Why Zero-Build Vanilla JS）

SiteFlow 的外部插件订阅系统采用 **纯声明式 + 零构建原生前端资产** 设计，刻意不引入 `package.json`、Webpack/Vite 打包链、外部 CDN 或远程服务端代码：

- **严格安全沙箱（Strict Security Sandbox）**：插件包仅允许 JSON 清单与白名单静态资源，拒绝任何 Python 模块、Jinja 模板或原始 HTML 片段，彻底杜绝远程代码执行（RCE）与模板注入。
- **开箱兼容 `BLOG_CSP`（CSP-Compliant by Default）**：所有静态脚本与样式均由 SiteFlow 同源路由 `/media/plugins/<pack_id>/<plugin_id>/<asset>?v=<sha256[:8]>` 下发，无内联 `<script>`，无第三方 CDN 请求，离线/内网环境同样稳定运行。
- **零供应链与零构建漂移（Zero Build / Supply-Chain Drift）**：仓库内的 `main.js`、`style.css` 与 `.svg` 即最终运行产物，支持在 SiteFlow 后台通过 GitHub URL 或 ZIP 压缩包一键订阅与原子同步（Atomic Sync）。
- **DOM 与无障碍安全规范（Safe DOM Authoring）**：
  - 统一使用 IIFE + `"use strict"`，避免污染全局作用域；
  - 始终通过 `[data-sf-pack-plugin$=".<id>"]` 后缀选择器查找挂载节点，确保 Fork 更换 `pack_id` 后仍可正常工作；
  - 读取 `[data-sf-pack-config]` 时使用 `try / catch` 并提供完整默认值兜底；
  - 严格使用 `document.createElement` / `document.createElementNS` / `.textContent` 构建节点，禁止 `.innerHTML`；
  - 复用 SiteFlow CSS 变量（`--bg`、`--surface`、`--border`、`--text`、`--text-muted`、`--accent`、`--font-mono`），并尊重 `@media (prefers-reduced-motion: reduce)` 与 `@media print`。

---

## 2. 插件目录结构（Directory Structure）

```text
siteflow-plugins/
├── siteflow-pack.json              # 插件包顶层清单（注册全部插件路径）
├── scripts/
│   └── validate_pack.py            # 本地与 CI 共用的全量门禁校验脚本
└── plugins/
    └── <plugin_id>/                # 目录名必须与 plugin.json 中的 id 完全一致
        ├── plugin.json             # 单插件声明式清单（schema_version: 1）
        └── assets/                 # 仅此目录内的白名单静态文件会被导入
            ├── style.css
            ├── main.js
            ├── badge-*.svg         # 可选装饰 SVG（需通过严格 SVG 安全校验）
            └── icons/
                └── *.svg           # 可选自定义图标覆盖集（配合 icon_overrides）
```

> **EN Key Points**:
> - Folder name under `plugins/` must match `^[a-z][a-z0-9_]{1,31}$` and equal `plugin.json["id"]`.
> - Only files inside `plugins/<id>/assets/` with allowlisted extensions (`.css`, `.js`, `.svg`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.woff2`, `.json`) are imported by SiteFlow.
> - No symlinks, no hidden files (`.` prefix inside `assets/`), no path traversal (`..`), and every asset file must be `<= 256 KB`.

---

## 3. `plugin.json` 清单规范（Manifest Specification）

新增插件后，务必将其路径 `plugins/<id>` 注册到根目录 `siteflow-pack.json` 的 `plugins` 数组（最多 30 个插件）。

### 必需与常用字段

| 字段 | 必填 | 约束说明 |
| :--- | :---: | :--- |
| `schema_version` | 是 | 固定整数 `1` |
| `id` | 是 | `^[a-z][a-z0-9_]{1,31}$`，与目录名一致；加载后生成 `<pack_id>.<id>` |
| `name` / `name_en` | 是 / 建议 | 1..80 字符中英文名称 |
| `description` / `description_en` | 建议 | 0..300 字符中英文简介 |
| `version` | 是 | SemVer（如 `"1.0.0"`） |
| `icon` | 否 | SiteFlow 内置 Lucide 图标名（`^[a-z0-9-]{1,32}$`，默认 `"puzzle"`） |
| `targets` | 是 | `["blog", "space", "resume"]` 的非空子集 |
| `pages` | 否 | `["list", "post", "space", "resume", "bottle"]` 的非空子集 |
| `slot` | 是 | 仅允许 `"body_start"`, `"main_start"`, `"body_end"`, `"header"`, `"aside"`, `"overlay"`, `"footer"`, `"title_deco"`, `"none"` |
| `mount` | 否 | `{"tag": "div"\|"aside"\|"section"\|"span", "class": "安全类名(<=8)", "aria_label": "<=80"}` |
| `assets` | 是 | `{"css": [...<=5], "js": [...<=5]}`，路径必须以 `assets/` 开头且文件真实存在 |
| `config_schema` | 否 | 最多 20 个配置项，支持 `select`、`text`、`textarea`、`number`、`range`、`boolean` |

---

## 4. `tokens`、`icon_overrides` 与 `title_deco` 主题扩展规范

参考 `plugins/dafeiyu_theme/plugin.json`，声明式主题插件可组合以下三项能力，无需修改任何 SiteFlow 服务端模板：

### 4.1 `tokens`（主题 CSS 变量覆盖）

- 最多声明 **30** 项，键名必须在 SiteFlow 白名单内：
  - **颜色类（Color）**：`--accent`、`--accent-soft`、`--bg`、`--surface`、`--bg-card`、`--bg-hover`、`--text`、`--text-muted`、`--muted`、`--border`、`--border-hover`（仅接受 Hex、`rgb/rgba/hsl/hsla` 或 `transparent`/`currentColor`/`white`/`black`）
  - **圆角长度类（Length）**：`--radius-card`、`--radius-btn`（仅接受 `0` 或 `px`/`rem`/`em`/`%` 数值）
  - **字体族（Font）**：`--font-family`（逗号分隔的安全字体名称）
  - **阴影（Shadow）**：`--shadow-hover`（标准偏移 + 颜色值）
- 严禁出现 `url(...)`、`var(...)`、`expression(...)`、`@import`、`javascript:`、`data:` 或分号/花括号。

### 4.2 `icon_overrides`（自定义 SVG 图标覆盖）

- 最多声明 **30** 项，键名必须属于允许覆盖的内置图标集合：
  `folder`、`layers`、`file-text`、`book-open`、`globe`、`link`、`external-link`、`mail`、`phone`、`map-pin`、`briefcase`、`graduation-cap`、`wrench`、`search`、`settings`、`pin`、`lock`、`maximize`、`printer`、`arrow-left`、`arrow-right`、`notebook-pen`。
- 值必须是本插件 `assets/` 内的 `.svg` 相对路径（如 `"assets/icons/layers.svg"`）。
- **SVG 安全红线（SVG Security Rules）**：
  - 必须为合法 UTF-8 XML，根节点为 `<svg>`（标准命名空间 `http://www.w3.org/2000/svg`），单文件 `<= 256 KB`；
  - 严禁包含 `<script>`、`<foreignObject>`、`<iframe>`、`<object>`、`<embed>`、`<style>`、`<a>`、`<use>`、`<image>`、`<animate*>`、`<!DOCTYPE>`/`<!ENTITY>`；
  - 严禁包含事件属性（`on*=`）、`style=`、`href=`、`javascript:`、`vbscript:`、`data:` 或任何外部 `http(s)://` 引用。

### 4.3 `title_deco`（标题装饰插槽）

- 将 `slot` 设为 `"title_deco"` 并声明 `mount`（推荐使用 `tag: "span"`），SiteFlow 会在空间、博客与简历主标题旁渲染标准挂载节点，并自动注入：
  - `data-sf-pack-plugin="<pack_id>.<id>"`
  - `data-sf-page="space|list|post|resume"`
  - `data-sf-asset-base="/media/plugins/<pack_id>/<id>/"`
  - `<script type="application/json" data-sf-pack-config>...</script>`
- 在 `main.js` 中拼接 `mount.dataset.sfAssetBase + "badge-whale.svg"` 即可同源加载装饰图标，并请通过 `mount.dataset.sfInit = "1"` 防止重复初始化。

---

## 5. 本地校验方法（Local Validation）

提交修改前，请在仓库根目录执行完整校验（与 CI 执行完全一致的门禁）：

```bash
# 一键运行全量校验（清单 + 字段合法性 + tokens/icon_overrides + SVG 安全 + JS 语法 + 无软链/穿越 + 256KB 上限 + ZIP 打包冒烟）
python3 scripts/validate_pack.py

# 也可单独检查全部插件 JS 语法与 JSON 格式
for f in plugins/*/assets/*.js; do node --check "$f"; done
python3 -m json.tool siteflow-pack.json > /dev/null
for f in plugins/*/plugin.json; do python3 -m json.tool "$f" > /dev/null; done
```

> **EN Key Points**: Run `python3 scripts/validate_pack.py` locally (requires Python 3.12+ and Node.js). It validates `siteflow-pack.json`, all `plugins/*/plugin.json`, `tokens` & `icon_overrides`, strict SVG sanitization rules, `node --check` on all plugin scripts, symlink/path-traversal checks, 256 KB per-asset cap, and a full GitHub-style ZIP packaging & extraction smoke test.

---

## 6. Git PR 与 CI 流程（Git PR & CI Workflow）

1. **创建特性分支（Create Branch）**：从 `main` 切出语义化分支，例如 `feat/plugin-my-widget` 或 `fix/dafeiyu-svg-padding`。
2. **同步清单与文档（Update Manifests & Docs）**：
   - 新增插件时同步更新 `siteflow-pack.json`（按需递增 `version`）以及 `README.md` / `README_CN.md` 插件列表；
   - 确保提交信息清晰（推荐使用 Conventional Commits：`feat:` / `fix:` / `chore:` / `docs:`）。
3. **本地全绿校验（Verify Locally）**：确认 `python3 scripts/validate_pack.py` 返回 `validate_pack: OK ...` 且无任何错误。
4. **发起 Pull Request 并等待 CI 全绿（Open PR & Pass CI）**：
   - GitHub Actions（`.github/workflows/ci.yml`）会在 `main` 推送与所有 `pull_request` 上自动运行 JS 语法校验与 `scripts/validate_pack.py`；
   - 如涉及视觉变化，建议在 PR 描述中附亮/暗模式截图；CI 全绿并经评审通过后即可合入 `main`。
