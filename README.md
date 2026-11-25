# SiteFlow Official Plugin Pack

English | [简体中文](./README_CN.md)

The official declarative extension plugin pack (`schema_version: 1`) for **SiteFlow**. Subscribe to this repository directly inside any SiteFlow instance to install lightweight, CSP-compliant frontend plugins spanning **Blog**, **Space**, and **Resume** projects.

---

## Quick Subscribe in SiteFlow

### Option 1: Subscribe via GitHub URL (Recommended)

1. Open any **Blog**, **Space**, or **Resume** admin page in SiteFlow.
2. Expand **Plugin Subscriptions (插件订阅源)** inside the Extensions section.
3. Paste the repository URL and click **Subscribe**:
   ```text
   https://github.com/mcocdaa/siteflow-plugins
   ```
4. Enable and configure any plugin per project. Use **Sync** at any time to pull the latest release atomically.

### Option 2: Offline / Airgapped ZIP Upload

1. Download or package this repository as a `.zip` archive (GitHub's single top-level `<repo>-<branch>/` wrapper is unwrapped automatically).
2. Upload the `.zip` archive via **Upload ZIP** in the Plugin Subscriptions panel (or `POST /api/admin/plugin-packs/upload`).

---

## Included Pack Plugins (`pack_id: "siteflow-plugins"`)

Every plugin from an external pack receives a namespaced canonical ID (`siteflow-plugins.<id>`), preventing collisions with built-in plugins or other subscribed packs.

| Plugin ID | Canonical ID | Target | Pages | Slot | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `reading_progress` | `siteflow-plugins.reading_progress` | `blog` | `post` | `body_start` | Smooth top scroll progress rail with optional floating percentage pill and back-to-top click action. |
| `code_copy_badge` | `siteflow-plugins.code_copy_badge` | `blog` | `post` | `body_end` | Enhances `.post-body pre > code` blocks with a language chip and one-click SVG copy toolbar. |
| `space_welcome_badge` | `siteflow-plugins.space_welcome_badge` | `space` | `space` | `main_start` | Editorial status pill bar above the space gallery with live project card count and optional tagline. |
| `resume_print_badge` | `siteflow-plugins.resume_print_badge` | `resume` | `resume` | `main_start` | Clean availability status ribbon for resumes with configurable `@media print` / PDF visibility. |
| `dafeiyu_theme` | `siteflow-plugins.dafeiyu_theme` | `space`, `blog`, `resume` | `space`, `list`, `post`, `resume` | `title_deco` | Breezy ocean blue-and-white theme tokens, custom DaFeiYu-inspired SVG icon overrides, and a gentle animated title whale badge. |

---

## Built-In Official Plugins vs. Pack Plugins

SiteFlow separates **built-in official plugins** (`pack_id: "official"`, bundled directly in SiteFlow with deeper server-side hooks) from **declarative plugin packs** (pure JSON + static CSS/JS/SVG assets subscribed from GitHub or ZIP archives):

| Category | Plugin ID | Targets | Scope & Capabilities |
| :--- | :--- | :--- | :--- |
| Built-in (`official`) | `post_cover` | `blog` | Article cover image upload, list card & post header slots |
| Built-in (`official`) | `post_background` | `blog` | Atmospheric blog background presets, custom image upload, opacity & card surface controls |
| Built-in (`official`) | `mascot` | `blog`, `space` | Interactive chibi SVG mascot (v2), custom avatar upload, free dragging & optional streaming AI chat |
| Built-in (`official`) | `space_banner` | `space` | Server-rendered dismissible announcement banner at the top of a space |
| Built-in (`official`) | `space_background` | `space` | Space background presets, custom wallpaper upload & frosted card surface mode |
| Built-in (`official`) | `resume_style` | `resume` | Accent palette, paper tone, density, typography & print-safe styling presets |
| Pack (`siteflow-plugins`) | `reading_progress` | `blog` | Declarative client-side scroll progress rail & percentage pill |
| Pack (`siteflow-plugins`) | `code_copy_badge` | `blog` | Declarative code block toolbar with language chip & clipboard copy |
| Pack (`siteflow-plugins`) | `space_welcome_badge` | `space` | Declarative space status bar & live gallery card counter |
| Pack (`siteflow-plugins`) | `resume_print_badge` | `resume` | Declarative resume availability ribbon with print visibility switch |
| Pack (`siteflow-plugins`) | `dafeiyu_theme` | `space`, `blog`, `resume` | Declarative deep-sea theme tokens, custom SVG icon set & animated title whale badge |

---

## Repository Structure

```text
siteflow-plugins/
├── LICENSE
├── README.md
├── README_CN.md
├── siteflow-pack.json
└── plugins/
    ├── reading_progress/
    │   ├── plugin.json
    │   └── assets/
    │       ├── style.css
    │       └── main.js
    ├── code_copy_badge/
    │   ├── plugin.json
    │   └── assets/
    │       ├── style.css
    │       └── main.js
    ├── space_welcome_badge/
    │   ├── plugin.json
    │   └── assets/
    │       ├── style.css
    │       └── main.js
    ├── resume_print_badge/
    │   ├── plugin.json
    │   └── assets/
    │       ├── style.css
    │       └── main.js
    └── dafeiyu_theme/
        ├── plugin.json
        └── assets/
            ├── style.css
            ├── main.js
            ├── badge-whale.svg
            └── icons/
                ├── book-open.svg
                ├── file-text.svg
                ├── folder.svg
                ├── globe.svg
                ├── layers.svg
                ├── link.svg
                └── mail.svg
```

---

## Manifest Schema (`schema_version: 1`)

### 1. Pack Manifest (`siteflow-pack.json`)

| Field | Required | Constraints | Description |
| :--- | :---: | :--- | :--- |
| `schema_version` | Yes | `1` | Manifest schema version. |
| `id` | Yes | `^[a-z][a-z0-9-]{1,31}$` (no `--`, cannot be `"official"`) | Unique pack namespace prefix. |
| `name` | Yes | String, 1..80 chars | Primary pack display name (Chinese). |
| `name_en` | No | String, 0..80 chars | Optional English pack display name. |
| `description` | No | String, 0..300 chars | Primary pack description. |
| `description_en` | No | String, 0..300 chars | Optional English description. |
| `version` | Yes | Semver (e.g. `"1.0.0"`) | Pack release version. |
| `author` | No | String | Author or organization name. |
| `homepage` | No | `https://...` or `http://...` | Repository or documentation URL. |
| `plugins` | Yes | Array of 1..30 unique `plugins/<id>` paths | Relative directories of included plugins. |

### 2. Plugin Manifest (`plugins/<id>/plugin.json`)

| Field | Required | Constraints | Description |
| :--- | :---: | :--- | :--- |
| `schema_version` | Yes | `1` | Plugin manifest schema version. |
| `id` | Yes | `^[a-z][a-z0-9_]{1,31}$`, must match folder name | Local plugin ID; becomes `<pack_id>.<id>`. |
| `name` / `name_en` | Yes / No | 1..80 chars | Localized display names. |
| `description` / `description_en` | No | 0..300 chars | Localized short summaries. |
| `version` | Yes | Semver (e.g. `"1.0.0"`) | Plugin version. |
| `icon` | No | Lucide icon key in SiteFlow `icons.html` (falls back to `"puzzle"`) | Card icon in the admin UI. |
| `targets` | Yes | Non-empty subset of `["blog", "space", "resume"]` | Project types where this plugin can be enabled. |
| `pages` | No | Subset of `["list", "post", "space", "resume"]` | Specific rendered pages where assets/mount load. |
| `slot` | Yes | `"body_start" \| "main_start" \| "body_end" \| "header" \| "aside" \| "overlay" \| "footer" \| "title_deco" \| "none"` | Template injection slot for the mount element. |
| `assets` | Yes | `{"css": [...<=5], "js": [...<=5]}` under `assets/`, each `<= 256 KB` | Static stylesheets and deferred scripts served same-origin. |
| `mount` | No | `{"tag": "div"\|"aside"\|"section"\|"span", "class": "...", "aria_label": "<=80"}` | Safe declarative mount element rendered by SiteFlow. |
| `tokens` | No | Object of `<= 30` allowlisted CSS custom properties | Safe `:root` theme token overrides (strictly sanitized). |
| `icon_overrides` | No | Object of `<= 30` allowlisted icon keys mapped to `assets/*.svg` | Custom sanitized SVG icons replacing built-in Lucide icons. |
| `config_schema` | No | Array of `<= 20` field objects | Generates the admin drawer form and server-side validation. |

Supported `config_schema` field kinds:

- `select`: requires `options: [{"value": "...", "label_default": "..."}]` and `default`.
- `text` / `textarea`: supports `default` and `max_length`.
- `number` / `range`: supports `default`, `min`, `max`, and `step`.
- `boolean`: supports boolean `default`.

### 3. Runtime DOM Contract

When a pack plugin is enabled on a matching page, SiteFlow injects its CSS and deferred JS from same-origin URLs (`/media/plugins/<pack_id>/<plugin_id>/<asset>?v=<sha256[:8]>`) and renders a safe mount container via `_declarative_widget.html`:

```html
<div class="sf-pack-mount sf-ext-reading-progress"
     data-sf-pack-plugin="siteflow-plugins.reading_progress"
     data-sf-page="post"
     data-sf-project-slug="my-blog"
     data-sf-asset-base="/media/plugins/siteflow-plugins/reading_progress/"
     aria-label="阅读进度">
  <script type="application/json" data-sf-pack-config>{"height_px":3,"color_style":"accent"}</script>
</div>
```

Authoring best practices used across all plugins in this pack:

- Query mounts with `[data-sf-pack-plugin$=".<id>"]` so forks under a custom `pack_id` work without code changes.
- Parse `[data-sf-pack-config]` inside `try / catch` with defensive defaults.
- Build DOM strictly with `document.createElement`, `document.createElementNS`, and `.textContent` (never `.innerHTML`).
- Style against SiteFlow CSS custom properties (`--bg`, `--surface`, `--border`, `--text`, `--text-muted`, `--accent`, `--font-mono`) with crisp light/dark fallbacks.
- Respect `@media (prefers-reduced-motion: reduce)` and `@media print`.

---

## Security Model

SiteFlow enforces a strict **declarative-only** sandbox for external plugin packs:

- **Zero remote code execution**: No Python modules, no Jinja templates, and no raw HTML fragments are accepted or executed from packs.
- **Allowlisted static assets only**: Only `.css`, `.js`, `.svg`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.woff2`, and `.json` files inside `plugins/<id>/assets/` are copied on import/sync. All `.svg` assets are sanitized on import and served with `Content-Security-Policy: default-src 'none'; sandbox` and `X-Content-Type-Options: nosniff`.
- **Network & archive hardening**: HTTPS-only downloads with SSRF host validation on every redirect hop, 10 MB archive cap, 20 MB extracted size cap, 300-entry cap, and full Zip-Slip / symlink / encrypted-entry / 100:1 zip-bomb rejection.
- **CSP compliance**: All assets are served same-origin and comply with SiteFlow's `BLOG_CSP` (`script-src 'self'`, `default-src 'self'`).
- **Clean uninstallation**: Deleting a subscribed pack atomically removes its files and strips every `<pack_id>.*` entry from all projects.

---

## Local Validation

Validate manifests and scripts locally before submitting changes:

```bash
python3 -m json.tool siteflow-pack.json > /dev/null
for f in plugins/*/plugin.json; do python3 -m json.tool "$f" > /dev/null; done
for f in plugins/*/assets/*.js; do node --check "$f"; done
```

---

## License

Released under the [MIT License](./LICENSE).
