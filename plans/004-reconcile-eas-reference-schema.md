# Plan 004: Reconcile the EAS reference schema with the data model (uint8 lp_version, two competing schemas, unparseable location string)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat 84653d1..HEAD -- docs/spec-page/appendices/eas-integration.md docs/spec-page/implementation/examples.md`
> If either file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: MED (the doc references an already-registered on-chain schema UID; docs must describe reality, not aspiration)
- **Depends on**: plans/002-align-doc-examples-with-spec.md (examples.md context), plans/003-resolve-canonical-encoding-contradictions.md (canonical payload encoding is what the recommended schema carries)
- **Category**: docs (reference-implementation correctness)
- **Planned at**: commit `84653d1`, 2026-07-02

## Why this matters

EAS is the protocol's *reference implementation* (`overview.md`, `workflow.md`), and the EAS appendix is where implementers copy their schema string from. The appendix's "base schema" contradicts the core data model on the most fundamental field, and the repo presents **two different** EAS schemas as the way to attest a payload, without acknowledging the other exists. Implementers picking different pages produce mutually unreadable attestations — the exact failure the protocol exists to prevent.

## Current state

Confirmed against the live files:

1. `docs/spec-page/appendices/eas-integration.md:69-70, 88-89` — the "base schema for the Location Protocol":
   ```typescript
   const schemaString =
     "string srs, string location_type, string location, uint8 lp_version";
   ```
   But the data model (`docs/spec-page/specification/data-model.md:9-16`) requires `lp_version` to be a **string** matching `major.minor.patch` (e.g. `"1.0.0"`). A `uint8` cannot carry `"1.0.0"`; the appendix's own payload example (line 120) attests `{ name: "lp_version", value: 1, type: "uint8" }` — a value that violates the spec's required pattern.
2. `eas-integration.md:119` — `{ name: "location", value: "-103.771556, 44.967243", type: "string" }` — a comma-separated string that corresponds to **no** registered `location_type` serialization (`coordinate-decimal+lon-lat` is defined as a JSON array, `location-types.md:26,48-55`). No parser following the spec can interpret it.
3. `eas-integration.md:102, 138-139` — states the schema UID for the field-per-field schema is `0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a`. The same UID appears in `composable-fields.md:69` as an `eas:base:` example.
4. `docs/spec-page/implementation/examples.md:194-196` — presents a *different* EAS schema, `"string locationPayload"`, carrying the entire canonically-encoded payload as one string. Neither page mentions the other's approach.

Why two approaches exist (context for the executor): a field-per-field schema makes individual fields readable by on-chain resolvers/indexers; a single-string schema preserves the canonical CBOR encoding end-to-end (hashes/signatures survive intact, all 9 location types work, optional fields need no schema change). The protocol's determinism story (Plan 003) only holds along the single-string path.

**Recommended resolution** (apply unless a maintainer overrides): make the single-string schema (`"string locationPayload"`) the *primary reference schema*, and present the field-per-field schema as an *alternative for on-chain readability* — with its types corrected to carry spec-conformant values (`string lp_version`, and `location` defined as the JSON-serialized value of the `location` field).

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Install deps | `pip install poetry && poetry install --no-interaction` | exit 0 |
| Docs build | `poetry run mkdocs build` | exit 0 |

## Scope

**In scope** (the only file you should modify):

- `docs/spec-page/appendices/eas-integration.md`

**Out of scope** (do NOT touch):

- `docs/spec-page/implementation/examples.md` — its `"string locationPayload"` flow is already the recommended shape; Plans 002/003 own its edits.
- `docs/spec-page/specification/composable-fields.md` — the `eas:base:0xedd6...` string there is only a *format example* for `attributes_schema`; leave it.
- Registering any new schema on-chain, or any code/SDK work.

## Git workflow

- Branch: `advisor/004-eas-schema-reconciliation`
- Suggested commit: `docs(eas): make string locationPayload the primary reference schema; fix uint8 lp_version`
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Restructure "Schema Registration" around the primary schema

In `eas-integration.md`, section "Schema Registration":

- Present the primary reference schema first:
  ```typescript
  const schemaString = "string locationPayload";
  ```
  with one paragraph: the value is the complete Location Protocol payload, deterministically CBOR-encoded and Base64url-encoded per the encoding guide (link `../implementation/encoding.md`); this preserves canonical bytes for hashing/signature verification and supports every location type and optional field without schema changes.
