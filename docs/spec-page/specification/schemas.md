## Formal Schemas and Data Validation

This document provides the definitive formal schemas for the Location Protocol, alongside comprehensive procedures for data validation and guidelines for schema evolution. The schemas are designed to be precise, implementable, and extensible, serving as the canonical reference for developers and validation tool implementers.

### Schema Definitions

The Location Protocol uses JSON Schema to formally define the structure, constraints, and data types of a location payload. This choice ensures compatibility with a wide range of validation tools and programming languages.

While presented here as a single, comprehensive schema, the components are defined in a modular fashion within the `definitions` section. This allows implementers to use the schema as a single file or break it into smaller, interconnected files for easier maintenance.

#### Naming Conventions

To ensure consistency and interoperability across the ecosystem, the Location Protocol adopts `snake_case` as the canonical naming convention for all schema fields.

- **Core Protocol**: All core fields (e.g., `lp_version`, `location_type`) and natively supported extensions MUST use `snake_case`.
- **Custom Extensions**: While not strictly enforced for custom or user-defined schemas, the use of `snake_case` is STRONGLY RECOMMENDED to maintain stylistic alignment with the protocol.

#### JSON Schema

The following JSON Schema, compliant with Draft 07 or later, defines the complete `LocationPayload` object. It includes base fields, location types, composable fields, and proof structures. The schema uses an `$id` for unique identification and references internal definitions for modularity.

```json
--8<-- "schema.json"
```

### Validation Procedure

Validating a location payload ensures it conforms to the protocol's structural and semantic rules. The process involves the following steps:

!!! note
      The `srs` property in all schemas MUST use a full URI (e.g., `http://www.opengis.net/def/crs/OGC/1.3/CRS84`). Shorthand codes like "EPSG:4326" are deprecated. See [Deprecation of legacy shorthand codes](../appendices/srs.md#deprecation-of-legacy-shorthand-codes).

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
