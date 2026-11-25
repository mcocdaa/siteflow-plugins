# SiteFlow 官方扩展插件包

[English](./README.md) | 简体中文

**SiteFlow** 官方声明式扩展插件包（`schema_version: 1`）。可在任意 SiteFlow 实例中通过 GitHub 订阅地址或离线 ZIP 一键导入，为 **博客（Blog）**、**空间（Space）** 与 **简历（Resume）** 项目提供轻量、暗黑自适应且符合 `BLOG_CSP` 的前端增强体验。

---

## 在 SiteFlow 中快速订阅

### 方式一：通过 GitHub 仓库地址订阅（推荐）

1. 在 SiteFlow 管理后台打开任意 **博客**、**空间** 或 **简历** 项目的管理页。
2. 在「扩展插件」区域展开 **「插件订阅源」** 面板。
3. 填入本仓库地址并点击 **订阅**：
   ```text
   https://github.com/mcocdaa/siteflow-plugins
   ```
4. 即可在项目扩展列表中启用并配置所需插件；后续可随时点击 **同步** 原子更新到最新版本。

### 方式二：离线 / 内网 ZIP 上传导入

1. 将本仓库打包或下载为 `.zip` 压缩包（SiteFlow 会自动剥离 GitHub 压缩包自带的顶层 `<repo>-<branch>/` 目录）。
2. 在「插件订阅源」面板点击 **上传 ZIP**（或调用 `POST /api/admin/plugin-packs/upload`）即可完成离线导入或覆盖更新。

---

## 内置展示插件一览（`pack_id: "siteflow-plugins"`）

所有外部插件包中的插件在 SiteFlow 内都会自动赋予命名空间规范 ID（`siteflow-plugins.<id>`），彻底避免与官方内置插件或其他第三方插件包产生 ID 冲突。

| 插件 ID | 规范 ID | 适用目标 | 生效页面 | 注入插槽 | 功能简介 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `reading_progress` | `siteflow-plugins.reading_progress` | `blog` | `post` | `body_start` | 博客文章顶部平滑滚动进度条，可选悬浮百分比胶囊并支持点击返回顶部。 |
| `code_copy_badge` | `siteflow-plugins.code_copy_badge` | `blog` | `post` | `body_end` | 自动为 `.post-body pre > code` 代码块添加语言标签与纯 SVG 一键复制按钮。 |
| `space_welcome_badge` | `siteflow-plugins.space_welcome_badge` | `space` | `space` | `main_start` | 在空间画廊顶部呈现极简状态胶囊、实时作品卡片计数与自定义欢迎语。 |
| `resume_print_badge` | `siteflow-plugins.resume_print_badge` | `resume` | `resume` | `main_start` | 在简历顶部展示求职意向、到岗说明与更新标记，支持控制打印/导出 PDF 时是否保留。 |
| `dafeiyu_theme` | `siteflow-plugins.dafeiyu_theme` | `space`, `blog`, `resume` | `space`, `list`, `post`, `resume` | `title_deco` | 清透深海蓝白配色 Tokens、大肥鱼风格自定义 SVG 图标集与标题旁微动效大肥鱼徽章。 |

---

## 官方内置插件 vs. 订阅插件包

SiteFlow 将 **内置官方插件**（`pack_id: "official"`，随 SiteFlow 本体内置，支持服务端模板与媒体上传等深度钩子）与 **声明式订阅插件包**（纯 JSON 清单 + 静态 CSS/JS/SVG 资源，可自由订阅、同步与批量卸载）清晰解耦：

