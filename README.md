# Location Protocol Specification

[![Netlify Status](https://api.netlify.com/api/v1/badges/005c5473-4983-4835-a8b3-976f50ea0745/deploy-status)](https://app.netlify.com/projects/protocol-spec-docs/deploys)

**A minimal, portable, implementation-agnostic standard for representing location data across decentralized and centralized systems.**

## Why Location Protocol?

### The Problem

Existing geospatial data standards—GeoJSON, KML, STAC, Overture—are powerful tools for representing and exchanging spatial information. However, they were designed for **centralized data systems** and don't address the core requirements of **decentralized, verifiable, user-controlled location data**:

- **No standard for portable, signed location claims**: Applications need to prove "I was here" or "this happened here" in ways that can be verified across systems, but there's no interoperable way to do this.
- **Ambiguous parsing across implementations**: When location data moves between Ethereum, ATProto, IPFS, or traditional databases, critical context (like coordinate reference systems or data formats) is often lost or interpreted inconsistently.
- **Overly rigid for decentralized use cases**: Existing standards prescribe specific data models (e.g., GeoJSON locks you to WGS84) that don't work across Earth-based, metaverse, or symbolic location contexts.
- **Difficult to extend safely**: Adding new fields or proof mechanisms to established formats risks breaking compatibility or creating vendor-specific forks.

**The Location Protocol solves this by defining the absolute minimum fields required for spatial interoperability**, while enabling extensions for proofs, media, attributes, and implementation-specific needs.

### What Makes Location Protocol Different?

| Standard | Purpose | Key Limitation for Decentralized Systems |
|---|---|---|
| **GeoJSON** | Represents geometries and features | Locked to WGS84; no built-in support for verification, proofs, or non-Earth coordinate systems |
| **KML** | Google Earth visualization | XML-based, visualization-focused, not designed for verifiable claims or programmatic interop |
| **STAC** | Catalog spatiotemporal assets (satellite imagery, etc.) | Heavy metadata model designed for asset catalogs, not minimal location claims |
| **Overture Maps** | Open map data exchange | Focuses on map features and schema, not portable signed location records |
| **Location Protocol** | **Minimal, verifiable, portable location records** | **Implementation-agnostic base layer with 4 required fields; supports both signed and unsigned records; extensible for any use case** |

### Core Design Principles

1. **Minimal Base Fields**: Only 4 required fields (`lp_version`, `srs`, `location_type`, `location`) ensure maximum portability
2. **Implementation Agnostic**: Works across Ethereum, ATProto, IPFS, traditional databases, and future systems
3. **OGC-Aligned**: Uses OGC URI standards for spatial reference systems to eliminate axis-order ambiguity
4. **Signed or Unsigned**: Supports both cryptographically signed attestations and plain location records
5. **Extensible by Design**: Optional composable fields (media, attributes, proofs, timestamps) without breaking core compatibility
6. **Namespace Clean**: Uses `lp_` prefix and snake_case to avoid collisions when embedded in other specs (e.g., STAC Items)

## Who Is This For?

- **Decentralized application developers** building on Ethereum, ATProto, Farcaster, Nostr, or other decentralized protocols
- **Geospatial data systems** that need interoperability between centralized and decentralized infrastructure
- **Impact verification platforms** (dMRV, Hypercerts, Gitcoin) that require portable proof-of-location
- **Social and check-in apps** that want user-controlled, verifiable location data
- **Field data collection tools** (biodiversity monitoring, environmental sensing) that need to attach rich attributes to locations

## What's in This Repository

**[📖 Full Specification](./docs/spec-page/)** — Complete formal specification with schemas, validation rules, and examples

**[🏗️ Implementation Guides](./docs/spec-page/appendices/)** — How to implement Location Protocol using EAS, ATProto, and other systems

**[🗂️ Location Type Registry](./docs/spec-page/specification/location-types.md)** — Supported spatial data formats (GeoJSON, H3, coordinates, etc.)

## Quick Example

```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  "location_type": "geojson",
  "location": {
    "type": "Point",
    "coordinates": [-122.4194, 37.7749]
  }
}
```

That's it. Four fields. Parseable anywhere. Optionally signable. Endlessly extensible.

## Get Started

- **Read the spec**: [docs.astral.global/location-protocol](https://docs.astral.global/location-protocol)
- **Implement it**: See [EAS Integration Guide](./docs/spec-page/appendices/eas-integration.md)
- **Contribute**: Open an issue or PR with proposed extensions or implementations
- **Join the discussion**: [GitHub Discussions](https://github.com/DecentralizedGeo/location-protocol-spec/discussions)
