## Composable Fields and Extensions

The Location Protocol is designed for extensibility. Beyond the required base fields, payloads can include optional composable fields to add rich context, such as media attachments, structured attributes, or custom proof data. This modularity allows implementers to tailor location records to specific use cases without altering the core data model.

This document defines the standard set of optional fields, outlines the framework for proof extensions, and describes the process for registering new fields.

### Optional Composable Fields

These fields can be added to any Location Payload to provide supplementary information.

---

#### `event_timestamp`

- **Type**: `integer`
- **Description**: A Unix timestamp (seconds since epoch) representing when the reported event occurred, which may differ from when the record was created. This field allows for the reporting of historical location data.
- **Constraints**: Must be a positive integer.

---

#### `media_data`

- **Type**: `string`
- **Description**: Contains data or a reference to an external media object, such as a photo, video, or audio recording, that provides evidence or context for the location record. To manage payload size and on-chain costs, it is strongly recommended to use a Content Identifier (CID) from a decentralized storage network like IPFS instead of embedding large media files directly. Using a CID allows for efficient, verifiable, and decentralized handling of large media files.
- **Constraints**:
  - When using a CID, the string should follow the standard CID format.
  - For direct embedding of small files, Base64 encoding is recommended.
  - Implementations should define and enforce reasonable size limits to maintain performance.

---

#### `media_type`

- **Type**: `string`
- **Description**: Specifies the MIME type of the content in the `media_data` field, such as `image/jpeg` or `application/pdf`. This field is essential for clients to correctly interpret and render the associated media.
- **Constraints**: Must be a valid MIME type string as defined by IANA standards.

---

#### `attributes`

- **Type**: `string`
- **Description**: A JSON-encoded string containing structured metadata about the location as key-value pairs, or a CID/URI reference resolving to such data. This field enables rich, domain-specific attributes to be attached to location records (e.g., field observations, environmental monitoring data, logistics metadata). The term "attributes" aligns with GIS conventions where features have associated attribute tables.
- **Constraints**:
  - When present, the value SHOULD be valid JSON or a valid CID/URI.
  - If `attributes_schema` is provided, the attributes MUST validate against that schema.
  - Parsers MAY skip validation if they don't support the referenced schema system.
- **Examples**:
  - `"{\"species\": \"Quercus alba\", \"height_m\": 12.5}"`
  - `"bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"`

---

#### `attributes_schema`

- **Type**: `string`
- **Description**: A reference to the schema that defines the structure and validation rules for the `attributes` field. This field uses prefix notation to indicate the schema system: `{system}:{namespace}:{identifier}`.
- **Supported formats**:
  - `json:inline:{base64}` - Inline JSON Schema, base64 encoded
  - `ipfs:cid:{cid}` - IPFS-hosted schema document
  - `eas:{chain}:{uid}` - EAS schema UID (e.g., `eas:base:0xabc123...`)
  - `atproto:lexicon:{nsid}` - ATProto lexicon (e.g., `atproto:lexicon:app.bsky.feed.post`)
- **Constraints**:
  - This field is only meaningful when `attributes` is also present.
  - Parsers SHOULD emit warnings (not errors) if validation fails or the schema system is unsupported.
- **Examples**:
  - `"json:inline:eyJ0eXBlIjoib2JqZWN0In0="`
  - `"ipfs:cid:bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"`
  - `"eas:base:0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a"`

### Schema Definitions

The following snippets define the schema for the optional composable fields.

**JSON Schema**

```json
{
  "event_timestamp": {
    "type": "integer",
    "description": "Unix timestamp of the event time.",
    "exclusiveMinimum": 0
  },
  "media_data": {
    "type": "string",
    "description": "Base64 encoded media or a Content Identifier (CID)."
  },
  "media_type": {
    "type": "string",
    "description": "MIME type of the media data."
  },
  "attributes": {
    "type": "string",
    "description": "JSON-encoded structured metadata or CID reference."
  },
  "attributes_schema": {
    "type": "string",
    "description": "Schema reference using prefix notation (e.g., 'json:inline:', 'ipfs:cid:', 'eas:chain:', 'atproto:lexicon:')."
  }
}
```

