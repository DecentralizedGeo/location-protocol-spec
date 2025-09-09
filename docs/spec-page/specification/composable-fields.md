## Composable Fields and Extensions

The Location Protocol is designed for extensibility. Beyond the required base fields, payloads can include optional composable fields to add rich context, such as media attachments or custom proof data. This modularity allows implementers to tailor location attestations to specific use cases without altering the core data model.

This document defines the standard set of optional fields, outlines the framework for proof extensions, and describes the process for registering new fields.

### Optional Composable Fields

These fields can be added to any Location Payload to provide supplementary information.

---

#### `eventTimestamp`

- **Type**: `Integer`
- **Description**: A Unix timestamp (seconds since epoch) representing when the reported event occurred, which may differ from when the attestation was created. This field allows for the reporting of historical location data.
- **Constraints**: Must be a positive integer.

---

#### `mediaData`

- **Type**: `String`
- **Description**: Contains data or a reference to an external media object, such as a photo, video, or audio recording, that provides evidence or context for the location attestation. To manage payload size and on-chain costs, it is strongly recommended to use a Content Identifier (CID) from a decentralized storage network like IPFS instead of embedding large media files directly. Using a CID allows for efficient, verifiable, and decentralized handling of large media files.
- **Constraints**:
  - When using a CID, the string should follow the standard CID format.
  - For direct embedding of small files, Base64 encoding is recommended.
  - Implementations should define and enforce reasonable size limits to maintain performance.

---

#### `mediaType`

- **Type**: `String`
- **Description**: Specifies the MIME type of the content in the `mediaData` field, suchas `image/jpeg` or `application/pdf`. This field is essential for clients to correctly interpret and render the associated media.
- **Constraints**: Must be a valid MIME type string as defined by IANA standards.

### Schema Definitions

The following snippets define the schema for the optional composable fields.

**JSON Schema**

```json
{
  "eventTimestamp": {
    "type": "integer",
    "description": "Unix timestamp of the event time.",
    "exclusiveMinimum": 0
  },
  "mediaData": {
    "type": "string",
    "description": "Base64 encoded media or a Content Identifier (CID)."
  },
  "mediaType": {
    "type": "string",
    "description": "MIME type of the media data."
  }
}
```

### Proof Extension Framework

The Location Protocol supports custom, verifiable proof mechanisms through the `proof` object, which contains `recipeType` and `recipePayload` fields. This allows for domain-specific verification methods beyond the base attestation signature.

> **Note**: The proof extension framework is an advanced feature. The definitions and validation requirements are expected to evolve with community feedback and implementation experience.

---

#### `proof.recipeType`

- **Type**: `String`
- **Description**: An identifier for the type of proof recipe being used. This string signals to verifiers which validation logic to apply to the `recipePayload`. Examples could include `signed-sensor-reading.v1` or `hardware-attestation.tpm.v2`.
- **Constraints**: Must be a unique, versioned identifier registered in the extension registry.

---

#### `proof.recipePayload`

- **Type**: `String` (typically Base64 encoded)
- **Description**: The data payload for the specified proof recipe. Its structure and content are defined by the `recipeType`. This could contain cryptographic signatures, sensor data, or other evidence that can be independently verified according to the recipe's rules.
- **Constraints**: The payload must conform to the schema and validation rules defined by its corresponding `recipeType`.

### Usage Patterns

The following examples demonstrate how composable fields can be combined within a Location Payload.

**Simple Payload with Timestamp**
This example includes an `eventTimestamp` to specify when a delivery was recorded.

```json
{
  "srs": "EPSG:4326",
  "locationType": "coordinate-decimal.lon-lat",
  "location": [-74.006, 40.7128],
  "specVersion": "1.0",
  "eventTimestamp": 1732552800
}
```

**Complex Payload with Media and Proof**
This example includes a CID reference to a photo on IPFS and a custom proof payload for a hardware-attested location reading.

```json
{
  "srs": "EPSG:4326",
  "locationType": "geojson.Point",
  "location": {
    "type": "Point",
    "coordinates": [-122.4194, 37.7749]
  },
  "specVersion": "1.0",
  "mediaData": "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
  "mediaType": "image/jpeg",
  "proof": {
    "recipeType": "trusted-hardware.gps.v1",
    "recipePayload": "a1b2c3d4e5f6..."
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