| 类型 | 插件 ID | 适用目标 | 核心能力说明 |
| :--- | :--- | :--- | :--- |
| 内置（`official`） | `post_cover` | `blog` | 文章封面上传与展示（列表卡片 + 文章顶部插槽） |
| 内置（`official`） | `post_background` | `blog` | 博客页面氛围背景预设、自定义背景图上传、透明度与卡片玻璃质感 |
| 内置（`official`） | `mascot` | `blog`, `space` | 二次元看板娘 v2（6 款原创 SVG 皮肤、自定义头像、自由拖拽与可选流式 AI 对话） |
| 内置（`official`） | `space_banner` | `space` | 空间顶部服务端渲染公告横幅，支持色调与会话级关闭 |
| 内置（`official`） | `space_background` | `space` | 空间背景预设、自定义背景图上传与磨砂卡片模式 |
| 内置（`official`） | `resume_style` | `resume` | 简历强调色、纸张底色、版面密度、字体风格与打印安全样式 |
| 插件包（`siteflow-plugins`） | `reading_progress` | `blog` | 声明式文章滚动阅读进度条与悬浮百分比胶囊 |
| 插件包（`siteflow-plugins`） | `code_copy_badge` | `blog` | 声明式代码块语言标签与一键复制工具栏 |
| 插件包（`siteflow-plugins`） | `space_welcome_badge` | `space` | 声明式空间状态徽章栏与实时作品计数 |
| 插件包（`siteflow-plugins`） | `resume_print_badge` | `resume` | 声明式简历求职状态条与打印显隐开关 |
| 插件包（`siteflow-plugins`） | `dafeiyu_theme` | `space`, `blog`, `resume` | 声明式深海蓝白配色 Tokens、自定义 SVG 图标覆盖集与标题旁微动效大肥鱼徽章 |

---

## 仓库目录结构

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

## 清单规范（`schema_version: 1`）

### 1. 插件包清单（`siteflow-pack.json`）

| 字段 | 必填 | 校验规则 | 说明 |
| :--- | :---: | :--- | :--- |
| `schema_version` | 是 | `1` | 清单协议版本号。 |
| `id` | 是 | `^[a-z][a-z0-9-]{1,31}$`（禁止 `--`，不可为 `"official"`） | 插件包全局命名空间 ID。 |
| `name` | 是 | 字符串，1..80 字符 | 插件包中文展示名。 |
| `name_en` | 否 | 字符串，0..80 字符 | 插件包英文展示名。 |
| `description` | 否 | 字符串，0..300 字符 | 插件包中文简介。 |
| `description_en` | 否 | 字符串，0..300 字符 | 插件包英文简介。 |
| `version` | 是 | 语义化版本号（如 `"1.0.0"`） | 插件包发布版本。 |
| `author` | 否 | 字符串 | 作者或组织名称。 |
| `homepage` | 否 | `https://...` 或 `http://...` | 仓库主页或文档链接。 |
| `plugins` | 是 | 1..30 个唯一相对路径 `plugins/<id>` | 包含的插件目录列表。 |

### 2. 单插件清单（`plugins/<id>/plugin.json`）

| 字段 | 必填 | 校验规则 | 说明 |
| :--- | :---: | :--- | :--- |
| `schema_version` | 是 | `1` | 插件清单协议版本。 |
| `id` | 是 | `^[a-z][a-z0-9_]{1,31}$`，必须与目录名一致 | 插件本地 ID，加载后自动拼装为 `<pack_id>.<id>`。 |
| `name` / `name_en` | 是 / 否 | 1..80 字符 | 中英文插件名称。 |
| `description` / `description_en` | 否 | 0..300 字符 | 中英文功能简介。 |
| `version` | 是 | 语义化版本号（如 `"1.0.0"`） | 插件版本号。 |
| `icon` | 否 | SiteFlow `icons.html` 中有效的 Lucide 图标名（缺省回退为 `"puzzle"`） | 管理后台插件卡片图标。 |
| `targets` | 是 | `["blog", "space", "resume"]` 的非空子集 | 允许启用该插件的项目类型。 |
| `pages` | 否 | `["list", "post", "space", "resume"]` 的子集 | 实际渲染加载该插件的页面类型。 |
| `slot` | 是 | `"body_start" \| "main_start" \| "body_end" \| "header" \| "aside" \| "overlay" \| "footer" \| "title_deco" \| "none"` | 挂载节点插入的模板插槽位置。 |
| `assets` | 是 | `{"css": [...<=5], "js": [...<=5]}`，均位于 `assets/` 内且单文件 `<= 256 KB` | 同源下发的静态样式与延迟执行脚本。 |
| `mount` | 否 | `{"tag": "div"\|"aside"\|"section"\|"span", "class": "...", "aria_label": "<=80"}` | SiteFlow 渲染的安全声明式挂载容器。 |
| `tokens` | 否 | 不超过 30 项白名单 CSS 变量映射对象 | 经严格净化的 `:root` 主题配色与圆角变量覆盖。 |
| `icon_overrides` | 否 | 不超过 30 项白名单图标名到 `assets/*.svg` 的映射对象 | 经安全净化的自定义 SVG 图标，替换内置 Lucide 图标。 |
| `config_schema` | 否 | 不超过 20 个字段配置对象 | 用于自动生成管理后台抽屉表单与服务端校验。 |

