# Plan 003: Resolve the contradictory canonical-encoding rules (CBOR RFC, key ordering, Base64 variant, hash algorithm)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat 84653d1..HEAD -- docs/spec-page/implementation/encoding.md docs/spec-page/implementation/examples.md docs/spec-page/implementation/workflow.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MED (these are normative wire-format decisions; wrong choices are hard to walk back once implementations ship)
- **Depends on**: plans/002-align-doc-examples-with-spec.md (touches adjacent text in `examples.md`; land 002 first to avoid merge conflicts)
- **Category**: docs (normative spec correctness)
- **Planned at**: commit `84653d1`, 2026-07-02

## Why this matters

The entire point of `encoding.md` is byte-for-byte determinism — "enabling developers to produce byte-for-byte identical outputs for any given payload" (`encoding.md:1`) — because hashes and signatures are computed over these bytes. Today two conformant implementations following different pages of the same spec produce **different bytes, different hashes, and signatures that fail to verify**:

1. **Base64 variant**: `encoding.md:40` mandates *standard* Base64 (RFC 4648, padded in its own example) while `examples.md:87` mandates *Base64url* and both its code samples emit unpadded base64url.
2. **CBOR canonicalization reference**: `encoding.md:39` cites RFC 7049 "Canonical CBOR" (length-first map key ordering); `examples.md:86` cites RFC 8949 (whose Core Deterministic Encoding orders keys by bytewise-lexicographic comparison of encoded keys). The two orderings differ in general.
3. **Key-ordering self-contradiction**: `encoding.md:8` and step 2 (line 38) mandate sorting JSON keys *alphabetically*, but the doc's own canonical CBOR output (step 3, line 99) is length-first ordered (`srs`, `location`, `lp_version`, `location_type`, `event_timestamp` — alphabetical would put `event_timestamp` first). A reader cannot tell which rule the hash is actually computed over. (Verified: the step-3 hex, step-4 base64, and step-5 SHA-256 are mutually consistent; it's the *prose rule* that contradicts them.)
4. **What gets CBOR-encoded is ambiguous**: step 3 says "Encode the canonical JSON *string* into … CBOR", which would produce a CBOR text string; the worked example actually encodes the *data item* (a CBOR map). Only one is correct.
5. **Hash algorithm**: `encoding.md:51` specifies SHA-256; `workflow.md:50` says "Generate a hash (e.g., Keccak-256)". A verifier re-computing the payload hash must know which one, exactly.
6. The worked example's payload (`encoding.md:80`) uses `"event_timestamp": "2025-06-25T23:18:00Z"` — a string, violating the spec's own integer-seconds definition. The spec's flagship encoding example fails the spec's canonical schema.

## Current state

- `docs/spec-page/implementation/encoding.md` — normative serialization/encoding/verification rules plus one worked example (payload → canonical JSON → CBOR hex → Base64 → SHA-256, lines 69–112).
- `docs/spec-page/implementation/examples.md:84-88` — restates the encoding pipeline ("1. Serialize … using CBOR (RFC 8949). 2. Encode … into a Base64url string").
- `docs/spec-page/implementation/workflow.md:40-52` — restates encoding + signing ("Reference: Adhere to specifications like RFC 7049", "Generate a hash (e.g., Keccak-256)").

