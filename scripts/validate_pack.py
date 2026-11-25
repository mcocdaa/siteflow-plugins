import io
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

MAX_PLUGINS_PER_PACK = 30
MAX_PACK_ARCHIVE_BYTES = 10 * 1024 * 1024
MAX_PACK_EXTRACT_BYTES = 20 * 1024 * 1024
MAX_PACK_ZIP_ENTRIES = 300
MAX_EXPANSION_RATIO = 100
MAX_ASSET_FILE_BYTES = 256 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
MAX_ASSETS_PER_KIND = 5
MAX_CONFIG_FIELDS = 20
MAX_SELECT_OPTIONS = 30
MAX_THEME_TOKENS = 30
MAX_ICON_OVERRIDES = 30
MAX_SVG_ELEMENTS = 500
MAX_SVG_DEPTH = 20

ALLOWED_TARGETS = frozenset({"blog", "space", "resume"})
ALLOWED_PAGES = frozenset({"list", "post", "space", "resume", "bottle"})
ALLOWED_SLOTS = frozenset(
    {
        "body_start",
        "main_start",
        "body_end",
        "header",
        "aside",
        "overlay",
        "footer",
        "title_deco",
        "none",
    }
)
ALLOWED_MOUNT_TAGS = frozenset({"div", "aside", "section", "span"})
ALLOWED_FIELD_KINDS = frozenset({"select", "text", "textarea", "number", "range", "boolean"})
ALLOWED_ASSET_EXTS = frozenset(
    {".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".woff2", ".json"}
)
COLOR_THEME_TOKENS = frozenset(
    {
        "--accent",
        "--accent-soft",
        "--bg",
        "--surface",
        "--bg-card",
        "--bg-hover",
        "--text",
        "--text-muted",
        "--muted",
        "--border",
        "--border-hover",
    }
)
LENGTH_THEME_TOKENS = frozenset({"--radius-card", "--radius-btn"})
FONT_THEME_TOKENS = frozenset({"--font-family"})
SHADOW_THEME_TOKENS = frozenset({"--shadow-hover"})
ALLOWED_THEME_TOKENS = COLOR_THEME_TOKENS | LENGTH_THEME_TOKENS | FONT_THEME_TOKENS | SHADOW_THEME_TOKENS
ALLOWED_OVERRIDE_ICONS = frozenset(
    {
        "folder",
        "layers",
        "file-text",
        "book-open",
        "globe",
        "link",
        "external-link",
        "mail",
        "phone",
        "map-pin",
        "briefcase",
        "graduation-cap",
        "wrench",
        "search",
        "settings",
        "pin",
        "lock",
        "maximize",
        "printer",
        "arrow-left",
        "arrow-right",
        "notebook-pen",
    }
)

SVG_NS = "http://www.w3.org/2000/svg"
SVG_FORBIDDEN_TAGS = frozenset(
    {
        "script",
        "foreignobject",
        "iframe",
        "object",
        "embed",
        "audio",
        "video",
        "image",
        "use",
        "a",
        "style",
        "handler",
        "set",
    }
)

PACK_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,31}$")
EXT_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,31}$")
SEMVER_RE = re.compile(r"^[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}(?:-[a-zA-Z0-9.-]{1,32})?$")
ICON_RE = re.compile(r"^[a-z0-9-]{1,32}$")
PLUGIN_PATH_RE = re.compile(r"^plugins/([a-z][a-z0-9_]{1,31})$")
FIELD_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,39}$")
SAFE_CSS_CLASS_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,48}$")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")

