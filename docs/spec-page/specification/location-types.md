## Location Format Types

The Location Protocol is designed for flexibility, allowing location data to be represented in various formats. The `location_type` field is a mandatory string in the base data model that specifies the format of the data contained within the `location` field. This identifier is essential for interoperability, ensuring that any consuming application can correctly interpret the spatial information.

While the protocol is "extensible by design" to support custom formats, a standardized naming convention is proposed to ensure consistency, prevent collisions, and support versioning.

### Standardized Naming Convention

To support a scalable and interoperable registry of location types, all new and standardized identifiers should follow a consistent naming convention. This structure clearly distinguishes between core protocol types and community-provided extensions, and it incorporates versioning to manage changes over time.

The recommended pattern is:
`<namespace>.<type>.v<major>`

- **Namespace**: A prefix indicating the origin and stability of the type.
  - `lp`: Reserved for core types officially maintained and guaranteed by the Location Protocol.
  - `community`: Used for experimental or specialized types submitted by the community for broader use.
- **Type**: A descriptive, lowercase string identifying the data format (e.g., `coordinate-decimal`, `geojson-point`).
- **v<major>**: A major version number, prefixed with `v`, to denote the revision of the type's specification. This is incremented only for backward-incompatible changes.

### Location Type Registry

The current implementation uses simple, unversioned string identifiers for `location_type`. A formal registry is in development to standardize these types and manage future extensions. The following table lists the currently supported types and their proposed standardized identifiers for future releases.

| Supported Location Types    | Description                                                                                                                                          |
| :-------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| `coordinate-decimal`        | A pair of decimal degree coordinates. Default order is latitude, longitude. A `+lon-lat` modifier can be used for explicit longitude-first ordering. |
| `geojson` / `geojson-point` | A GeoJSON Geometry object representing a geographic feature. Supports all geometry types: Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, and GeometryCollection as defined in RFC 7946. |
| `h3`                        | An H3 geospatial index representing a hexagonal cell.                                                                                                |
| `geohash`                   | A Geohash string representing a geographic bounding box.                                                                                             |
| `wkt`                       | A Well-Known Text (WKT) representation of a geometric object.                                                                                        |
| `address`                   | A standard mailing or street address.                                                                                                                |
| `scaledCoordinates`         | A scaled integer representation of coordinate pairs, representing points, lines, or polygons.                                                        |

### Usage Examples

The following examples demonstrate how to structure a Location Protocol payload for different location types, using the current, unversioned identifiers.

#### `coordinate-decimal`

Represents a single geographic point using decimal degrees.

```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  "location_type": "coordinate-decimal",
  "location": [-103.771556, 44.967243]
}
```

#### `geojson-point`

Represents a single geographic point using a GeoJSON Point object.

```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  "location_type": "geojson-point",
  "location": {
    "type": "Point",
    "coordinates": [-103.771556, 44.967243]
  }
}
```

#### `geojson` (Polygon)

Represents a geographic boundary or area using a GeoJSON Polygon object. The first coordinate array defines the outer boundary; subsequent arrays define holes (if any).

```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  "location_type": "geojson",
  "location": {
    "type": "Polygon",
    "coordinates": [
      [
        [-103.771556, 44.967243],
        [-103.771556, 44.977243],
        [-103.761556, 44.977243],
        [-103.761556, 44.967243],
        [-103.771556, 44.967243]
      ]
    ]
  }
}
```

### Extensibility and Versioning

The protocol's extensibility allows developers to define and use custom location types for specific use cases. However, for broad interoperability, it is highly recommended to register new types.

**Proposing a New Type**

1. **Proposal**: Contributors can propose new types by submitting a request to the protocol's governance body, typically via a GitHub repository.
2. **Definition**: The proposal must include a detailed description of the format, validation rules, a clear use case, and a requested identifier under the `community` namespace (e.g., `community.my-custom-type.v1`).
3. **Review**: The proposal undergoes a community review. Once accepted, it is added to the official registry.

**Backward Compatibility**
The version number in the standardized identifier is crucial for managing changes. Any modification to a type's format that is not backward-compatible requires incrementing the major version number. Applications should be designed to handle specific versions and gracefully manage payloads with unsupported `locationType` identifiers to prevent data misinterpretation.

---

[:material-arrow-left: Back to Specification Overview](index.md){ .md-button .md-button--primary }
