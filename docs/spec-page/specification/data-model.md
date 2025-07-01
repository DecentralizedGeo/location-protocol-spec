## Base Data Model Specification

Every Location Protocol payload must be a JSON object containing a set of required base fields that provide essential context for interpreting the location data. These fields ensure that any compliant system can correctly parse and understand the payload's structure, coordinate system, and specification version.

### Field Definitions and Constraints

The base data model consists of four required fields: `specVersion`, `srs`, `locationType`, and `location`. Implementations must ensure these fields are present and valid in every Location Protocol payload.

**`specVersion`**

- **Description**: A string that identifies the version of the Location Protocol specification to which the payload conforms. This ensures parsers can apply the correct rules for validation and interpretation.
- **Type**: `string`
- **Constraints**:
  - This field is **required**.
  - The value MUST follow a `major.minor` semantic versioning pattern (e.g., "1.0").

**`srs`**

- **Description**: A string specifying the Spatial Reference System (SRS) used for the coordinate values within the `location` field. Using a standard identifier is critical for interoperability.
- **Type**: `string`
- **Constraints**:
  - This field is **required**.
  - The value SHOULD be a standardized identifier, with the format `authority:code` being recommended (e.g., "EPSG:4326").

**`locationType`**

- **Description**: A string that defines the format of the data contained in the `location` field. This acts as a schema identifier, informing the consumer how to parse the `location` data.
- **Type**: `string`
- **Constraints**:
  - This field is **required**.
  - The value MUST correspond to an identifier in the official Location Type Registry (e.g., `geojson`, `h3`, `coordinate-decimal`).

**`location`**

- **Description**: The field containing the core spatial data. The structure of this field is determined by the value of `locationType`.
- **Type**: `string | number[] | object`
- **Constraints**:
  - This field is **required**.
  - The data structure MUST be valid according to the format specified by `locationType`. For example, if `locationType` is `geojson`, this field must contain a valid GeoJSON Geometry Object as defined in RFC 7946.

### Schema Definitions

The formal structure of the base data model is defined below in both JSON formats.

**JSON Schema**
This schema can be used for programmatic validation of Location Protocol payloads.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Location Protocol Base Payload",
  "description": "The base structure for a Location Protocol payload.",
  "type": "object",
  "properties": {
    "specVersion": {
      "description": "The specification version (e.g., '1.0').",
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "srs": {
      "description": "The Spatial Reference System identifier (e.g., 'EPSG:4326').",
      "type": "string"
    },
    "locationType": {
      "description": "The format of the 'location' field, from the Location Type Registry.",
      "type": "string"
    },
    "location": {
      "description": "The spatial data, whose structure is defined by 'locationType'."
    }
  },
  "required": ["specVersion", "srs", "locationType", "location"]
}
```

### Validation Rules and Flow

Validation is a sequential process. An implementation must check for the presence and syntactic validity of all required base fields before proceeding to semantic validation (i.e., checking if the `location` data matches the `locationType`).

**Validation Checks**

- The payload MUST be a valid JSON object.
- The `specVersion` field MUST be present and its value MUST match the `major.minor` version pattern.
- The `srs` field MUST be present and contain a non-empty string.
- The `locationType` field MUST be present and contain a non-empty string.
- The `location` field MUST be present.
- The value of the `location` field MUST validate against the schema defined for the given `locationType`.

**Validation Flowchart**
The following diagram illustrates the validation sequence for the base fields.

```mermaid
graph TD
    A[Start: Receive Payload] --> B{Is payload a valid JSON object?};
    B -- Yes --> C{Are all required base fields present?};
    B -- No --> Z[Fail: Invalid JSON];
    C -- No --> Y[Fail: Missing Required Field];
    C -- Yes --> D{Is 'specVersion' format valid?};
    D -- No --> X[Fail: Invalid specVersion];
    D -- Yes --> E{Is 'location' data valid for 'locationType'?};
    E -- No --> W[Fail: Mismatched Location Data];
    E -- Yes --> V[Success: Base Fields Valid];

    subgraph Base Field Checks
        C
        D
    end

    subgraph Semantic Check
        E
    end
```

### Payload Examples

**Valid Payload**
This example shows a correctly formatted payload using the `geojson` location type.

```json
{
  "specVersion": "1.0",
  "srs": "EPSG:4326",
  "locationType": "geojson",
  "location": {
    "type": "Point",
    "coordinates": [-103.771556, 44.967243]
  }
}
```

**Invalid Payloads**
These examples demonstrate common validation errors.

```json
// Invalid: Missing the required 'srs' field.
{
  "specVersion": "1.0",
  "locationType": "geojson",
  "location": {
    "type": "Point",
    "coordinates": [-103.771556, 44.967243]
  }
}
```

```json
// Invalid: 'specVersion' does not match the required pattern.
{
  "specVersion": "v1",
  "srs": "EPSG:4326",
  "locationType": "geojson",
  "location": {
    "type": "Point",
    "coordinates": [-103.771556, 44.967243]
  }
}
```

```json
// Invalid: 'location' data (an array) does not match the 'geojson' locationType (expects an object).
{
  "specVersion": "1.0",
  "srs": "EPSG:4326",
  "locationType": "geojson",
  "location": [-103.771556, 44.967243]
}
```

---

[:material-arrow-left: Back to Specification Overview](index.md){ .md-button .md-button--primary }
