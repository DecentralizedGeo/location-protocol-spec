## GeoJSON Alignment and Interoperability

The Location Protocol is designed for interoperability with established geospatial standards to ensure broad adoption and seamless integration into existing workflows. This document outlines how the protocol aligns with GeoJSON (RFC 7946) and leverages Spatial Reference System (SRS) identifiers like EPSG codes, providing clear guidance for developers working across both conventional and decentralized ecosystems. The protocol encapsulates standard formats, adding a layer of cryptographic verifiability without replacing the underlying data structures that developers already use.

### Standards Mapping

While the Location Protocol is a container for location information, its fields map logically to concepts within the GeoJSON standard. The primary goal is to carry GeoJSON data as a verifiable payload.

The table below illustrates the direct mapping between Location Protocol's core fields and their GeoJSON counterparts when `locationType` is set to `geojson`.

| Location Protocol Field | GeoJSON Equivalent | Description                                                                                                                                                                 |
| :---------------------- | :----------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `locationType`          | N/A                | A Location Protocol field that specifies the format of the `location` data. For GeoJSON, this would be set to `geojson`.                                                    |
| `location`              | `geometry`         | The `location` field directly holds a standard GeoJSON `Geometry` object (e.g., Point, LineString, Polygon).                                                                |
| `srs`                   | `crs` (deprecated) | Specifies the Spatial Reference System. For GeoJSON, this MUST be `EPSG:4326` to comply with RFC 7946, which mandates WGS 84.                                               |
| `composable-fields`     | `properties`       | Optional fields in the Location Protocol payload can be used to store the contents of the GeoJSON `properties` object, preserving all metadata associated with the feature. |

### Migration Guidance: GeoJSON to Location Protocol

Converting an existing GeoJSON `Feature` object into a Location Protocol payload is a straightforward process. This allows developers to wrap standard geospatial data in a verifiable, attestable format.

1. **Start with a GeoJSON Feature**: Begin with a standard GeoJSON `Feature` object, which contains `geometry` and `properties`.
2. **Initialize Location Protocol Payload**: Create a new Location Protocol payload structure.
3. **Set `locationType`**: Set the `locationType` field to `"geojson"` to indicate the format of the location data.
4. **Assign Geometry**: Copy the entire `geometry` object from the GeoJSON `Feature` into the `location` field of the protocol payload.
5. **Assign Properties**: Copy the `properties` object from the GeoJSON `Feature` into a suitable composable field, such as `metadata`, within the Location Protocol payload.
6. **Set Spatial Reference System (`srs`)**: Set the `srs` field to `"EPSG:4326"`. According to RFC 7946, GeoJSON coordinates are always in the World Geodetic System 1984 (WGS 84), and `EPSG:4326` is the corresponding identifier.

#### Example Conversion

This example demonstrates the transformation of a GeoJSON `Feature` into a Location Protocol payload.

**1. Original GeoJSON `Feature`**

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-74.0445, 40.6892]
  },
  "properties": {
    "name": "Statue of Liberty",
    "type": "National Monument"
  }
}
```

**2. Resulting Location Protocol Payload**

```json
{
  "specVersion": "1.0",
  "srs": "EPSG:4326",
  "locationType": "geojson",
  "location": {
    "type": "Point",
    "coordinates": [-74.0445, 40.6892]
  },
  "metadata": {
    "name": "Statue of Liberty",
    "type": "National Monument"
  },
  "eventTimestamp": "2025-06-25T23:36:00Z"
}
```

#### Conversion Flow

The following diagram illustrates the migration workflow.

```mermaid
graph TD
    A[GeoJSON Feature] --> B{Extract geometry};
    A --> C{Extract properties};
    B --> D[LP 'location' field];
    C --> E[LP 'metadata' field];
    F[Set LP 'locationType' = 'geojson'] --> G{Construct Location Protocol Payload};
    D --> G;
    E --> G;
    H[Set LP 'srs' = 'EPSG:4326'] --> G;
```

### Interoperability Matrix

The Location Protocol's features are designed to map clearly onto capabilities defined in major geospatial standards.

| Location Protocol Feature                | GeoJSON (RFC 7946) | EPSG         |
| :--------------------------------------- | :----------------- | :----------- |
| **Base Fields** (`srs`, `locationType`)  | Partial Support    | Full Support |
| **Location Types** (`geojson`, etc.)     | Full Support       | N/A          |
| **Composable Fields** (`metadata`, etc.) | Full Support       | N/A          |

- **GeoJSON**: Fully supports encapsulating `geometry` and `properties` objects. The `crs` member was removed from the GeoJSON spec, but the Location Protocol's `srs` field provides explicit support for coordinate system definition.
- **EPSG**: Fully supported via the `srs` field to define the coordinate reference system for any `locationType`, ensuring unambiguous spatial context.

### Compatibility and Best Practices

When integrating the Location Protocol with systems that consume GeoJSON, adhere to the following notes to ensure compatibility.

- **Coordinate Reference System**: To maintain strict GeoJSON (RFC 7946) compatibility, the `srs` field **MUST** be set to `"EPSG:4326"`. While the Location Protocol supports other systems, `"EPSG:4326"` is the only valid value when interoperating with standard GeoJSON tools.
- **Coordinate Order**: GeoJSON mandates a coordinate order of **longitude, latitude** for geographic coordinates. Payloads must conform to this order when `locationType` is `geojson`.
- **Unsupported Mappings**: The Location Protocol does not directly map to a GeoJSON `FeatureCollection`. To handle multiple locations, multiple Location Protocol attestations should be created—one for each feature.
- **Protocol as a Wrapper**: Remember that a Location Protocol payload is a _wrapper_ for geospatial data, not a replacement for it. The payload adds context, versioning, and verifiability around a standard data format like GeoJSON.

---

[:material-arrow-left: Back to Appendices Overview](index.md){ .md-button .md-button--primary }
