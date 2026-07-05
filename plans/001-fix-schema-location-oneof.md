# Plan 001: Make the canonical JSON Schema accept string-based location types (h3, geohash, wkt, address)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat 84653d1..HEAD -- json-schema/schema.json`
> If the file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug
- **Planned at**: commit `84653d1`, 2026-07-02

## Why this matters

`json-schema/schema.json` is the canonical, published validation schema for the entire Location Protocol ("the definitive formal schemas", per `docs/spec-page/specification/schemas.md`). As written, it **rejects every conformant payload whose `location` is a string** — that is, all four of the `h3`, `geohash`, `wkt`, and `address` location types (4 of the 9 registered types). Even the H3 example in the repository's own `README.md` fails validation against this schema. Any implementer who wires this schema into AJV or `jsonschema`, exactly as the spec instructs, will conclude that valid payloads are invalid.

## Current state

Relevant file: `json-schema/schema.json` — the canonical payload schema, included into the docs via the `--8<-- "schema.json"` snippet in `docs/spec-page/specification/schemas.md:23`.

The bug: `properties.location` (lines 17–28) uses `oneOf` — which requires the value to match **exactly one** branch:

```json
"location": {
  "description": "The location data, whose format is determined by location_type.",
  "oneOf": [
    { "$ref": "#/definitions/locationCoordinateDecimal" },
    { "$ref": "#/definitions/locationGeoJSON" },
    { "$ref": "#/definitions/locationH3" },
    { "$ref": "#/definitions/locationGeohash" },
    { "$ref": "#/definitions/locationWKT" },
    { "$ref": "#/definitions/locationAddress" },
    { "$ref": "#/definitions/locationScaledCoordinates" }
  ]
},
```

But the string-typed definitions overlap (lines 157–174): `locationWKT` and `locationAddress` are both unconstrained `{"type": "string"}`, so **any** string matches at least those two branches. Measured overlap for representative values:

| `location` value | Branches matched | `oneOf` result |
|---|---|---|
| `"8928308280fffff"` (h3) | locationH3, locationGeohash, locationWKT, locationAddress = 4 | **FAIL** |
| `"9q8yyk8ytpxr"` (geohash) | locationGeohash, locationWKT, locationAddress = 3 | **FAIL** |
| `"POINT(-103.77 44.96)"` (wkt) | locationWKT, locationAddress = 2 | **FAIL** |
| `"1600 Pennsylvania Ave"` (address) | locationWKT, locationAddress = 2 | **FAIL** |
| `[-74.006, 40.7128]` (coordinate-decimal) | locationCoordinateDecimal = 1 | pass |
| GeoJSON object | locationGeoJSON = 1 | pass |

The type-specific pairing of `location_type` ↔ `location` shape is *already* correctly enforced by the discriminated **top-level** `oneOf` (lines 53–117), where each branch pins `location_type` with a `const`, so exactly one branch can match. The per-property `oneOf` inside `properties.location` adds nothing except this bug.

Repo conventions: the schema is JSON Schema Draft 07 (`"$schema": "http://json-schema.org/draft-07/schema#"`), verified in CI-less fashion by `scripts/verify_json_schema.py` (checks meta-schema validity only, not instance behavior).

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Install deps | `pip install poetry && poetry install --no-interaction` | exit 0 (installs `jsonschema` from the dev group) |
| Fallback if poetry unavailable | `python3 -m pip install jsonschema` | exit 0 |
| Meta-schema check | `poetry run python scripts/verify_json_schema.py json-schema/schema.json --allow-missing-schema` | `OK: 1 schema(s) verified as Draft 07` — note: without `--allow-missing-schema` and with the file passed explicitly it still passes because the file has a Draft-07 `$schema` |

## Scope

**In scope** (the only file you should modify):

- `json-schema/schema.json`

**Out of scope** (do NOT touch, even though they look related):

- `docs/spec-page/specification/data-model.md` — its inline "Base Payload" schema has no `location` shape constraints and is unaffected.
- `docs/spec-page/specification/schemas.md` — it includes `schema.json` by snippet; no edit needed.
- The `locationH3` first-character class `[89ab]` and the unbounded `locationGeohash` length — see Maintenance notes; do not change patterns in this plan.
- Any doc example payloads (handled by Plan 002).

## Git workflow

- Branch: `advisor/001-fix-schema-location-oneof`
- Commit style: conventional commits, matching repo history (e.g. `fix: typo in schemas documentation`). Suggested message: `fix(schema): accept string location types by relaxing per-property oneOf to anyOf`
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Change `properties.location` `oneOf` to `anyOf`