### Proof Extension Framework

The Location Protocol supports custom, verifiable proof mechanisms through the `proof` object, which contains `stamp_types` and `stamps` fields. This allows for domain-specific verification methods beyond the base record signature.

> **Note**: The proof extension framework is an advanced feature, still in development. The definitions and validation requirements are expected to evolve with community feedback and implementation experience.

---

#### `proof.stamp_types`

- **Type**: `string`
- **Description**: An identifier for the type of proof recipe being used. This string signals to verifiers which validation logic to apply to the `stamps`. Examples might include `signed_sensor_reading.v1` or `hardware_attestation.tpm.v2`. (Location proof plugin naming conventions have not been established.)
- **Constraints**: Must be a unique, versioned identifier registered in the extension registry.

---

#### `proof.stamps`

- **Type**: `string` (typically Base64 encoded)
- **Description**: The data payload for the specified proof recipe. Its structure and content are defined by the `stamp_types`. This could contain cryptographic signatures, sensor data, or other evidence that can be independently verified according to the recipe's rules.
- **Constraints**: The payload must conform to the schema and validation rules defined by its corresponding `stamp_types`.

### Usage Patterns

The following examples demonstrate how composable fields can be combined within a Location Payload.

**Simple Payload with Timestamp**
This example includes an `event_timestamp` to specify when a delivery was recorded.

```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  "location_type": "coordinate-decimal",
  "location": [-74.006, 40.7128],
  "event_timestamp": 1732552800
}
```

**Payload with Structured Attributes**
This example shows field observation data with an inline JSON schema reference.

```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/EPSG/0/4326",
  "location_type": "geojson-point",
  "location": {
    "type": "Point",
    "coordinates": [44.967243, -103.771556]
  },
  "attributes": "{\"species\": \"Pinus ponderosa\", \"height_m\": 18.2, \"dbh_cm\": 45.3}",
  "attributes_schema": "json:inline:eyJ0eXBlIjoib2JqZWN0IiwicHJvcGVydGllcyI6eyJzcGVjaWVzIjp7InR5cGUiOiJzdHJpbmcifSwiaGVpZ2h0X20iOnsidHlwZSI6Im51bWJlciJ9fX0="
}
```

**Complex Payload with Media and Proof**
This example includes a CID reference to a photo on IPFS and a custom proof payload for a hardware-attested location reading.

```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  "location_type": "geojson-point",
  "location": {
    "type": "Point",
    "coordinates": [-122.4194, 37.7749]
  },
  "media_data": "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
  "media_type": "image/jpeg",
  "proof": {
    "stamp_types": "trusted_hardware.gps.v1",
    "stamps": "a1b2c3d4e5f6..."
  }
}
```

### Extension Registration and Discovery

To ensure interoperability, new composable fields and proof recipes should be proposed and documented through a community-governed process.

**Proposal Process**

- **Submission**: Proposers submit a formal definition, including a use case, schema, and validation rules, following an RFC-style template.
- **Review**: The proposal undergoes a public comment and review period by community members and protocol maintainers.
- **Adoption**: Once consensus is reached, the new extension is merged into the official registry with a designated status (e.g., `experimental`, `stable`, `deprecated`).

**Extension Registry**
A static registry file, likely in a JSON format, will serve as the canonical source for all registered extensions. Each entry will contain metadata such as its unique ID, description, schema reference, and stability status. This allows tools and implementers to discover and dynamically support new extensions.

At present, the use of custom fields not defined in the registry is not supported in the reference AstralSDK implementation, but this may be considered for future releases. Deprecation of fields will be managed through the registry, with clear timelines to ensure backward compatibility for implementers.

---

[:material-arrow-left: Back to Specification Overview](index.md){ .md-button .md-button--primary }