CSS_FORBIDDEN_RE = re.compile(
    r"[\x00-\x1f\x7f;{}<>\\`@]|/\*|\*/|<!--|-->|"
    r"(?:url|expression|image-set|var)\s*\(|"
    r"(?:javascript|vbscript|data|behavior|-moz-binding)\s*:|@import",
    re.IGNORECASE,
)
CSS_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
CSS_FUNC_COLOR_RE = re.compile(
    r"^(?:rgb|rgba|hsl|hsla)\(\s*[0-9.]+%?(?:\s*[,/\s]\s*[0-9.]+%?){2,3}\s*\)$",
    re.IGNORECASE,
)
CSS_NAMED_COLORS = frozenset({"transparent", "currentcolor", "white", "black"})
CSS_LENGTH_RE = re.compile(r"^(?:0|[0-9]{1,3}(?:\.[0-9]{1,2})?(?:px|rem|em|%))$")
CSS_FONT_PART_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\s+[A-Za-z0-9_-]+)*$")
CSS_SHADOW_RE = re.compile(
    r"^(?:inset\s+)?(?:-?[0-9]{1,3}(?:\.[0-9]{1,2})?(?:px)?\s+){2,4}"
    r"(?:#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})|"
    r"(?:rgb|rgba|hsl|hsla)\(\s*[0-9.]+%?(?:\s*[,/\s]\s*[0-9.]+%?){2,3}\s*\))$",
    re.IGNORECASE,
)

XML_DECL_RE = re.compile(r"^\s*<\?xml(?:\s+[^?]*)?\?>", re.IGNORECASE)
SVG_FORBIDDEN_SYNTAX_RE = re.compile(
    r"<!(?:DOCTYPE|ENTITY|ELEMENT|ATTLIST|\[CDATA\[)|<\?xml-stylesheet|<\?",
    re.IGNORECASE,
)
SVG_DANGEROUS_VALUE_RE = re.compile(
    r"(?:javascript|vbscript|data|http|https)\s*:|expression\s*\(",
    re.IGNORECASE,
)
SVG_RAW_FORBIDDEN_RE = re.compile(
    r"<\s*script\b|foreignobject|\bon[a-z]+\s*=|javascript\s*:|vbscript\s*:|https?://",
    re.IGNORECASE,
)
SVG_NS_ATTR_RE = re.compile(r'\bxmlns\s*=\s*["\']http://www\.w3\.org/2000/svg["\']', re.IGNORECASE)


def _split_xml_name(tag: str) -> tuple[str, str]:
    if tag.startswith("{") and "}" in tag:
        ns, local = tag[1:].split("}", 1)
        return ns, local
    return "", tag