Decision record (advisor-recommended resolutions — apply these unless a maintainer overrides; each choice matches what the majority of the repo's code examples already do):

| Question | Decision | Rationale |
|---|---|---|
| CBOR spec | **RFC 8949 Core Deterministic Encoding** (§4.2.1) | RFC 8949 obsoletes 7049; `cbor-x`/`cbor2` implement it; for definite-length text keys < 24 bytes the ordering coincides with 7049 length-first, so the existing worked-example bytes remain valid. |
| Map key order | **Defined by CBOR deterministic encoding (bytewise-lexicographic of encoded keys)**; drop the "sort JSON alphabetically" rule — canonical JSON is a presentation aid, not the hashed artifact | Removes contradiction #3; the hashed bytes are CBOR, so CBOR's rule must govern. |
| What is encoded | **The data item (JSON object → CBOR map)**, never the JSON text | Matches the worked example and both code samples. |
| Base64 variant | **Base64url without padding (RFC 4648 §5)** | Matches both code samples; URL/filename-safe is what attestation and web contexts need. |
| Payload hash | **SHA-256 over the deterministic CBOR bytes** | Matches `encoding.md`'s existing example. Keccak-256 appears only inside EAS/EIP-712 signing, which is the attestation layer's concern — clarify layering instead of offering two algorithms. |

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Install deps | `pip install poetry && poetry install --no-interaction` | exit 0 |
| Docs build | `poetry run mkdocs build` | exit 0 |
| Regenerate artifacts | inline python (Step 3) | values below |

## Scope

**In scope** (the only files you should modify):

- `docs/spec-page/implementation/encoding.md`
- `docs/spec-page/implementation/examples.md` (only the two pipeline sentences at lines 84–88)
- `docs/spec-page/implementation/workflow.md` (only lines 40–52, encoding/signing references)

**Out of scope** (do NOT touch):

- `json-schema/schema.json` (Plan 001) and all other docs.
- The signature/EIP-712 mechanics in `eas-integration.md` (Plan 004).
- Any change to which fields exist or their types — this plan is only about serialization, encoding, and hashing rules.

## Git workflow

- Branch: `advisor/003-canonical-encoding`
- Suggested commit: `docs(encoding): adopt RFC 8949 deterministic CBOR, unpadded base64url, and SHA-256 as the single canonical pipeline`
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Rewrite the normative rules in `encoding.md`

- "Field Ordering" section (line 8): replace the alphabetical-JSON-sort rule with: map keys are ordered by the **deterministic encoding rules of RFC 8949 §4.2.1** (bytewise-lexicographic comparison of the encoded keys); implementations MUST rely on a CBOR library's canonical/deterministic mode rather than pre-sorting JSON text. Note explicitly that the canonical *JSON* rendering shown in examples is illustrative only — hashes and signatures are computed over CBOR bytes, never JSON text.
- Step 3 (line 39): change "Encode the canonical JSON string" to "Encode the payload data item (the JSON object) as CBOR using the Core Deterministic Encoding Requirements of [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949)". Remove the RFC 7049 citation.
- Step 4 (line 40): change to **Base64url without padding**, citing RFC 4648 §5, and note this is the transport encoding for text contexts (the hash is computed over the CBOR bytes, not the Base64url string).
- Verification section (line 51): keep SHA-256; add one sentence: signature schemes layered on top (e.g. EAS/EIP-712) may internally use their own digest (Keccak-256); that is defined by the attestation layer, not by Location Protocol payload hashing.

**Verify**: `grep -n "7049" docs/spec-page/implementation/encoding.md` → no matches; `grep -n "8949" docs/spec-page/implementation/encoding.md` → ≥ 1 match; `grep -ni "alphabetical" docs/spec-page/implementation/encoding.md` → no normative-rule matches.

### Step 2: Fix the worked example's payload

In `encoding.md` lines 69–94, change `"event_timestamp": "2025-06-25T23:18:00Z"` to `"event_timestamp": 1750893480` in **both** the initial payload (line 80) and the canonical JSON rendering (line 88). (1750893480 is that instant as Unix seconds.)

**Verify**: `grep -n "2025-06-25T23:18:00Z" docs/spec-page/implementation/encoding.md` → no matches.

### Step 3: Regenerate the worked example's CBOR hex, Base64url, and hash

Replace the three artifact blocks with these exact values (precomputed; the integer timestamp changes the bytes):

- **Step 3 block (CBOR hex)**:
```
a563737273782c687474703a2f2f7777772e6f70656e6769732e6e65742f6465662f6372732f4f47432f312e332f4352533834686c6f636174696f6ea2647479706565506f696e746b636f6f7264696e6174657382fbc059f1612c6ac216fb40467bce9e5e24796a6c705f76657273696f6e65312e302e306d6c6f636174696f6e5f747970656d67656f6a736f6e2d706f696e746f6576656e745f74696d657374616d701a685c83a8
```
- **Step 4 block (Base64url, unpadded)** — also retitle the block from "Base64-Encoded CBOR" to "Base64url-Encoded CBOR (unpadded)":
```
pWNzcnN4LGh0dHA6Ly93d3cub3Blbmdpcy5uZXQvZGVmL2Nycy9PR0MvMS4zL0NSUzg0aGxvY2F0aW9uomR0eXBlZVBvaW50a2Nvb3JkaW5hdGVzgvvAWfFhLGrCFvtARnvOnl4keWpscF92ZXJzaW9uZTEuMC4wbWxvY2F0aW9uX3R5cGVtZ2VvanNvbi1wb2ludG9ldmVudF90aW1lc3RhbXAaaFyDqA
```
- **Step 5 block (SHA-256 of CBOR bytes)**:
```
a006a832451386d371c4ceb2e562fda575d9e137efb574cadef1162ff2f92202
```

**Verify** (checks all three are mutually consistent and match the doc):
```bash
python3 - << 'EOF'
import base64, binascii, hashlib, re
doc = open("docs/spec-page/implementation/encoding.md").read()
hexes = re.findall(r"^a5[0-9a-f]{100,}$", doc, re.M)
assert len(hexes) == 1, hexes
cbor = binascii.unhexlify(hexes[0])
b64 = base64.urlsafe_b64encode(cbor).rstrip(b"=").decode()
assert b64 in doc, "base64url block does not match hex block"
assert hashlib.sha256(cbor).hexdigest() in doc, "hash block does not match"
assert b"\x1a\x68\x5c\x83\xa8" in cbor, "integer timestamp missing from CBOR"
print("ok: hex, base64url, and sha256 are consistent")
EOF
```
→ `ok: hex, base64url, and sha256 are consistent`

### Step 4: Align the two restatements

- `examples.md:84-88`: make the pipeline read "1. Encode the payload as deterministic CBOR (RFC 8949). 2. Encode the CBOR bytes as unpadded Base64url (RFC 4648 §5)."
- `workflow.md:41-45`: replace "followed by Base64 encoding" with "followed by unpadded Base64url encoding" and the RFC 7049 reference with RFC 8949.
- `workflow.md:50`: replace "Generate a hash (e.g., Keccak-256) of the canonically encoded payload" with "Generate the SHA-256 hash of the deterministic CBOR bytes (EIP-712/EAS signing flows apply their own Keccak-256 digest internally — see the EAS integration appendix)".

**Verify**: `grep -rn "7049" docs/spec-page/` → no matches; `grep -rni "keccak" docs/spec-page/implementation/workflow.md` → only the parenthetical clarification remains.

### Step 5: Build the docs

**Verify**: `poetry run mkdocs build` → exit 0.

## Test plan

The Step 3 consistency script is the test. Plan 005's CI can additionally re-derive these artifacts from the payload (golden-vector test) — note that in your report as a follow-up hook.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `grep -rn "7049" docs/spec-page/` → 0 matches
- [ ] `grep -rn "base64url" docs/spec-page/implementation/encoding.md -i` → ≥ 1 match
- [ ] Step 3 consistency script prints `ok: hex, base64url, and sha256 are consistent`
- [ ] `grep -rn "2025-06-25T23:18:00Z" docs/spec-page/implementation/` → 0 matches
- [ ] `poetry run mkdocs build` exits 0
- [ ] `git status` shows changes only to the three in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- A maintainer note, issue, or ADR-like doc surfaces that already decided any of these questions differently — implement the maintainer's decision or stop and ask, do not ship the table's default over an explicit prior decision.
- The regenerated artifacts in Step 3 fail the consistency script — do not hand-tweak hex/base64/hash values; report the discrepancy.
- You find signature-verification prose describing "decrypting" a signature with a public key (`encoding.md:62`) and want to rewrite it — that's a real inaccuracy (signature verification is not decryption) but out of this plan's scope; note it in your report.

## Maintenance notes

- Any future change to the worked-example payload requires regenerating all three artifacts together; never edit one in isolation. Plan 005's checker should eventually enforce hex↔base64↔hash consistency automatically.
- If a `coordinate` or other new field with keys ≥ 24 bytes is ever added to examples, RFC 7049 vs RFC 8949 orderings can diverge; the spec now pins 8949, so libraries must be configured for *deterministic* (not "canonical 7049") mode — `cbor2.dumps(..., canonical=True)` currently emits length-first order, which agrees with 8949 for the short keys used here. Flag any example whose keys are ≥ 24 bytes for manual byte-order review.
- Reviewers: scrutinize that no *field semantics* changed — this plan only touches serialization/encoding/hash language and regenerated artifacts.
