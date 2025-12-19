## Appendix: Spatial Reference Systems, URI Identifiers, and Coordinate Order

This appendix provides authoritative guidance on the use of Spatial Reference System (SRS) and Coordinate Reference System (CRS) identifiers within the Location Protocol. It establishes formal procedures for CRS selection, the deprecation of legacy shorthand codes, the use of URI and URN identifiers, and the handling of coordinate order to ensure unambiguous interpretation of spatial data.

### Deprecation of Legacy Shorthand Codes

The Location Protocol deprecates the use of shorthand CRS codes, such as `EPSG:4326`, in favor of fully-qualified URI (Uniform Resource Identifier) or URN (Uniform Resource Name) identifiers. While shorthand codes have been widely used, they introduce ambiguity and are not aligned with modern web standards for the following reasons:

* **Ambiguity of Coordinate Order:** Shorthand codes often do not explicitly define the coordinate order (`latitude, longitude` vs. `longitude, latitude`), which has been a persistent source of errors in geospatial data processing. For example, while the traditional GIS order for EPSG:4326 is `latitude, longitude`, many web-oriented systems, including GeoJSON, default to `longitude, latitude`.
* **Lack of Machine-Readability:** Shorthand codes are not inherently machine-readable or resolvable on the web. They are simply strings that require prior knowledge or external lookup tables to be understood by software. URIs, on the other hand, can be dereferenced to access a full, machine-readable definition of the CRS.
* **Inconsistent Implementations:** The same shorthand code can have different interpretations and implementations across different software libraries and systems. This can lead to subtle but significant discrepancies in coordinate transformations and data alignment.
* **Limited Expressiveness:** Shorthand codes cannot capture the full range of parameters and transformations that may be associated with a CRS, especially for complex or custom systems.

For these reasons, the Location Protocol **requires** the use of URI or URN identifiers for specifying Coordinate Reference Systems. This aligns with the "Spatial Data on the Web Best Practices" from the W3C and OGC, and the principles of Linked Data.

### Selecting a Coordinate Reference System

Choosing the right CRS is crucial for ensuring the accuracy and interoperability of spatial data. The choice of CRS depends on the specific use case, the geographic extent of the data, and the requirements of the applications that will consume the data.

#### Common Use Cases and Recommended CRS

| Use Case | Recommended CRS | Rationale |
| :-- | :-- | :-- |
| **Global Point Data** | WGS 84 (CRS84) | The standard for global latitude and longitude data, used by GPS and widely supported in web applications. |
| **Web Map Tiles** | Web Mercator | The de facto standard for web mapping services like Google Maps, Bing Maps, and OpenStreetMap. It is a projected CRS that is optimized for displaying maps on a flat screen. |
| **Local Projected Data** | National or Regional Grids | For high-precision applications within a specific country or region, a local projected CRS is often more accurate than a global system. Examples include the British National Grid (EPSG:27700) or State Plane Coordinate Systems in the US. |

When in doubt, **WGS 84 (CRS84) with `longitude, latitude` coordinate order is the recommended default** for vector data in the Location Protocol, as it is the standard for GeoJSON and many other web-based formats.

### CRS Identifiers: URIs and URNs

A URI or URN provides a globally unique and persistent identifier for a CRS. These identifiers are resolvable on the web, allowing both humans and machines to access a detailed definition of the CRS, including its parameters, datum, and coordinate system.

#### Canonical URI Patterns

The Open Geospatial Consortium (OGC) maintains a registry of CRS definitions and provides a standard URI pattern for referencing them. The general pattern is:

```
http://www.opengis.net/def/crs/{authority}/{version}/{code}
```

Here are some examples of replacing shorthand codes with their canonical OGC URIs:

| Shorthand Code | Canonical URI |
| :-- | :-- |
| `EPSG:4326` | `http://www.opengis.net/def/crs/EPSG/0/4326` |
| `EPSG:3857` | `http://www.opengis.net/def/crs/EPSG/0/3857` |
| `CRS:84` | `http://www.opengis.net/def/crs/OGC/1.3/CRS84` |

While the OGC registry is the recommended source for CRS URIs, other registries, such as the IGN France CRS registry, may also be used, as long as they provide stable, resolvable, and machine-readable definitions.

### Coordinate Order: `lon, lat` vs. `lat, lon`

The order of coordinates (`longitude, latitude` vs. `latitude, longitude`) is a common source of confusion and errors in geospatial data. The Location Protocol aims to be explicit about coordinate order to prevent such issues.

The following table summarizes the expected coordinate order in different contexts:

