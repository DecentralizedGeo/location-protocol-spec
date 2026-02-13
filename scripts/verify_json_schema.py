#!/usr/bin/env python3
"""Verify JSON Schema Draft 07 definitions.

Validates JSON schemas (from .json files or JSON code blocks in .md files)
against the Draft 07 meta-schema using the jsonschema library.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from jsonschema import Draft7Validator

DRAFT07_URIS = {
    "http://json-schema.org/draft-07/schema#",
    "https://json-schema.org/draft-07/schema#",
    "http://json-schema.org/draft-07/schema",
    "https://json-schema.org/draft-07/schema",
}

SNIPPET_DIRECTIVE_RE = re.compile(r'^--8<--\s+["\']([^"\']+)["\']\s*$')


@dataclass
class SchemaSource:
    path: Path
    label: str
    schema: object


def parse_json_file(path: Path) -> Iterable[SchemaSource]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    yield SchemaSource(path=path, label=str(path), schema=data)


def parse_json_block(path: Path, start_line: int, block_index: int, block_text: str) -> SchemaSource:
    label = f"{path}:{start_line} (block {block_index})"
    try:
        data = json.loads(block_text)
    except json.JSONDecodeError as exc:
        return SchemaSource(path=path, label=label, schema=exc)
    return SchemaSource(path=path, label=label, schema=data)


def parse_snippet_block(
    path: Path,
    start_line: int,
    block_index: int,
    include_target: str,
    repo_root: Path,
    original_block_text: str,
) -> SchemaSource:
    label = f"{path}:{start_line} (block {block_index})"
    candidate_paths = [
        path.parent / include_target,
        repo_root / include_target,
        repo_root / "json-schema" / include_target,
    ]
    include_path = next((candidate for candidate in candidate_paths if candidate.exists()), None)

    if include_path is None:
        error = json.JSONDecodeError(
            f"snippet include not found: {include_target}",
            original_block_text,
            0,
        )
        return SchemaSource(path=path, label=label, schema=error)

    try:
        data = json.loads(include_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return SchemaSource(path=path, label=label, schema=exc)

    label = f"{path}:{start_line} (block {block_index}, include {include_path})"
    return SchemaSource(path=path, label=label, schema=data)


def parse_markdown_json_blocks(path: Path) -> Iterable[SchemaSource]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_block = False
    block_start_line = 0
    block_lines: List[str] = []
    blocks: List[Tuple[int, str]] = []

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not in_block and stripped.lower().startswith("```json"):
            in_block = True
            block_start_line = idx + 1
            block_lines = []
            continue
        if in_block and stripped.startswith("```"):
            in_block = False
            blocks.append((block_start_line, "\n".join(block_lines)))
            block_lines = []
            continue
        if in_block:
            block_lines.append(line)

    repo_root = Path(__file__).resolve().parents[1]

    for block_index, (start_line, block_text) in enumerate(blocks, start=1):
        stripped_block = block_text.strip()
        if not stripped_block:
            continue

        snippet_match = SNIPPET_DIRECTIVE_RE.match(stripped_block)
        if snippet_match:
            include_target = snippet_match.group(1)
            yield parse_snippet_block(
                path=path,
                start_line=start_line,
                block_index=block_index,
                include_target=include_target,
                repo_root=repo_root,
                original_block_text=stripped_block,
            )
            continue

        yield parse_json_block(path=path, start_line=start_line, block_index=block_index, block_text=block_text)


def iter_schema_sources(paths: Iterable[Path]) -> Iterable[SchemaSource]:
    for path in paths:
        if path.is_dir():
            for child in path.rglob("*.json"):
                yield from parse_json_file(child)
            for child in path.rglob("*.md"):
                yield from parse_markdown_json_blocks(child)
            continue
        if path.suffix.lower() == ".json":
            yield from parse_json_file(path)
        elif path.suffix.lower() == ".md":
            yield from parse_markdown_json_blocks(path)


def require_draft07(schema: object, label: str) -> List[str]:
    if not isinstance(schema, dict):
        return [f"{label}: schema must be a JSON object"]
    schema_uri = schema.get("$schema")
    if schema_uri not in DRAFT07_URIS:
        return [
            f"{label}: $schema must be Draft 07 (got {schema_uri!r})",
        ]
    return []


def validate_schema(schema: object, label: str) -> List[str]:
    if isinstance(schema, json.JSONDecodeError):
        return [f"{label}: invalid JSON ({schema.msg})"]
    if not isinstance(schema, dict):
        return [f"{label}: schema must be a JSON object"]
    try:
        Draft7Validator.check_schema(schema)
    except Exception as exc:  # pragma: no cover - defensive
        return [f"{label}: {exc}"]
    return []


def resolve_default_paths() -> List[Path]:
    repo_root = Path(__file__).resolve().parents[1]
    default_file = repo_root / "docs" / "spec-page" / "specification" / "schemas.md"
    if default_file.exists():
        return [default_file]
    return [repo_root]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify JSON Schema Draft 07 definitions.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files or directories containing schema JSON or markdown files.",
    )
    parser.add_argument(
        "--allow-missing-schema",
        action="store_true",
        help="Do not require $schema to be Draft 07.",
    )
    args = parser.parse_args()

    paths = args.paths or resolve_default_paths()
    sources = list(iter_schema_sources(paths))
    if not sources:
        print("No JSON schemas found.")
        return 1

    failures: List[str] = []
    for source in sources:
        if not args.allow_missing_schema:
            failures.extend(require_draft07(source.schema, source.label))
        failures.extend(validate_schema(source.schema, source.label))

    if failures:
        print("Schema verification failed:\n")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"OK: {len(sources)} schema(s) verified as Draft 07")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
