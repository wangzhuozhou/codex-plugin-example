#!/usr/bin/env python3
"""Validate the example Codex plugin using only the Python standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_INSTALLATION = {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}
VALID_AUTHENTICATION = {"ON_INSTALL", "ON_USE"}


def fail(message: str) -> None:
    print(f"Validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing file: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected a JSON object in {path.relative_to(ROOT)}")
    return value


def validate_skill(skill_path: Path) -> None:
    text = skill_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"missing YAML frontmatter: {skill_path.relative_to(ROOT)}")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        fail(f"incomplete YAML frontmatter: {skill_path.relative_to(ROOT)}")
    frontmatter = parts[1]
    for field in ("name:", "description:"):
        if field not in frontmatter:
            fail(f"missing {field[:-1]} in {skill_path.relative_to(ROOT)}")


def main() -> None:
    marketplace = read_json(MARKETPLACE_PATH)
    marketplace_name = marketplace.get("name")
    if not isinstance(marketplace_name, str) or not marketplace_name:
        fail("marketplace name must be a non-empty string")

    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or not entries:
        fail("marketplace must contain at least one plugin")

    seen_names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("each marketplace plugin entry must be an object")
        name = entry.get("name")
        if not isinstance(name, str) or not KEBAB_CASE.fullmatch(name):
            fail(f"invalid plugin name: {name!r}")
        if name in seen_names:
            fail(f"duplicate marketplace plugin: {name}")
        seen_names.add(name)

        source = entry.get("source")
        if not isinstance(source, dict) or source.get("source") != "local":
            fail(f"{name}: example marketplace source must be local")
        relative_path = source.get("path")
        if not isinstance(relative_path, str) or not relative_path.startswith("./"):
            fail(f"{name}: source.path must start with ./")
        plugin_dir = (ROOT / relative_path[2:]).resolve()
        if ROOT not in plugin_dir.parents:
            fail(f"{name}: source.path escapes repository root")
        if not plugin_dir.is_dir():
            fail(f"{name}: plugin directory does not exist")
        if plugin_dir.name != name:
            fail(f"{name}: folder name and marketplace name differ")

        policy = entry.get("policy")
        if not isinstance(policy, dict):
            fail(f"{name}: missing policy object")
        if policy.get("installation") not in VALID_INSTALLATION:
            fail(f"{name}: invalid installation policy")
        if policy.get("authentication") not in VALID_AUTHENTICATION:
            fail(f"{name}: invalid authentication policy")
        if not isinstance(entry.get("category"), str) or not entry["category"]:
            fail(f"{name}: category must be a non-empty string")

        manifest_path = plugin_dir / ".codex-plugin" / "plugin.json"
        manifest = read_json(manifest_path)
        if manifest.get("name") != name:
            fail(f"{name}: manifest name does not match folder name")
        version = manifest.get("version")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            fail(f"{name}: version is not valid semver")
        for field in ("description", "author", "interface"):
            if field not in manifest:
                fail(f"{name}: manifest is missing {field}")

        skills_path = manifest.get("skills")
        if not isinstance(skills_path, str) or not skills_path.startswith("./"):
            fail(f"{name}: skills path must start with ./")
        skills_dir = plugin_dir / skills_path[2:]
        skill_files = sorted(skills_dir.glob("*/SKILL.md"))
        if not skill_files:
            fail(f"{name}: no skills/*/SKILL.md files found")
        for skill_file in skill_files:
            validate_skill(skill_file)

        print(f"Validation passed: {name} {version}")


if __name__ == "__main__":
    main()