| Context | Expected Coordinate Order | Notes |
| :-- | :-- | :-- |
| **CRS Registries (e.g., EPSG)** | `latitude, longitude` | The traditional order in many GIS databases and standards. |
| **Wire Formats (e.g., GeoJSON)** | `longitude, latitude` | The standard for GeoJSON, as defined in RFC 7946. |
| **Frontend Mapping Libraries** | Varies | Leaflet and Mapbox GL JS generally expect `[longitude, latitude]`, while OpenLayers can be configured to handle different orders. Always consult the documentation of the specific library. |

**The Location Protocol defaults to the `longitude, latitude` order for all coordinate data, in alignment with the GeoJSON specification.** When a different coordinate order is used, it **must** be explicitly declared in the CRS definition.

### Integration Guidance for Implementers

Implementers of the Location Protocol should follow these guidelines to ensure proper handling of CRS and coordinate order:

#### Accepting and Normalizing CRS Identifiers

* **At the boundaries of a system (e.g., API endpoints), implementations SHOULD accept only URI/URN identifiers for CRS.** Shorthand codes SHOULD be rejected with an appropriate error message.
* **If an implementation chooses to accept shorthand codes for backward compatibility, it MUST normalize them internally to their canonical URI/URN counterparts.** This normalization should be based on a curated and well-documented mapping of a limited set of common shorthand codes to their URIs.

#### Declaring CRS and Coordinate Order

* **All APIs and data schemas that expose Location Protocol data MUST unambiguously declare the CRS and coordinate order.** This can be done using a dedicated field in the API response or schema definition, which contains the full URI of the CRS.
* **When using GeoJSON, the `crs` member is deprecated.** The CRS is assumed to be WGS 84 (CRS84) with `longitude, latitude` coordinates. If a different CRS is used, it must be declared outside of the GeoJSON object itself, for example, in the API response header or in the documentation.

#### Interfacing with Legacy Systems

* When interfacing with systems that still use shorthand codes (e.g., `proj4js`), implementations should use a mapping library or function to convert between shorthand codes and URIs.
* Migration strategies should be developed to phase out the use of shorthand codes over time, in favor of URIs.

### Reference Implementation (Pseudocode)

The following pseudocode examples illustrate how to implement some of the key functionalities for handling CRS identifiers and coordinate order.

#### Mapping Shorthand Codes to URIs

```python
function mapShorthandToUri(shorthand: string): string | null {
  const mapping = {
    "EPSG:4326": "http://www.opengis.net/def/crs/EPSG/0/4326",
    "EPSG:3857": "http://www.opengis.net/def/crs/EPSG/0/3857",
    "CRS:84": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
  };

  return mapping[shorthand] || null;
}
```

#### Validating a CRS URI

```python
import re

function isValidCrsUri(uri: string): boolean {
  // A simple regex to check for a valid OGC URI pattern.
  // A more robust implementation would involve actually resolving the URI
  // and checking for a valid GML or other machine-readable definition.
  const ogcPattern = /^http:\/\/www\.opengis\.net\/def\/crs\/\w+\/\d+(\.\d+)*\/\w+$/;
  return re.test(ogcPattern, uri);
}
```

#### Verifying and Enforcing Coordinate Order

```python
function enforceLonLatOrder(coordinates: number[], crsUri: string): number[] {
  // This is a simplified example. A real implementation would need to
  // parse the CRS definition to determine the correct axis order.
  const crsWithLatLonOrder = [
    "http://www.opengis.net/def/crs/EPSG/0/4326"
    // ... add other CRSs with lat, lon order here
  ];

  if (crsWithLatLonOrder.includes(crsUri)) {
    // Swap the coordinates if the CRS expects lat, lon order.
    return [coordinates[1], coordinates[0]];
  }

  return coordinates;
}
```

### Supporting Resources

The following resources provide further information on SRS/CRS, URI identifiers, and coordinate order. Implementers are encouraged to consult these documents for a deeper understanding of these topics.

* [OGC API - Features - Part 1: Core](https://docs.ogc.org/is/17-069r3/17-069r3.html)
* [OGC API - Features - Part 2: Coordinate Reference Systems by Reference](https://docs.ogc.org/is/18-058/18-058.html)
* [W3C Spatial Data on the Web Best Practices](https://www.w3.org/TR/sdw-bp/)
* [RFC 7946: The GeoJSON Format](https://datatracker.ietf.org/doc/html/rfc7946)
* [EPSG Geodetic Parameter Dataset](https://epsg.org/)
* [The Google Maps / Bing Maps Spherical Mercator Projection](https://alastaira.wordpress.com/2011/01/23/the-google-maps-bing-maps-spherical-mercator-projection/)
* [Working with projections in Leaflet](https://rstudio.github.io/leaflet/articles/projections.html)
