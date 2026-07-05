# Plan 005: Add a doc-example conformance checker and CI so the spec can't contradict itself silently again

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat 84653d1..HEAD -- scripts/ json-schema/ netlify.toml pyproject.toml`
> Plans 001–002 are *expected* to have changed `json-schema/schema.json` and
> the docs since `84653d1` — that is not drift. Treat as drift only changes to
> `scripts/verify_json_schema.py`, `netlify.toml`, or an already-existing
> `.github/workflows/` directory.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: LOW
- **Depends on**: plans/001-fix-schema-location-oneof.md and plans/002-align-doc-examples-with-spec.md (without them, the new CI is red on arrival). Runs correctly before/after 003 and 004.
- **Category**: tests / dx
- **Planned at**: commit `84653d1`, 2026-07-02

## Why this matters

This repository's product is the specification itself, and its critical path is *internal consistency*: examples must validate against the schema they illustrate. Today there is no verification baseline — no CI at all (no `.github/workflows/`), and the only checker, `scripts/verify_json_schema.py`, verifies that schemas are *well-formed Draft-07 schemas*, never that the spec's example payloads *validate against* the canonical schema. That gap is exactly how a schema bug that rejects 4 of 9 location types (Plan 001) and a README example that fails validation shipped unnoticed. One script + one workflow closes it permanently. A bonus fix rides along: Netlify builds pin Python 3.11 (`netlify.toml:5`) while `pyproject.toml` requires `>=3.12` — a time bomb for the docs deploy.

## Current state

- `scripts/verify_json_schema.py` — existing checker; extracts ```json blocks from markdown (including resolving `--8<--` snippet includes) and runs `Draft7Validator.check_schema` on each. Its markdown-block extraction (`parse_markdown_json_blocks`, lines 84–127) is the exemplar to model the new script on. Its CLI shape (argparse, `main() -> int`, `raise SystemExit(main())`) is the repo's script convention — match it.
- `json-schema/schema.json` — canonical payload schema (post-Plan-001: `properties.location` uses `anyOf`).
- Doc payload examples live in ```json blocks across `README.md` and `docs/spec-page/**/*.md`. Payload blocks are recognizable: they are JSON objects containing both `lp_version` and `location_type` keys. `docs/spec-page/specification/data-model.md:138-174` also contains three *deliberately invalid* payloads, each preceded by a `// Invalid:` comment **inside** the block — which makes them unparseable as strict JSON.
- No `.github/` directory exists.
- `pyproject.toml:12`: `requires-python = ">=3.12,<4"`; dev group has `jsonschema`. `netlify.toml:5`: `PYTHON_VERSION = "3.11"`.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Install deps | `pip install poetry && poetry install --no-interaction` | exit 0 |
| Existing checker | `poetry run python scripts/verify_json_schema.py` | `OK: 1 schema(s) verified as Draft 07` |
| New checker | `poetry run python scripts/validate_doc_examples.py` | see Step 2 |
| Docs build | `poetry run mkdocs build` | exit 0 |

## Scope

**In scope** (the only files you should create/modify):

- `scripts/validate_doc_examples.py` (create)
- `.github/workflows/ci.yaml` (create)
- `netlify.toml` (one line: `PYTHON_VERSION = "3.12"`)

**Out of scope** (do NOT touch):

- `scripts/verify_json_schema.py` — reuse by importing or by shelling out; do not modify it.
- `json-schema/schema.json`, all docs content, `mkdocs.yaml`, `pyproject.toml`.
- Fixing any non-conformant example the checker finds (report instead — see STOP conditions).

## Git workflow

- Branch: `advisor/005-conformance-ci`
- Suggested commit: `ci: validate doc payload examples against the canonical schema` (and `fix(netlify): align Python version with requires-python` for the netlify change, or one combined commit)
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Create `scripts/validate_doc_examples.py`

Behavior spec:

1. Inputs: optional path arguments (default: repo root `README.md` + `docs/spec-page/`), `--schema` (default `json-schema/schema.json`).
2. Extract fenced ```json blocks from every `.md` file, reusing the line-scanning approach of `parse_markdown_json_blocks` in `scripts/verify_json_schema.py` (copy the loop; do not import private helpers if that couples the scripts awkwardly — a copied 30-line function with a comment pointing at the original is acceptable here).
3. For each block: attempt `json.loads`. If parsing fails → skip (covers prose fragments and the deliberately-invalid blocks that contain `// Invalid:` comments); if the block parses but is not a dict, or lacks *both* `lp_version` and `location_type` keys → skip (not a payload).
4. Validate every payload block against the canonical schema with `jsonschema.Draft7Validator`.
5. Output: one line per failure — `<file>:<line>: <first error message>`; then a summary. Exit 0 iff zero failures and at least one payload was checked; exit 1 otherwise (zero payloads found means the extractor broke — fail loudly).