`config_schema` 支持的字段类型：

- `select`：下拉选项，需声明 `options: [{"value": "...", "label_default": "..."}]` 与 `default`。
- `text` / `textarea`：单行或多行文本，支持 `default` 与 `max_length`。
- `number` / `range`：数值输入或滑块，支持 `default`、`min`、`max`、`step`。
- `boolean`：布尔开关，支持布尔值 `default`。

### 3. 运行时 DOM 契约

当插件包内的插件在匹配页面启用时，SiteFlow 会通过同源路由（`/media/plugins/<pack_id>/<plugin_id>/<asset>?v=<sha256[:8]>`）加载其 CSS 与 `defer` JS，并通过 `_declarative_widget.html` 渲染标准挂载容器：

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

本插件包中所有插件均遵循以下前端开发规范：

- 使用 `[data-sf-pack-plugin$=".<id>"]` 后缀选择器定位挂载容器，确保他人 Fork 并更换 `pack_id` 后依然开箱可用。
- 在 `try / catch` 中安全解析 `[data-sf-pack-config]` 并内置完整默认值兜底。
- 严格采用 `document.createElement`、`document.createElementNS` 与 `.textContent` 构建界面，杜绝 `.innerHTML`。
- 优先复用 SiteFlow CSS 变量（`--bg`、`--surface`、`--border`、`--text`、`--text-muted`、`--accent`、`--font-mono`）并提供降级色值，天然兼容亮暗主题。
- 完整尊重 `@media (prefers-reduced-motion: reduce)` 减弱动效偏好与 `@media print` 打印排版。

---

## 安全边界说明

SiteFlow 对所有外部订阅插件包强制执行 **纯声明式安全边界**：

- **零远程代码执行**：拒绝一切远程 Python 代码、不可信 Jinja 模板或原始 HTML 片段注入。
- **静态资源白名单**：导入与同步时仅复制 `plugins/<id>/assets/` 下白名单扩展名文件（`.css`、`.js`、`.svg`、`.png`、`.jpg`、`.jpeg`、`.webp`、`.gif`、`.woff2`、`.json`）。所有 `.svg` 资源在入库时经过严格净化，并附带 `Content-Security-Policy: default-src 'none'; sandbox` 与 `X-Content-Type-Options: nosniff`。
- **网络与压缩包防护**：仅允许 HTTPS 订阅并逐跳执行 SSRF 公网主机校验；强制限制压缩包 `<= 10 MB`、解压总大小 `<= 20 MB`、文件数 `<= 300`，拦截 Zip Slip 路径穿越、符号链接、加密条目与 `100:1` 以上压缩炸弹。
- **完全兼容 `BLOG_CSP`**：所有脚本与样式均由同源 `/media/plugins/` 路由下发，不依赖任何第三方 CDN，不注入内联 `<script>`。
- **一键干净卸载**：取消订阅插件包时，SiteFlow 会原子清理本地文件并批量移除各项目中对应的 `<pack_id>.*` 配置。

---

## 本地校验命令

提交修改前可通过以下命令快速校验清单与脚本语法：

```bash
python3 -m json.tool siteflow-pack.json > /dev/null
for f in plugins/*/plugin.json; do python3 -m json.tool "$f" > /dev/null; done
for f in plugins/*/assets/*.js; do node --check "$f"; done
```

---

## 开源协议

本项目基于 [MIT License](./LICENSE) 开源。
