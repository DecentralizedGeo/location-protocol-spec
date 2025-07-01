## Formal Schemas and Data Validation

This document provides the definitive formal schemas for the Location Protocol, alongside comprehensive procedures for data validation and guidelines for schema evolution. The schemas are designed to be precise, implementable, and extensible, serving as the canonical reference for developers and validation tool implementers.

### Schema Definitions

The Location Protocol uses JSON Schema to formally define the structure, constraints, and data types of a location payload. This choice ensures compatibility with a wide range of validation tools and programming languages.

While presented here as a single, comprehensive schema, the components are defined in a modular fashion within the `definitions` section. This allows implementers to use the schema as a single file or break it into smaller, interconnected files for easier maintenance.

#### JSON Schema

The following JSON Schema, compliant with Draft 07 or later, defines the complete `LocationPayload` object. It includes base fields, location types, composable fields, and proof structures. The schema uses an `$id` for unique identification and references internal definitions for modularity.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://locationprotocol.io/schemas/v1/location-payload.schema.json",
  "title": "Location Protocol Payload",
  "description": "A complete schema for a Location Protocol attestation payload.",
  "type": "object",
  "properties": {
    "specVersion": {
      "$ref": "#/definitions/specVersion"
    },
    "srs": {
      "$ref": "#/definitions/srs"
    },
    "locationType": {
      "$ref": "#/definitions/locationType"
    },
    "location": {
      "description": "The location data, whose format is determined by locationType.",
      "oneOf": [
        { "$ref": "#/definitions/locationCoordinateDecimal" },
        { "$ref": "#/definitions/locationGeoJSON" },
        { "$ref": "#/definitions/locationH3" }
      ]
    },
    "eventTimestamp": {
      "$ref": "#/definitions/eventTimestamp"
    },
    "mediaData": {
      "$ref": "#/definitions/mediaData"
    },
    "mediaType": {
      "$ref": "#/definitions/mediaType"
    },
    "proof": {
      "$ref": "#/definitions/proof"
    },
    "extensions": {
      "type": "object",
      "description": "An object for custom, non-standard fields."
    }
  },
  "required": ["specVersion", "srs", "locationType", "location"],
  "definitions": {
    "specVersion": {
      "type": "string",
      "description": "The version of the Location Protocol specification.",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "examples": ["1.0.0"]
    },
    "srs": {
      "type": "string",
      "description": "The Spatial Reference System for the location coordinates, preferably an EPSG code.",
      "pattern": "^EPSG:\\d+$",
      "examples": ["EPSG:4326"]
    },
    "locationType": {
      "type": "string",
      "description": "Identifier for the location data format.",
      "enum": ["coordinate-decimal.lon-lat", "geojson.point", "h3.index"]
    },
    "locationCoordinateDecimal": {
      "description": "Location as a longitude, latitude array.",
      "type": "array",
      "items": { "type": "number" },
      "minItems": 2,
      "maxItems": 2
    },
    "locationGeoJSON": {
      "description": "A GeoJSON Point object as defined in RFC 7946.",
      "type": "object",
      "properties": {
        "type": { "const": "Point" },
        "coordinates": { "$ref": "#/definitions/locationCoordinateDecimal" }
      },
      "required": ["type", "coordinates"]
    },
    "locationH3": {
      "description": "Location as an H3 cell index.",
      "type": "string",
      "pattern": "^[89ab][0-9a-f]{14}$"
    },
    "eventTimestamp": {
      "type": "string",
      "description": "ISO 8601 timestamp of the event.",
      "format": "date-time"
    },
    "mediaData": {
      "type": "string",
      "description": "A URI or Content Identifier (CID) for associated media.",
      "format": "uri"
    },
    "mediaType": {
      "type": "string",
      "description": "The MIME type of the associated mediaData.",
      "examples": ["image/jpeg", "video/mp4"]
    },
    "proof": {
      "type": "object",
      "description": "A cryptographic proof of the location claim.",
      "properties": {
        "recipeType": {
          "type": "string",
          "description": "Identifier for the proof generation method."
        },
        "recipePayload": {
          "type": "object",
          "description": "The data required to verify the proof."
        }
      },
      "required": ["recipeType", "recipePayload"]
    }
  }
}
```

### Validation Procedure

Validating a location payload ensures it conforms to the protocol's structural and semantic rules. The process involves the following steps:

1. **Select Schema**: Identify the `specVersion` from the payload and load the corresponding version of the Location Protocol schema.
2. **Choose a Validator**: Use a robust validation library that supports JSON Schema Draft 07 or later. Recommended tools include AJV for JavaScript/Node.js or equivalent validators for other languages.
3. **Perform Structural Validation**: Validate the payload against the loaded schema. This initial pass checks for:
   - Presence of all `required` fields.
   - Correct data types for each field (e.g., `string`, `number`, `object`).
   - Compliance with format constraints (e.g., `pattern` for `srs`, `format` for `eventTimestamp`).
   - Adherence to enumerations (e.g., `locationType`).
4. **Perform Conditional Validation**: The schema uses `oneOf` to enforce that the structure of the `location` field matches the specified `locationType`. The validator will automatically handle this conditional logic.
5. **Handle Errors**: If validation fails, the validator will report a list of errors, typically including the path to the invalid field and a description of the issue. This feedback is crucial for debugging malformed payloads.

While the protocol specifies the schema, it does not mandate specific validator configurations (e.g., strict mode). Implementers should choose settings appropriate for their application's requirements.

### Schema Evolution and Versioning

To ensure long-term stability and interoperability, the Location Protocol adheres to a strict versioning and evolution policy.

#### Semantic Versioning

The protocol uses the **Semantic Versioning (SemVer)** standard (`MAJOR.MINOR.PATCH`) to manage changes to the schema:

- **MAJOR** version (e.g., `2.0.0`) is incremented for breaking changes, such as removing a required field, changing a field's data type, or altering a required pattern in a non-backward-compatible way.
- **MINOR** version (e.g., `1.1.0`) is incremented for additive, backward-compatible changes, such as adding a new optional field or adding a new value to an `enum`.
- **PATCH** version (e.g., `1.0.1`) is incremented for non-breaking bug fixes or clarifications, such as correcting a typo in a field's `description`.

#### Extension Points

The schema is designed to be extensible. Custom, non-standard fields can be added within the optional `extensions` object. This allows for innovation and custom use cases without invalidating core protocol compliance.

#### Field Status: Experimental and Deprecated

To manage the lifecycle of schema fields, the following conventions are used:

- **Experimental Fields**: New, unstable fields may be introduced with a vendor prefix (e.g., `x-custom-field`) or within the `extensions` object to signal that they are subject to change.
- **Deprecated Fields**: When a field is planned for removal, it will be marked as deprecated in its `description`. The property will be removed in a future MAJOR version release, and the deprecation policy will provide a clear migration path and timeline.

---

[:material-arrow-left: Back to Specification Overview](index.md){ .md-button .md-button--primary }