def _read_json(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file() or path.is_symlink():
        errors.append(f"{label}: missing regular file")
        return None
    if path.stat().st_size > MAX_MANIFEST_BYTES:
        errors.append(f"{label}: exceeds {MAX_MANIFEST_BYTES} bytes")
        return None
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{label}: invalid UTF-8 JSON ({exc})")
        return None
    if not isinstance(parsed, dict):
        errors.append(f"{label}: root must be a JSON object")
        return None
    return parsed


def _check_str(
    obj: dict[str, Any],
    key: str,
    label: str,
    errors: list[str],
    *,
    required: bool = False,
    min_len: int = 0,
    max_len: int = 200,
) -> str:
    val = obj.get(key)
    if val is None:
        if required:
            errors.append(f"{label}: missing required field {key}")
        return ""
    if not isinstance(val, str):
        errors.append(f"{label}.{key}: must be a string")
        return ""
    cleaned = val.strip()
    if len(cleaned) < min_len or len(cleaned) > max_len:
        errors.append(f"{label}.{key}: length must be {min_len}..{max_len}")
    if CONTROL_RE.search(cleaned.replace("\n", "").replace("\r", "")):
        errors.append(f"{label}.{key}: contains control characters")
    return cleaned


def _normalize_asset_rel(raw: object, expected_suffix: str, label: str, errors: list[str]) -> str | None:
    if not isinstance(raw, str):
        errors.append(f"{label}: asset path must be a string")
        return None
    stripped = raw.strip()
    if stripped.startswith(("/", "\\")) or "://" in stripped or "\x00" in stripped or ":" in stripped:
        errors.append(f"{label}: unsafe asset path {raw!r}")
        return None
    normalized = stripped.replace("\\", "/")
    if ".." in normalized.split("/"):
        errors.append(f"{label}: path traversal in asset path {raw!r}")
        return None
    if not normalized.startswith("assets/"):
        errors.append(f"{label}: asset path {raw!r} must live under assets/")
        return None
    rel_raw = normalized.removeprefix("assets/")
    parts = PurePosixPath(rel_raw).parts
    if not parts or any(part in ("", ".", "..") or part.startswith(".") for part in parts):
        errors.append(f"{label}: invalid asset path segments in {raw!r}")
        return None
    rel = PurePosixPath(*parts).as_posix()
    if not rel.lower().endswith(expected_suffix):
        errors.append(f"{label}: asset path {raw!r} must end with {expected_suffix}")
        return None
    return rel


def _validate_tokens(raw_tokens: object, label: str, errors: list[str]) -> None:
    if raw_tokens is None:
        return
    if not isinstance(raw_tokens, dict) or len(raw_tokens) > MAX_THEME_TOKENS:
        errors.append(f"{label}.tokens: must be an object with <= {MAX_THEME_TOKENS} entries")
        return
    for key, val in raw_tokens.items():
        if not isinstance(key, str) or key.strip() not in ALLOWED_THEME_TOKENS:
            errors.append(f"{label}.tokens: unsupported token key {key!r}")
            continue
        if not isinstance(val, str):
            errors.append(f"{label}.tokens.{key}: value must be a string")
            continue
        k = key.strip()
        v = val.strip()
        if not v or len(v) > 160 or CSS_FORBIDDEN_RE.search(v):
            errors.append(f"{label}.tokens.{k}: unsafe or empty CSS value {v!r}")
            continue
        if k in COLOR_THEME_TOKENS:
            if not (CSS_HEX_COLOR_RE.match(v) or CSS_FUNC_COLOR_RE.match(v) or v.lower() in CSS_NAMED_COLORS):
                errors.append(f"{label}.tokens.{k}: invalid CSS color {v!r}")
        elif k in LENGTH_THEME_TOKENS:
            if not CSS_LENGTH_RE.match(v):
                errors.append(f"{label}.tokens.{k}: invalid CSS length {v!r}")
        elif k in FONT_THEME_TOKENS:
            parts = [p.strip().strip("'\"") for p in v.split(",") if p.strip()]
            if not parts or any(not CSS_FONT_PART_RE.match(p) for p in parts):
                errors.append(f"{label}.tokens.{k}: invalid CSS font-family {v!r}")
        elif k in SHADOW_THEME_TOKENS and not CSS_SHADOW_RE.match(v):
            errors.append(f"{label}.tokens.{k}: invalid CSS box-shadow {v!r}")


def _validate_config_schema(raw_schema: object, label: str, errors: list[str]) -> None:
    if raw_schema is None:
        return
    if not isinstance(raw_schema, list) or len(raw_schema) > MAX_CONFIG_FIELDS:
        errors.append(f"{label}.config_schema: must be a list with <= {MAX_CONFIG_FIELDS} fields")
        return
    seen_keys: set[str] = set()
    for idx, item in enumerate(raw_schema):
        item_label = f"{label}.config_schema[{idx}]"
        if not isinstance(item, dict):
            errors.append(f"{item_label}: must be an object")
            continue
        key = _check_str(item, "key", item_label, errors, required=True, min_len=1, max_len=40)
        if key and (not FIELD_KEY_RE.match(key) or key in seen_keys):
            errors.append(f"{item_label}.key: invalid or duplicate key {key!r}")
        seen_keys.add(key)
        kind = _check_str(item, "kind", item_label, errors, required=True, min_len=1, max_len=20)
        if kind and kind not in ALLOWED_FIELD_KINDS:
            errors.append(f"{item_label}.kind: unsupported field kind {kind!r}")
        label_key = "label_default" if "label_default" in item else "label"
        _check_str(item, label_key, item_label, errors, required=True, min_len=1, max_len=80)
        if kind == "select":
            raw_opts = item.get("options")
            if not isinstance(raw_opts, list) or not (1 <= len(raw_opts) <= MAX_SELECT_OPTIONS):
                errors.append(f"{item_label}.options: must have 1..{MAX_SELECT_OPTIONS} options")
                continue
            seen_vals: set[str] = set()
            for opt_idx, opt in enumerate(raw_opts):
                opt_label = f"{item_label}.options[{opt_idx}]"
                if not isinstance(opt, dict):
                    errors.append(f"{opt_label}: must be an object")
                    continue
                val = _check_str(opt, "value", opt_label, errors, required=True, min_len=1, max_len=60)
                if val in seen_vals:
                    errors.append(f"{opt_label}.value: duplicate option value {val!r}")
                seen_vals.add(val)
                ol_key = "label_default" if "label_default" in opt else "label"
                _check_str(opt, ol_key, opt_label, errors, required=True, min_len=1, max_len=80)
            default_val = item.get("default")
            if default_val is not None and default_val not in seen_vals:
                errors.append(f"{item_label}.default: {default_val!r} not in select options")
        elif kind in ("text", "textarea"):
            max_len = item.get("max_length")
            if max_len is not None and (
                isinstance(max_len, bool) or not isinstance(max_len, int) or max_len < 1
            ):
                errors.append(f"{item_label}.max_length: must be a positive integer")
        elif kind in ("number", "range"):
            raw_min = item.get("min_value", item.get("min"))
            raw_max = item.get("max_value", item.get("max"))
            raw_step = item.get("step")
            for bound_name, bound_val in (("min", raw_min), ("max", raw_max)):
                if bound_val is not None and (
                    isinstance(bound_val, bool) or not isinstance(bound_val, (int, float))
                ):
                    errors.append(f"{item_label}.{bound_name}: must be a number")
            if (
                isinstance(raw_min, (int, float))
                and not isinstance(raw_min, bool)
                and isinstance(raw_max, (int, float))
                and not isinstance(raw_max, bool)
                and raw_min > raw_max
            ):
                errors.append(f"{item_label}: min cannot exceed max")
            if raw_step is not None and (
                isinstance(raw_step, bool) or not isinstance(raw_step, (int, float)) or raw_step <= 0
            ):
                errors.append(f"{item_label}.step: must be a positive number")


def validate_svg_file(svg_path: Path, rel_label: str, errors: list[str]) -> None:
    raw = svg_path.read_bytes()
    if not raw or len(raw) > MAX_ASSET_FILE_BYTES:
        errors.append(f"{rel_label}: SVG empty or exceeds {MAX_ASSET_FILE_BYTES} bytes")
        return
    if b"\x00" in raw:
        errors.append(f"{rel_label}: SVG contains null byte")
        return
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{rel_label}: SVG invalid UTF-8 ({exc})")
        return

    cleaned = XML_DECL_RE.sub("", text.removeprefix("\ufeff"), count=1).strip()
    if not cleaned:
        errors.append(f"{rel_label}: SVG content is empty")
        return
    if SVG_FORBIDDEN_SYNTAX_RE.search(cleaned):
        errors.append(f"{rel_label}: SVG contains forbidden XML declaration or processing instruction")

    scrubbed = SVG_NS_ATTR_RE.sub("", cleaned)
    raw_match = SVG_RAW_FORBIDDEN_RE.search(scrubbed)
    if raw_match:
        errors.append(f"{rel_label}: SVG contains forbidden pattern {raw_match.group(0)!r}")

    try:
        root = ET.fromstring(cleaned)
    except ET.ParseError as exc:
        errors.append(f"{rel_label}: invalid SVG XML ({exc})")
        return

    root_ns, root_local = _split_xml_name(root.tag)
    if root_ns not in ("", SVG_NS) or root_local.lower() != "svg":
        errors.append(f"{rel_label}: root element must be <svg>")
        return

    element_count = 0

    def walk(node: ET.Element, depth: int) -> None:
        nonlocal element_count
        if depth > MAX_SVG_DEPTH:
            errors.append(f"{rel_label}: SVG nesting exceeds {MAX_SVG_DEPTH}")
            return
        ns, local = _split_xml_name(node.tag)
        lowered = local.lower()
        if lowered in SVG_FORBIDDEN_TAGS or lowered.startswith("animate"):
            errors.append(f"{rel_label}: forbidden SVG element <{local}>")
        if ns not in ("", SVG_NS):
            errors.append(f"{rel_label}: unsupported XML namespace {ns!r}")
        element_count += 1
        if element_count > MAX_SVG_ELEMENTS:
            errors.append(f"{rel_label}: SVG element count exceeds {MAX_SVG_ELEMENTS}")
            return
        for attr_key, attr_val in node.attrib.items():
            _, attr_local = _split_xml_name(attr_key)
            attr_lower = attr_local.lower()
            if attr_lower.startswith("on") or attr_lower in ("style", "href"):
                errors.append(f"{rel_label}: forbidden SVG attribute {attr_local!r}")
            compact = re.sub(r"[\x00-\x20\x7f]+", "", attr_val)
            if SVG_DANGEROUS_VALUE_RE.search(compact):
                errors.append(f"{rel_label}: dangerous SVG attribute value in {attr_local!r}")
        for child in node:
            walk(child, depth + 1)

    walk(root, 0)


def check_repo_tree(root: Path, errors: list[str]) -> list[Path]:
    root_resolved = root.resolve()
    files: list[Path] = []
    for candidate in sorted(root.rglob("*")):
        rel = candidate.relative_to(root)
        if ".git" in rel.parts:
            continue
        if candidate.is_symlink():
            errors.append(f"symlink not allowed: {rel.as_posix()}")
            continue
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root_resolved):
            errors.append(f"path escapes repository root: {rel.as_posix()}")
            continue
        if candidate.is_file():
            files.append(candidate)
    return files