Match the CLI/typing conventions of `scripts/verify_json_schema.py` (dataclass for sources is optional; `from __future__ import annotations`, argparse, `main() -> int`).

**Verify**: `poetry run python scripts/validate_doc_examples.py` → exit 0, summary reports **≥ 12 payloads checked, 0 failures** (payload blocks exist in README.md ×3, data-model.md ×1 valid, location-types.md ×4, composable-fields.md ×3, geojson-alignment.md ×1, encoding.md ×2 — exact count may drift with Plans 002/003; anything ≥ 12 with 0 failures passes).

### Step 2: Prove the checker catches regressions

Temporarily (do not commit) re-introduce a bug: in `json-schema/schema.json`, change `properties.location` `anyOf` back to `oneOf`. Run the checker.

**Verify**: `poetry run python scripts/validate_doc_examples.py; echo "exit=$?"` → lists at least the README H3 example as a failure and prints `exit=1`. Then `git checkout -- json-schema/schema.json` and re-run → exit 0.

### Step 3: Create `.github/workflows/ci.yaml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install --no-interaction
      - name: Verify JSON Schemas are valid Draft 07
        run: poetry run python scripts/verify_json_schema.py
      - name: Validate doc payload examples against canonical schema
        run: poetry run python scripts/validate_doc_examples.py
      - name: Build docs
        run: poetry run mkdocs build
```

**Verify**: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yaml')); print('ok')"` → `ok` (if PyYAML is unavailable, `poetry run python` with the same one-liner; mkdocs depends on PyYAML so it is present in the poetry env). Also run each of the three workflow commands locally → all exit 0.

### Step 4: Fix the Netlify Python version

In `netlify.toml:5`, change `PYTHON_VERSION = "3.11"` to `PYTHON_VERSION = "3.12"` (keep the trailing comment or drop it; `pyproject.toml` demands `>=3.12`).

**Verify**: `grep -n 'PYTHON_VERSION' netlify.toml` → `PYTHON_VERSION = "3.12"`.

## Test plan

Step 2 *is* the test (mutation check: the checker must fail on a known-bad schema and pass on the fixed one). No separate test files — the checker is itself the test infrastructure this repo gains.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `poetry run python scripts/validate_doc_examples.py` → exit 0, ≥ 12 payloads checked, 0 failures
- [ ] Step 2 mutation check demonstrated (checker exits 1 on re-introduced `oneOf` bug), and the mutation was reverted (`git diff json-schema/schema.json` is empty)
- [ ] `poetry run python scripts/verify_json_schema.py` → `OK: 1 schema(s) verified as Draft 07`
- [ ] `poetry run mkdocs build` → exit 0
- [ ] `.github/workflows/ci.yaml` parses as YAML; its three run-steps each succeed locally
- [ ] `grep -n 'PYTHON_VERSION = "3.12"' netlify.toml` → 1 match
- [ ] `git status` shows only: new `scripts/validate_doc_examples.py`, new `.github/workflows/ci.yaml`, modified `netlify.toml`
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- The checker (correctly implemented) reports failures on the current docs — that means Plans 001/002 haven't fully landed or missed a payload. Report the exact `<file>:<line>` failures; do not edit docs or schema from this plan.
- Zero payload blocks are found — the extraction heuristic is wrong for this repo's markdown; report rather than loosening the heuristic blindly.
- `poetry install` cannot resolve on Python 3.12 — report; do not modify `pyproject.toml`.

## Maintenance notes

- Contributors adding payload examples to docs now get CI feedback; docs with deliberately-invalid examples must keep the `// Invalid:` comment style *inside* the block (it makes the block unparseable, so the checker skips it). If the docs ever adopt parseable invalid-examples, extend the checker with an explicit expected-to-fail marker instead of the parse-failure heuristic.
- Follow-up hook (deferred): extend the checker to verify the encoding worked example's hex ↔ base64url ↔ SHA-256 consistency (see Plan 003's verification script for the exact logic).
- If Netlify's build image lacks Python 3.12, the deploy will fail visibly — check the first Netlify deploy after merge; fallback is relaxing `requires-python` to `>=3.11` instead (maintainer choice).
