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
  "description": "A complete schema for a Location Protocol record payload.",
  "type": "object",
  "properties": {
    "lp_version": {
      "$ref": "#/definitions/lp_version"
    },
    "srs": {
      "$ref": "#/definitions/srs"
    },
    "location_type": {
      "$ref": "#/definitions/location_type"
    },
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
    "event_timestamp": {
      "$ref": "#/definitions/event_timestamp"
    },
    "media_data": {
      "$ref": "#/definitions/media_data"
    },
    "media_type": {
      "$ref": "#/definitions/media_type"
    },
    "attributes": {
      "$ref": "#/definitions/attributes"
    },
    "attributes_schema": {
      "$ref": "#/definitions/attributes_schema"
    },
    "proof": {
      "$ref": "#/definitions/proof"
    },
    "extensions": {
      "type": "object",
      "description": "An object for custom, non-standard fields."
    }
  },
  "required": ["lp_version", "srs", "location_type", "location"],
  "oneOf": [
    {
      "properties": {
        "location_type": { "const": "coordinate-decimal+lon-lat" },
        "location": { "$ref": "#/definitions/locationCoordinateDecimal" }
      },
      "required": ["location_type", "location"]
    },
    {
      "properties": {
        "location_type": { "const": "geojson-point" },
        "location": { "allOf": [ { "$ref": "#/definitions/locationGeoJSON" }, { "properties": { "type": { "const": "Point" } }, "required": ["type"] } ] }
      },
      "required": ["location_type", "location"]
    },
    {
      "properties": {
        "location_type": { "const": "geojson-line" },
        "location": { "allOf": [ { "$ref": "#/definitions/locationGeoJSON" }, { "properties": { "type": { "const": "LineString" } }, "required": ["type"] } ] }
      },
      "required": ["location_type", "location"]
    },
    {
      "properties": {
        "location_type": { "const": "geojson-polygon" },
        "location": { "allOf": [ { "$ref": "#/definitions/locationGeoJSON" }, { "properties": { "type": { "const": "Polygon" } }, "required": ["type"] } ] }
      },
      "required": ["location_type", "location"]
    },
    {
      "properties": {
        "location_type": { "const": "h3" },
        "location": { "$ref": "#/definitions/locationH3" }
      },
      "required": ["location_type", "location"]
    },
    {
      "properties": {
        "location_type": { "const": "geohash" },
        "location": { "$ref": "#/definitions/locationGeohash" }
      },
      "required": ["location_type", "location"]
    },
    {
      "properties": {
        "location_type": { "const": "wkt" },
        "location": { "$ref": "#/definitions/locationWKT" }
      },
      "required": ["location_type", "location"]
    },
    {
      "properties": {
        "location_type": { "const": "address" },
        "location": { "$ref": "#/definitions/locationAddress" }
      },
      "required": ["location_type", "location"]
    },
    {
      "properties": {
        "location_type": { "const": "scaledCoordinates" },
        "location": { "$ref": "#/definitions/locationScaledCoordinates" }
      },
      "required": ["location_type", "location"]
    }
  ],
  "definitions": {
    "lp_version": {
      "type": "string",
      "description": "The version of the Location Protocol specification.",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "examples": ["1.0.0"]
    },
    "srs": {
      "type": "string",
      "description": "The Spatial Reference System URI, following OGC standards.",
      "format": "uri",
      "examples": [
        "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
        "http://www.opengis.net/def/crs/EPSG/0/4326"
      ]
    },
    "location_type": {
      "type": "string",
      "description": "Identifier for the location data format.",
      "enum": ["coordinate-decimal+lon-lat", "geojson-point", "geojson-line", "geojson-polygon", "h3", "geohash", "wkt", "address", "scaledCoordinates"]
    },
    "locationCoordinateDecimal": {
      "description": "Location as a longitude, latitude array.",
      "type": "array",
      "items": { "type": "number" },
      "minItems": 2,
      "maxItems": 2
    },
    "locationGeoJSON": {
      "description": "A GeoJSON Geometry object as defined in RFC 7946. Supports geometry types: Point, LineString, and Polygon.",
      "type": "object",
      "properties": {
        "type": {
          "enum": ["Point", "LineString", "Polygon"]
        }
      },
      "required": ["type"],
      "additionalProperties": true
    },
    "locationH3": {
      "description": "Location as an H3 cell index.",
      "type": "string",
      "pattern": "^[89ab][0-9a-f]{14}$"
    },
    "locationGeohash": {
      "description": "Location as a Geohash string.",
      "type": "string",
      "pattern": "^[0123456789bcdefghjkmnpqrstuvwxyz]+$"
    },
    "locationWKT": {
      "description": "Location as a Well-Known Text (WKT) string.",
      "type": "string"
    },
    "locationAddress": {
      "description": "Location as a standard mailing or street address.",
      "type": "string"
    },
    "locationScaledCoordinates": {
      "description": "Location as scaled integer coordinates.",
      "type": "object",
      "properties": {
        "x": { "type": "integer" },
        "y": { "type": "integer" },
        "scale": { "type": "integer", "exclusiveMinimum": 0 }
      },
      "required": ["x", "y", "scale"]
    },
    "event_timestamp": {
      "type": "integer",
      "description": "Unix timestamp (seconds since epoch) of the event.",
      "exclusiveMinimum": 0
    },
    "media_data": {
      "type": "string",
      "description": "A URI or Content Identifier (CID) for associated media."
    },
    "media_type": {
      "type": "string",
      "description": "The MIME type of the associated media_data.",
      "examples": ["image/jpeg", "video/mp4"]
    },
    "attributes": {
      "type": "string",
      "description": "JSON-encoded structured metadata or CID reference."
    },
    "attributes_schema": {
      "type": "string",
      "description": "Schema reference using prefix notation (e.g., 'json:inline:', 'ipfs:cid:', 'eas:chain:', 'atproto:lexicon:')."
    },
    "proof": {
      "type": "object",
      "description": "A cryptographic proof of the location claim.",
      "properties": {
        "stamp_type": {
          "type": "string",
          "description": "Identifier for the proof generation method."
        },
        "stamps": {
          "type": "string",
          "description": "The data required to verify the proof."
        }
      },
      "required": ["stamp_type", "stamps"]
    }
  }
}
```

### Validation Procedure

Validating a location payload ensures it conforms to the protocol's structural and semantic rules. The process involves the following steps:

> **Note:** The `srs` property in all schemas MUST use a full URI (e.g., `http://www.opengis.net/def/crs/OGC/1.3/CRS84`). Shorthand codes like "EPSG:4326" are deprecated. See [Deprecation of legacy shorthand codes](../appendices/srs.md#deprecation-of-legacy-shorthand-codes).

1. **Select Schema**: Identify the `lp_version` from the payload and load the corresponding version of the Location Protocol schema.
2. **Choose a Validator**: Use a robust validation library that supports JSON Schema Draft 07 or later. Recommended tools include AJV for JavaScript/Node.js or equivalent validators for other languages.
3. **Perform Structural Validation**: Validate the payload against the loaded schema. This initial pass checks for:
   - Presence of all `required` fields.
   - Correct data types for each field (e.g., `string`, `number`, `object`).
   - Compliance with format constraints (e.g., `format` for `srs` and `event_timestamp`).
   - Adherence to enumerations (e.g., `location_type`).
4. **Perform Conditional Validation**: The schema uses `oneOf` to enforce that the structure of the `location` field matches the specified `location_type`. The validator will automatically handle this conditional logic.
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