In `json-schema/schema.json`, in the `properties.location` object (line 19), change the key `"oneOf"` to `"anyOf"`. Do not change the branch list, the top-level `oneOf` (line 53), or anything else. `anyOf` keeps `location` restricted to the union of known shapes (rejecting e.g. `42` or `true`) while leaving the exact pairing to the discriminated top-level `oneOf`.

**Verify**: `python3 -c "import json; s=json.load(open('json-schema/schema.json')); assert 'anyOf' in s['properties']['location'] and 'oneOf' not in s['properties']['location']; print('ok')"` → `ok`

### Step 2: Confirm the schema is still a valid Draft-07 schema

**Verify**: `poetry run python scripts/verify_json_schema.py json-schema/schema.json` → `OK: 1 schema(s) verified as Draft 07`

### Step 3: Validate representative instances

Run this instance-level check (uses the `jsonschema` dev dependency):

```bash
poetry run python3 - << 'EOF'
import json
from jsonschema import Draft7Validator
schema = json.load(open("json-schema/schema.json"))
v = Draft7Validator(schema)
base = {"lp_version": "1.0.0", "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}
valid = [
    dict(base, location_type="h3", location="8928308280fffff"),
    dict(base, location_type="geohash", location="9q8yyk8ytpxr"),
    dict(base, location_type="wkt", location="POINT(-103.77 44.96)"),
    dict(base, location_type="address", location="1600 Pennsylvania Ave NW, Washington, DC"),
    dict(base, location_type="geojson-point", location={"type": "Point", "coordinates": [-122.4194, 37.7749]}),
    dict(base, location_type="coordinate-decimal+lon-lat", location=[-74.006, 40.7128]),
    dict(base, location_type="scaledCoordinates", location={"x": 1, "y": 2, "scale": 1000}),
]
invalid = [
    dict(base, location_type="geojson-point", location=[-74.006, 40.7128]), # array for a point type
    dict(base, location_type="h3", location="not-an-h3-index"),
    {k: v2 for k, v2 in dict(base, location_type="geojson-point", location={"type": "Point", "coordinates": [0, 0]}).items() if k != "srs"}, # missing srs
]
for p in valid:
    assert v.is_valid(p), f"should be VALID: {p['location_type']}"
for p in invalid:
    assert not v.is_valid(p), f"should be INVALID: {p}"
print(f"ok: {len(valid)} valid accepted, {len(invalid)} invalid rejected")
EOF
```

**Verify**: output is `ok: 7 valid accepted, 3 invalid rejected`

## Test plan

There is no test suite in this repository. The instance-level script in Step 3 is the test for this change; Plan 005 turns this class of check into a permanent script + CI gate. Do not create test files in this plan.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] Step 1 python assertion prints `ok`
- [ ] `poetry run python scripts/verify_json_schema.py json-schema/schema.json` prints `OK: 1 schema(s) verified as Draft 07`
- [ ] Step 3 script prints `ok: 7 valid accepted, 3 invalid rejected`
- [ ] `git diff --stat` shows exactly one changed file: `json-schema/schema.json` (one-line change)
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- `properties.location` in the live file no longer matches the excerpt above (schema restructured since planning).
- After the change, any of the 7 valid payloads in Step 3 still fails — that means a second latent bug; report which branch fails and why instead of patching further.
- You find yourself wanting to edit the `definitions` patterns or the top-level `oneOf` — that is out of scope here.

## Maintenance notes

- The top-level discriminated `oneOf` is now the sole enforcer of `location_type` ↔ `location` pairing; if new location types are added, they need both a `definitions` entry **and** a top-level `oneOf` branch, and the `location_type` enum must be extended.
- Known residual looseness (accepted, not fixed here): `locationWKT`/`locationAddress` accept any string, so e.g. `location_type: "wkt"` with a street address validates. Tightening WKT would need a real grammar pattern — flag for a future registry with per-type schemas.
- Investigate later: `locationH3` pattern `^[89ab][0-9a-f]{14}$` — H3 *cell* indexes in canonical 15-char form always start with `8` (mode 1); `9`/`a`/`b` imply reserved bits set. Also `locationGeohash` has no length bound (geohashes are practically ≤ 12 chars).
- The schema's `$id` points at `refs/heads/main` — a mutable URL for a spec meant to underpin signed data; see the direction notes in `plans/README.md`.