def validate_pack(root: Path, errors: list[str]) -> tuple[list[str], int, int]:
    pack_manifest = _read_json(root / "siteflow-pack.json", "siteflow-pack.json", errors)
    if pack_manifest is None:
        return [], 0, 0

    schema_version = pack_manifest.get("schema_version")
    if type(schema_version) is not int or schema_version != 1:
        errors.append("siteflow-pack.json.schema_version: must be integer 1")

    pack_id = _check_str(
        pack_manifest, "id", "siteflow-pack.json", errors, required=True, min_len=2, max_len=32
    )
    if pack_id and (pack_id == "official" or "--" in pack_id or not PACK_ID_RE.match(pack_id)):
        errors.append(f"siteflow-pack.json.id: invalid pack id {pack_id!r}")

    _check_str(pack_manifest, "name", "siteflow-pack.json", errors, required=True, min_len=1, max_len=80)
    _check_str(pack_manifest, "name_en", "siteflow-pack.json", errors, max_len=80)
    _check_str(pack_manifest, "description", "siteflow-pack.json", errors, max_len=300)
    _check_str(pack_manifest, "description_en", "siteflow-pack.json", errors, max_len=300)
    _check_str(pack_manifest, "author", "siteflow-pack.json", errors, max_len=80)

    pack_version = _check_str(
        pack_manifest, "version", "siteflow-pack.json", errors, required=True, min_len=1, max_len=40
    )
    if pack_version and not SEMVER_RE.match(pack_version):
        errors.append(f"siteflow-pack.json.version: invalid semver {pack_version!r}")

    homepage = _check_str(pack_manifest, "homepage", "siteflow-pack.json", errors, max_len=300)
    if homepage:
        parsed_hp = urlparse(homepage)
        if parsed_hp.scheme.lower() not in ("http", "https") or not parsed_hp.hostname:
            errors.append(f"siteflow-pack.json.homepage: must be http(s):// URL ({homepage!r})")

    raw_plugins = pack_manifest.get("plugins")
    if not isinstance(raw_plugins, list) or not (1 <= len(raw_plugins) <= MAX_PLUGINS_PER_PACK):
        errors.append(f"siteflow-pack.json.plugins: must list 1..{MAX_PLUGINS_PER_PACK} plugins")
        return [], 0, 0

    declared_ids: list[str] = []
    seen_ids: set[str] = set()
    for rel in raw_plugins:
        if not isinstance(rel, str):
            errors.append("siteflow-pack.json.plugins: entry must be a string")
            continue
        match = PLUGIN_PATH_RE.match(rel.strip().replace("\\", "/"))
        if not match:
            errors.append(f"siteflow-pack.json.plugins: invalid path {rel!r}")
            continue
        local_id = match.group(1)
        if local_id in seen_ids:
            errors.append(f"siteflow-pack.json.plugins: duplicate plugin {local_id!r}")
            continue
        seen_ids.add(local_id)
        declared_ids.append(local_id)

    plugins_root = root / "plugins"
    if plugins_root.is_dir():
        disk_ids = sorted(
            entry.name
            for entry in plugins_root.iterdir()
            if entry.is_dir() and not entry.name.startswith(".")
        )
        undeclared = sorted(set(disk_ids) - seen_ids)
        if undeclared:
            errors.append(f"siteflow-pack.json.plugins missing plugin directories: {', '.join(undeclared)}")

    total_assets = 0
    total_svgs = 0
    for local_id in declared_ids:
        plugin_dir = root / "plugins" / local_id
        if not plugin_dir.is_dir():
            errors.append(f"plugins/{local_id}: directory does not exist")
            continue
        label = f"plugins/{local_id}/plugin.json"
        manifest = _read_json(plugin_dir / "plugin.json", label, errors)
        if manifest is None:
            continue

        p_schema = manifest.get("schema_version")
        if type(p_schema) is not int or p_schema != 1:
            errors.append(f"{label}.schema_version: must be integer 1")

        p_id = _check_str(manifest, "id", label, errors, required=True, min_len=2, max_len=32)
        if p_id and (not EXT_ID_RE.match(p_id) or p_id != local_id):
            errors.append(f"{label}.id: must match directory name {local_id!r}")

        _check_str(manifest, "name", label, errors, required=True, min_len=1, max_len=80)
        _check_str(manifest, "name_en", label, errors, max_len=80)
        _check_str(manifest, "description", label, errors, max_len=300)
        _check_str(manifest, "description_en", label, errors, max_len=300)

        p_ver = _check_str(manifest, "version", label, errors, required=True, min_len=1, max_len=40)
        if p_ver and not SEMVER_RE.match(p_ver):
            errors.append(f"{label}.version: invalid semver {p_ver!r}")

        icon = _check_str(manifest, "icon", label, errors, max_len=32)
        if icon and not ICON_RE.match(icon):
            errors.append(f"{label}.icon: invalid icon key {icon!r}")

        raw_targets = manifest.get("targets")
        if not isinstance(raw_targets, list) or not raw_targets:
            errors.append(f"{label}.targets: must be a non-empty list")
        else:
            for t in raw_targets:
                if not isinstance(t, str) or t not in ALLOWED_TARGETS:
                    errors.append(f"{label}.targets: invalid target {t!r}")

        raw_pages = manifest.get("pages")
        if raw_pages is not None:
            if not isinstance(raw_pages, list) or not raw_pages:
                errors.append(f"{label}.pages: must be a non-empty list when present")
            else:
                for p in raw_pages:
                    if not isinstance(p, str) or p not in ALLOWED_PAGES:
                        errors.append(f"{label}.pages: invalid page {p!r}")

        slot = manifest.get("slot")
        if not isinstance(slot, str) or slot not in ALLOWED_SLOTS:
            errors.append(f"{label}.slot: invalid or missing slot {slot!r}")

        raw_mount = manifest.get("mount")
        if raw_mount is not None:
            if not isinstance(raw_mount, dict):
                errors.append(f"{label}.mount: must be an object")
            else:
                tag = _check_str(raw_mount, "tag", f"{label}.mount", errors, max_len=20) or "div"
                if tag not in ALLOWED_MOUNT_TAGS:
                    errors.append(f"{label}.mount.tag: unsupported tag {tag!r}")
                raw_cls = _check_str(raw_mount, "class", f"{label}.mount", errors, max_len=200)
                if raw_cls:
                    tokens = raw_cls.split()
                    if len(tokens) > 8:
                        errors.append(f"{label}.mount.class: exceeds 8 CSS classes")
                    for token in tokens:
                        if not SAFE_CSS_CLASS_RE.match(token):
                            errors.append(f"{label}.mount.class: invalid class token {token!r}")
                _check_str(raw_mount, "aria_label", f"{label}.mount", errors, max_len=80)

        _validate_tokens(manifest.get("tokens"), label, errors)
        _validate_config_schema(manifest.get("config_schema"), label, errors)

        declared_asset_rels: list[str] = []
        raw_overrides = manifest.get("icon_overrides")
        if raw_overrides is not None:
            if not isinstance(raw_overrides, dict) or len(raw_overrides) > MAX_ICON_OVERRIDES:
                errors.append(f"{label}.icon_overrides: must be an object with <= {MAX_ICON_OVERRIDES} items")
            else:
                for icon_key, icon_path in raw_overrides.items():
                    if not isinstance(icon_key, str) or icon_key.strip() not in ALLOWED_OVERRIDE_ICONS:
                        errors.append(f"{label}.icon_overrides: unsupported icon key {icon_key!r}")
                    rel_svg = _normalize_asset_rel(
                        icon_path, ".svg", f"{label}.icon_overrides.{icon_key}", errors
                    )
                    if rel_svg is not None:
                        declared_asset_rels.append(rel_svg)

        raw_assets = manifest.get("assets")
        if not isinstance(raw_assets, dict):
            errors.append(f"{label}.assets: must be an object")
        else:
            for kind, ext in (("css", ".css"), ("js", ".js")):
                items = raw_assets.get(kind, [])
                if not isinstance(items, list) or len(items) > MAX_ASSETS_PER_KIND:
                    errors.append(
                        f"{label}.assets.{kind}: must be a list with <= {MAX_ASSETS_PER_KIND} entries"
                    )
                    continue
                for entry in items:
                    rel_asset = _normalize_asset_rel(entry, ext, f"{label}.assets.{kind}", errors)
                    if rel_asset is not None:
                        declared_asset_rels.append(rel_asset)

        assets_dir = plugin_dir / "assets"
        existing_assets: set[str] = set()
        if assets_dir.exists():
            if assets_dir.is_symlink() or not assets_dir.is_dir():
                errors.append(f"plugins/{local_id}/assets: must be a regular directory")
            else:
                for item in sorted(assets_dir.rglob("*")):
                    rel_item = item.relative_to(assets_dir)
                    rel_posix = rel_item.as_posix()
                    full_label = f"plugins/{local_id}/assets/{rel_posix}"
                    if any(part.startswith(".") for part in rel_item.parts):
                        errors.append(f"{full_label}: hidden asset path not allowed")
                        continue
                    if item.is_dir():
                        continue
                    total_assets += 1
                    existing_assets.add(rel_posix)
                    suffix = item.suffix.lower()
                    if suffix not in ALLOWED_ASSET_EXTS:
                        errors.append(f"{full_label}: disallowed asset extension {suffix or item.name!r}")
                    size = item.stat().st_size
                    if size == 0 or size > MAX_ASSET_FILE_BYTES:
                        errors.append(f"{full_label}: size {size} bytes must be 1..{MAX_ASSET_FILE_BYTES}")
                    if suffix == ".svg":
                        total_svgs += 1
                        validate_svg_file(item, full_label, errors)

        for rel_asset in declared_asset_rels:
            if rel_asset not in existing_assets:
                errors.append(f"{label}: declared asset not found: assets/{rel_asset}")

    return declared_ids, total_assets, total_svgs


