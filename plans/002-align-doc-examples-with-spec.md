# Plan 002: Make every code example and payload in the docs conform to the specification it illustrates

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat 84653d1..HEAD -- docs/spec-page scripts/generate_encoding_example.py pyproject.toml`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: LOW
- **Depends on**: none (Plan 001 recommended first so the Step 8 validation passes cleanly)
- **Category**: docs (spec conformance)
- **Planned at**: commit `84653d1`, 2026-07-02

## Why this matters

The spec's normative rules are clear — field names are `snake_case` (`docs/spec-page/specification/schemas.md`, "Naming Conventions": core fields **MUST** use `snake_case`), `lp_version` is a 3-part semver string, and `event_timestamp` is an **integer** Unix timestamp in seconds (`docs/spec-page/specification/composable-fields.md`). But the implementation examples — the code developers actually copy — violate all three, and several docs reference fields that don't exist in the spec. A developer following `implementation/examples.md` verbatim produces payloads that fail the canonical schema. These are the highest-traffic pages for implementers; every one of these mismatches becomes a bug in someone's integration.

## Current state

Facts, all confirmed against the live files at commit `84653d1`:

1. `docs/spec-page/implementation/examples.md:13-30` — TypeScript interface and payload use `specVersion`, `locationType`, `eventTimestamp`, `mediaData`, `mediaType` (camelCase; wrong names entirely for `lp_version`) and `eventTimestamp: new Date().toISOString()` (string, spec requires integer seconds).
2. `examples.md:61` — Python example uses correct snake_case keys but `"event_timestamp": datetime.now(timezone.utc).isoformat()` (string).
3. `examples.md:97-102` — CBOR encoding example payload uses `specVersion: "1.0"` (camelCase AND a 2-part version violating pattern `^\d+\.\d+\.\d+$`) plus `locationType`.
4. `examples.md:303-314` — the AJV "simplified schema" is internally broken: `properties` are camelCase (`specVersion`, `locationType`) while `required` is snake_case (`["lp_version", "srs", "location_type", "location"]`), and there is a stray `srs: "http://..."` key at the top level of the schema object which is not a JSON Schema keyword. No payload can satisfy it as intended.
5. `examples.md:229-231` and `examples.md:340-342` — the hardcoded `encodedPayload` string decodes (base64url → CBOR) to a map with keys `srs`, `location`, `specVersion` (value `"1.0"`), `locationType` — non-conformant. The surrounding code then `console.assert`s that verification succeeds; with a correct schema it would fail.
6. `docs/spec-page/appendices/geojson-alignment.md:26,60-64,77,92` — the migration guide tells users to copy GeoJSON `properties` into a **`metadata`** field. No such composable field exists; the spec's mechanism for this is `attributes` (a JSON-encoded string, `composable-fields.md:40-51`) or the `extensions` object (`schemas.md:57-59`). The example payload at line 64 also uses `"event_timestamp": "2025-06-25T23:36:00Z"` (string).
7. `docs/spec-page/introduction/core-concepts.md:33,89` — refers to the proof field as `stamp_type` (singular); the schema (`json-schema/schema.json:211`) and `composable-fields.md:112` define `stamp_types`.
8. `docs/spec-page/specification/data-model.md:45` — "if `location_type` is `geojson`…" — `geojson` is not a registered location type; the registry has `geojson-point` / `geojson-line` / `geojson-polygon`.
9. `docs/spec-page/appendices/srs.md:105-115` — a `typescript` code block begins with the Python statement `import re`.
10. `scripts/generate_encoding_example.py:6-10` — contains a leftover first-person authoring note ("…but I must match the example's code structure to avoid confusing the user…") and deliberately regenerates the *non-conformant* camelCase payload. `cbor2`, which it imports, is not declared in `pyproject.toml`.

Repo conventions to match: docs are MkDocs Material with admonitions (`!!! note`), fenced code blocks with language tags, and payload examples elsewhere use snake_case + CRS84 URI (see `docs/spec-page/specification/location-types.md:48-55` as the exemplar style).

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Install deps | `pip install poetry && poetry install --no-interaction` | exit 0 |
| Add cbor2 dev dep (Step 7) | `poetry add --group dev cbor2` | exit 0; `pyproject.toml` + `poetry.lock` updated |
| Docs build | `poetry run mkdocs build` | exit 0, site builds |
| Regenerate payload | `poetry run python scripts/generate_encoding_example.py` | prints the base64url string given in Step 5 |

## Scope

**In scope** (the only files you should modify):

- `docs/spec-page/implementation/examples.md`
- `docs/spec-page/appendices/geojson-alignment.md`
- `docs/spec-page/introduction/core-concepts.md`
- `docs/spec-page/specification/data-model.md` (one word, item 8 above)
- `docs/spec-page/appendices/srs.md` (code fence fix, item 9 only)
- `scripts/generate_encoding_example.py`
- `pyproject.toml` and `poetry.lock` (only via `poetry add --group dev cbor2`)

**Out of scope** (do NOT touch, even though they look related):

- `json-schema/schema.json` — Plan 001.
- `docs/spec-page/implementation/encoding.md` — its worked example and the base64/CBOR normative rules are Plan 003; do not "fix while you're in there".
- `docs/spec-page/appendices/eas-integration.md` — Plan 004.
- Any restructuring of prose, headings, or nav.

## Git workflow

- Branch: `advisor/002-align-doc-examples`
- Commit style: conventional commits (repo history: `docs: fix typo in implementation index`). Suggested: `docs(examples): make code examples conform to snake_case fields, semver, and integer timestamps`
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Fix the TypeScript payload-creation example (`examples.md` lines 11–45)

Rename interface fields to the spec names and fix the timestamp type. Target shape:

```typescript
interface LocationPayload {
  lp_version: string;
  srs: string;
  location_type: string;
  location: any;
  event_timestamp?: number; // Unix timestamp, seconds since epoch
  media_data?: string; // Optional field for CIDs
  media_type?: string; // Optional field for MIME types
}