- Move the field-per-field schema into a clearly-labeled subsection "Alternative: field-level schema (indexer-friendly)" and correct it to:
  ```typescript
  const schemaString =
    "string srs, string location_type, string location, string lp_version";
  ```
  with a note: `lp_version` is the semver string (e.g. `"1.0.0"`); `location` is the JSON-serialized value of the payload's `location` field (e.g. `"[-103.771556, 44.967243]"` for `coordinate-decimal+lon-lat`); this variant does not preserve the canonical CBOR bytes, so payload-hash verification per the encoding guide does not apply to it.

**Verify**: `grep -n "uint8" docs/spec-page/appendices/eas-integration.md` → no matches.

### Step 2: Fix the attestation-creation example (lines 112–130)

Update the `SchemaEncoder` example to the primary schema:

```typescript
const schemaEncoder = new SchemaEncoder("string locationPayload");
const encodedData = schemaEncoder.encodeData([
  { name: "locationPayload", value: encodedPayload, type: "string" },
]);
```

where `encodedPayload` is described as the Base64url string produced by the encoding pipeline (reference the worked example in `../implementation/encoding.md`). Remove the `value: 1, type: "uint8"` row and the `"-103.771556, 44.967243"` comma-string.

**Verify**: `grep -n '"-103.771556, 44.967243"' docs/spec-page/appendices/eas-integration.md` → no matches; `grep -n "locationPayload" docs/spec-page/appendices/eas-integration.md` → ≥ 2 matches.

### Step 3: Handle the registered schema UID honestly

The doc claims UID `0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a` corresponds to the old field-per-field/uint8 schema string. After Step 1 that claim would be misattached. Do NOT silently re-attach the UID to a different schema string:

- Keep the UID mentioned only in the alternative-schema subsection, labeled as "the UID previously registered for the legacy `uint8 lp_version` schema string" — or, if you cannot confirm what schema string that UID actually hashes to, replace the concrete UID with a placeholder `"0x..."` and add the sentence "look up the current registered UID on [EASSCAN](https://easscan.org)".
- Add a note that the primary `"string locationPayload"` schema must be registered once per network and its UID pinned by implementers (which the doc's own best-practices section already advises).

**Verify**: `grep -n "0xedd6b005" docs/spec-page/appendices/eas-integration.md` → either 0 matches, or every remaining match is inside the alternative-schema subsection with the "legacy" labeling.

### Step 4: Sweep the rest of the appendix for consistency

Re-read the whole file; update any remaining prose that assumes four separate schema fields (e.g. "a schema must contain the four base fields", line ~62) to say the schema must *carry the payload's four required base fields*, whether packed as one canonical string (primary) or as individual fields (alternative).

**Verify**: `poetry run mkdocs build` → exit 0; manual re-read confirms no remaining `uint8`/comma-string references.

## Test plan

No automated tests apply to prose. Verification gates above (greps + build) are the checks. Plan 005's example-checker does not parse TypeScript blocks; consistency here stays a review-time concern.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `grep -n "uint8" docs/spec-page/appendices/eas-integration.md` → 0 matches
- [ ] `grep -n '"-103.771556, 44.967243"' docs/spec-page/appendices/eas-integration.md` → 0 matches
- [ ] `grep -c "locationPayload" docs/spec-page/appendices/eas-integration.md` → ≥ 2
- [ ] Step 3 UID condition holds
- [ ] `poetry run mkdocs build` exits 0
- [ ] `git status` shows changes only to `docs/spec-page/appendices/eas-integration.md`
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- You find evidence (issue, commit message, external doc) that the field-per-field schema is the intentional production schema used by AstralSDK or a deployed system — in that case the *data model* and this appendix need a maintainer decision about which is authoritative; do not pick unilaterally.
- The excerpts in "Current state" don't match the live file.
- You are tempted to verify the UID on-chain — that requires network access and is explicitly not required; use the placeholder path in Step 3 instead.

## Maintenance notes

- Whatever schema string is primary, its registered UID per network should eventually live in a small table in this appendix (Sepolia / Base / Optimism / …) — deferred, needs someone with on-chain access to verify each UID.
- If a future protocol version adds required fields, the single-string schema needs no re-registration (the payload is opaque), but the field-per-field variant does — reviewers should keep that asymmetry stated in the doc.
- Reviewer focus: Step 3 — the doc must never assert that a UID corresponds to a schema string the executor did not verify.