def check_all_js_syntax(root: Path, errors: list[str]) -> int:
    js_files = sorted((root / "plugins").glob("*/assets/*.js"))
    if not js_files:
        errors.append("no plugin JS files found under plugins/*/assets/*.js")
        return 0
    node_bin = shutil.which("node")
    if node_bin is None:
        errors.append("node executable not found on PATH for JS syntax check")
        return 0
    for js_file in js_files:
        proc = subprocess.run(
            [node_bin, "--check", str(js_file)], capture_output=True, text=True, check=False
        )
        if proc.returncode != 0:
            rel = js_file.relative_to(root).as_posix()
            detail = (proc.stderr or proc.stdout).strip()
            errors.append(f"{rel}: node --check failed ({detail})")
    return len(js_files)


def check_zip_smoke(root: Path, files: list[Path], declared_ids: list[str], errors: list[str]) -> int:
    prefix = "siteflow-plugins-main/"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            rel = file_path.relative_to(root).as_posix()
            zf.writestr(f"{prefix}{rel}", file_path.read_bytes())

    archive_bytes = buf.getvalue()
    if len(archive_bytes) > MAX_PACK_ARCHIVE_BYTES:
        errors.append(f"ZIP smoke: archive size {len(archive_bytes)} exceeds {MAX_PACK_ARCHIVE_BYTES}")
        return len(archive_bytes)

    with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as zf:
        infos = zf.infolist()
        if len(infos) > MAX_PACK_ZIP_ENTRIES:
            errors.append(f"ZIP smoke: entry count {len(infos)} exceeds {MAX_PACK_ZIP_ENTRIES}")
        total_uncompressed = 0
        for info in infos:
            if info.flag_bits & 0x1:
                errors.append(f"ZIP smoke: encrypted entry {info.filename!r}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                errors.append(f"ZIP smoke: symlink entry {info.filename!r}")
            name = info.filename
            if name.startswith("/") or "\\" in name or ".." in PurePosixPath(name).parts:
                errors.append(f"ZIP smoke: unsafe entry path {name!r}")
            total_uncompressed += info.file_size
        if total_uncompressed > MAX_PACK_EXTRACT_BYTES:
            errors.append(
                f"ZIP smoke: uncompressed size {total_uncompressed} exceeds {MAX_PACK_EXTRACT_BYTES}"
            )
        compressed_base = max(len(archive_bytes), 1)
        if total_uncompressed / compressed_base > MAX_EXPANSION_RATIO:
            errors.append("ZIP smoke: expansion ratio exceeds limit")

        with tempfile.TemporaryDirectory(prefix="sf-pack-smoke-") as tmp_dir:
            tmp_root = Path(tmp_dir)
            zf.extractall(tmp_root)
            unpacked_root = tmp_root / "siteflow-plugins-main"
            if not (unpacked_root / "siteflow-pack.json").is_file():
                errors.append("ZIP smoke: unpacked siteflow-pack.json missing")
            for local_id in declared_ids:
                if not (unpacked_root / "plugins" / local_id / "plugin.json").is_file():
                    errors.append(f"ZIP smoke: unpacked plugins/{local_id}/plugin.json missing")
    return len(archive_bytes)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors: list[str] = []

    repo_files = check_repo_tree(root, errors)
    for file_path in repo_files:
        if file_path.suffix.lower() == ".svg" and "plugins" not in file_path.relative_to(root).parts[:1]:
            validate_svg_file(file_path, file_path.relative_to(root).as_posix(), errors)

    declared_ids, asset_count, svg_count = validate_pack(root, errors)
    js_count = check_all_js_syntax(root, errors)
    zip_size = check_zip_smoke(root, repo_files, declared_ids, errors)

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(
        f"validate_pack: OK (plugins={len(declared_ids)}, assets={asset_count}, "
        f"js={js_count}, svgs={svg_count}, zip={zip_size} bytes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