const payload: LocationPayload = {
  lp_version: "1.0.0",
  srs: "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  location_type: "coordinate-decimal+lon-lat",
  location: [-74.006, 40.7128], // [longitude, latitude]
  event_timestamp: Math.floor(Date.now() / 1000),
};
```

Update `validatePayload` to check `p.lp_version`, `p.srs`, `p.location_type`, `p.location`.

**Verify**: `grep -nE "specVersion|locationType|eventTimestamp|mediaData|mediaType" docs/spec-page/implementation/examples.md` → no matches in the payload-creation section (matches may remain temporarily in later sections until Steps 3–6).

### Step 2: Fix the Python payload-creation example (`examples.md` line 61)

Replace `"event_timestamp": datetime.now(timezone.utc).isoformat()` with `"event_timestamp": int(datetime.now(timezone.utc).timestamp())`.

**Verify**: `grep -n "isoformat" docs/spec-page/implementation/examples.md` → no matches.

### Step 3: Fix the CBOR encoding example payload (`examples.md` lines 96–102)

Replace the camelCase payload with:

```typescript
const payload = {
  lp_version: "1.0.0",
  srs: "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  location_type: "coordinate-decimal+lon-lat",
  location: [-74.006, 40.7128],
};
```

**Verify**: `grep -n 'specVersion: "1.0"' docs/spec-page/implementation/examples.md` → no matches.

### Step 4: Fix the AJV verification schema (`examples.md` lines 303–314)

Replace the broken "simplified schema" with a consistent one (snake_case properties matching `required`, stray `srs` key removed):

```typescript
const locationProtocolSchema = {
  type: "object",
  properties: {
    lp_version: { type: "string", pattern: "^\\d+\\.\\d+\\.\\d+$" },
    srs: { type: "string" },
    location_type: { type: "string" },
    location: {}, // array, object, or string depending on location_type
  },
  required: ["lp_version", "srs", "location_type", "location"],
};
```

Add one sentence below the block: for production use, validate against the full canonical schema at `json-schema/schema.json` instead of this simplified one.

**Verify**: `python3 - << 'EOF'` style check not needed; instead: `grep -n '"^http://www.opengis.net' docs/spec-page/implementation/examples.md` → no matches, and `grep -cn "lp_version" docs/spec-page/implementation/examples.md` → count ≥ 6.

### Step 5: Regenerate the hardcoded encoded payload (both occurrences)

Replace the `encodedPayload` string at BOTH `examples.md:229-231` (attestation section) and `examples.md:340-342` (verification section) with the canonical encoding of the Step 3 payload. The exact expected string (CBOR with length-first/deterministic key order — `srs`, `location`, `lp_version`, `location_type` — then base64url, no padding):

```
pGNzcnN4LGh0dHA6Ly93d3cub3Blbmdpcy5uZXQvZGVmL2Nycy9PR0MvMS4zL0NSUzg0aGxvY2F0aW9ugvvAUoBiTdLxqvtARFs9B8hLXmpscF92ZXJzaW9uZTEuMC4wbWxvY2F0aW9uX3R5cGV4GmNvb3JkaW5hdGUtZGVjaW1hbCtsb24tbGF0
```

**Verify**:
```bash
python3 - << 'EOF'
import base64
s = "pGNzcnN4LGh0dHA6Ly93d3cub3Blbmdpcy5uZXQvZGVmL2Nycy9PR0MvMS4zL0NSUzg0aGxvY2F0aW9ugvvAUoBiTdLxqvtARFs9B8hLXmpscF92ZXJzaW9uZTEuMC4wbWxvY2F0aW9uX3R5cGV4GmNvb3JkaW5hdGUtZGVjaW1hbCtsb24tbGF0"
raw = base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
assert b"lp_version" in raw and b"1.0.0" in raw and b"specVersion" not in raw
print("ok")
EOF
```
→ `ok`, and `grep -c "pGNzcnN4LGh0dHA6Ly93d3cub3Blbmdpcy5uZXQvZGVmL2Nycy9PR0MvMS4zL0NSUzg0aGxvY2F0aW9ugvvAUoBiTdLxqvtARFs9B8hLXmpscF92ZXJzaW9uZTEuMC4wbWxvY2F0aW9uX3R5cGV4GmNvb3JkaW5hdGUtZGVjaW1hbCtsb24tbGF0" docs/spec-page/implementation/examples.md` → `2`.

### Step 6: Fix `geojson-alignment.md` (phantom `metadata` field + string timestamp)

- Line 26 (migration step 5): change to instruct copying GeoJSON `properties` into the `attributes` composable field as a JSON-encoded string (cite `composable-fields.md`), noting `extensions` as the alternative for structured objects.
- Lines 60–64 (example payload): replace the `"metadata": {...}` member with `"attributes": "{\"name\": \"Statue of Liberty\", \"type\": \"National Monument\"}"` and replace `"event_timestamp": "2025-06-25T23:36:00Z"` with `"event_timestamp": 1750894560` (the same instant as an integer).
- Line 77 (mermaid): `LP 'metadata' field` → `LP 'attributes' field`.
- Line 92 (matrix row): `**Composable Fields** (\`metadata\`, etc.)` → `**Composable Fields** (\`attributes\`, etc.)`.

**Verify**: `grep -n "metadata" docs/spec-page/appendices/geojson-alignment.md` → no matches referring to a payload field (prose uses "metadata" generically elsewhere — acceptable only outside payload/field contexts; if unsure, zero matches is the safe target for lines 26, 60–64, 77, 92).

### Step 7: Fix `core-concepts.md`, `data-model.md`, `srs.md`, and the generator script

- `core-concepts.md:33`: `(\`stamp_type\` and \`stamps\`)` → `(\`stamp_types\` and \`stamps\`)`; `core-concepts.md:89`: `The \`stamp_type\` field` → `The \`stamp_types\` field`.
- `data-model.md:45`: `if \`location_type\` is \`geojson\`` → `if \`location_type\` is \`geojson-point\``.
- `srs.md:105-115`: remove the `import re` line (the block is TypeScript; the regex is defined inline and needs no import).
- Run `poetry add --group dev cbor2`.
- Rewrite `scripts/generate_encoding_example.py`: delete the leftover authoring comment (lines 6–10), change the payload to the Step 3 snake_case payload, keep `canonical=True` and base64url-unpadded output.

**Verify**: `grep -rn "stamp_type\b" docs/spec-page/ | grep -v stamp_types` → no matches; `grep -n "import re" docs/spec-page/appendices/srs.md` → no matches; `poetry run python scripts/generate_encoding_example.py` → output contains exactly the base64url string from Step 5.

### Step 8: Validate every changed payload against the canonical schema

```bash
poetry run python3 - << 'EOF'
import json
from jsonschema import Draft7Validator
v = Draft7Validator(json.load(open("json-schema/schema.json")))
payloads = [
    {"lp_version": "1.0.0", "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
     "location_type": "coordinate-decimal+lon-lat", "location": [-74.006, 40.7128],
     "event_timestamp": 1750893480},
    {"lp_version": "1.0.0", "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
     "location_type": "geojson-point",
     "location": {"type": "Point", "coordinates": [-74.0445, 40.6892]},
     "attributes": "{\"name\": \"Statue of Liberty\", \"type\": \"National Monument\"}",
     "event_timestamp": 1750894560},
]
for p in payloads:
    errs = sorted(v.iter_errors(p), key=str)
    assert not errs, errs
print("ok: all example payloads valid")
EOF
```

**Verify**: `ok: all example payloads valid` (requires Plan 001; if Plan 001 has not landed, this fails on nothing here — see STOP conditions). Then `poetry run mkdocs build` → exit 0.

## Test plan

No test suite exists. The verification gates above are the tests; Plan 005 adds a permanent doc-example conformance checker that will lock these fixes in. Do not create test files in this plan.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `grep -rnE "specVersion|locationType|eventTimestamp" docs/spec-page/implementation/examples.md` → 0 matches
- [ ] `grep -rn "isoformat\(\)" docs/spec-page/implementation/examples.md` → 0 matches
- [ ] `grep -rn "stamp_type\b" docs/spec-page/ | grep -v stamp_types` → 0 matches
- [ ] Step 5 decode check prints `ok`; the new encoded payload appears exactly twice in `examples.md`
- [ ] `poetry run python scripts/generate_encoding_example.py` prints the Step 5 base64url string
- [ ] Step 8 script prints `ok: all example payloads valid`
- [ ] `poetry run mkdocs build` exits 0
- [ ] `git status` shows changes only to the in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- Line numbers/excerpts in "Current state" don't match the live files (docs restructured since planning).
- Step 8 fails **because of the schema itself** (string location types rejected) — Plan 001 hasn't landed; report and mark this plan blocked on 001 rather than editing `schema.json`.
- `poetry add --group dev cbor2` fails to resolve (network/lockfile issues) — report; do not hand-edit `poetry.lock`.
- You find additional non-conformant examples beyond those listed (e.g. in `encoding.md` or `eas-integration.md`) — leave them; they belong to Plans 003/004. Note them in your report.

## Maintenance notes

- Reviewers should diff-check that only field *names/types* changed in code blocks — the pedagogical structure (validate → encode → attest → verify) must be preserved.
- The hardcoded encoded payload now depends on the canonical CBOR key-ordering convention. If Plan 003 changes the normative ordering rule, re-run `scripts/generate_encoding_example.py` and confirm the string is unchanged (for these short keys, RFC 7049 length-first and RFC 8949 bytewise orderings agree).
- Deferred: `examples.md`'s AJV block still says "simplified schema" — a future improvement is loading `json-schema/schema.json` directly in the example.
