# Location Protocol Specification

[![Netlify Status](https://api.netlify.com/api/v1/badges/005c5473-4983-4835-a8b3-976f50ea0745/deploy-status)](https://app.netlify.com/projects/protocol-spec-docs/deploys)

**A minimal envelope for making location data portable, verifiable, and unambiguous across any system.**

## What Is This?

Location Protocol is **not another geospatial data format**. It's a thin wrapper around existing formats (GeoJSON, H3, WKT, coordinates, etc.) that adds the metadata needed to make location data:

- ✅ **Portable** across Ethereum, ATProto, IPFS, databases, and future systems
- ✅ **Verifiable** through optional cryptographic signatures
- ✅ **Unambiguous** with explicit versioning, coordinate systems, and format identifiers
- ✅ **Extensible** with structured attributes, media, and proof mechanisms

**You already use GeoJSON, KML, or H3?** Location Protocol wraps them with 4 required fields so they work everywhere.

## The Problem We're Solving

Existing geospatial standards (GeoJSON, KML, WKT, H3) are excellent at representing spatial data. **The problem isn't the formats themselves**—it's that they lack a standardized way to:

1. **Indicate which format is being used** - Is this GeoJSON? Coordinates? H3? Parsers have to guess.
2. **Specify the coordinate system unambiguously** - GeoJSON assumes WGS84, but which axis order? What about other planets? Metaverse coordinates?
3. **Make location data verifiable** - How do you cryptographically sign a location claim in a way that works across Ethereum, ATProto, and traditional systems?
4. **Attach contextual metadata** - Timestamps, media, structured attributes, proofs—but without breaking compatibility.
5. **Version the specification** - When the protocol evolves, how does a parser know which rules to apply?

**Location Protocol provides the missing envelope.** It doesn't replace GeoJSON—it tells you "this is GeoJSON v1.0.0 in WGS84 lon/lat order, signed by Alice, with a photo attached."

## How It Works

Location Protocol defines **4 required fields** that wrap your spatial data:

```json
{
  "lp_version": "1.0.0",              // Which version of this spec
  "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",  // Coordinate system (OGC standard URI)
  "location_type": "geojson",         // What format is inside
  "location": {                        // Your actual GeoJSON/H3/WKT/coordinates
    "type": "Point",
    "coordinates": [-122.4194, 37.7749]
  }
}
```

**That's it.** Four fields. Then you can optionally add:
- `event_timestamp` - When this happened
- `media_data` / `media_type` - Attach photos, videos
- `attributes` / `attributes_schema` - Structured metadata (species observations, sensor readings, etc.)
- `proof` - Cryptographic evidence or verification data

## What Location Protocol Is NOT

❌ **Not a replacement for GeoJSON/KML/WKT** - We use these formats inside the `location` field
❌ **Not a new coordinate system** - We use OGC-standard SRS URIs
❌ **Not blockchain-specific** - Works on Ethereum, ATProto, IPFS, PostgreSQL, anywhere
❌ **Not trying to be STAC** - STAC is for asset catalogs; we're for minimal location claims

## Why Not Just Use GeoJSON/KML/H3 Directly?

**You can!** But when you need to:
- Share location data between **Ethereum and ATProto** and have it mean the same thing
- **Cryptographically sign** a location claim and verify it anywhere
- Support **non-Earth coordinate systems** (Mars, metaverse, game worlds)
- Attach **structured attributes** (field observations, sensor data) in a standard way
- Work with **multiple spatial formats** in the same system (GeoJSON + H3 + coordinates)
- **Version your data** so parsers know which validation rules to apply

...you need a thin, standardized wrapper. That's Location Protocol.

## Design Principles

1. **Format Agnostic**: Works with GeoJSON, H3, WKT, coordinates, addresses, geohash—anything spatial
2. **Implementation Agnostic**: Deploy on Ethereum, ATProto, IPFS, PostgreSQL, S3, anywhere
3. **OGC Standards**: Uses official OGC URIs for coordinate systems (no more axis-order ambiguity)
4. **Optionally Verifiable**: Add cryptographic signatures when you need them, skip them when you don't
5. **Minimalist Core**: Only 4 required fields; everything else is optional
6. **Safely Extensible**: Add attributes, media, proofs without breaking parsers

## Use Cases

- **Decentralized social apps** - Location check-ins that work across Bluesky, Farcaster, and Lens
- **Impact verification** - Signed location proofs for carbon credits, biodiversity monitoring, grants (dMRV, Hypercerts, Gitcoin)
- **Field data collection** - Attach structured attributes (species, measurements, conditions) to location records
- **Cross-chain applications** - Location data that works on Ethereum, Base, Optimism, Celo, and beyond
- **Interoperable systems** - Bridge between Web2 databases and Web3 protocols without data loss
- **Non-Earth contexts** - Metaverse coordinates, Mars missions, game worlds—anywhere spatial data exists

## What's in This Repository

**[📖 Full Specification](./docs/spec-page/)** — Complete formal specification with schemas, validation rules, and examples

**[🏗️ Implementation Guides](./docs/spec-page/appendices/)** — How to implement Location Protocol using EAS, ATProto, and other systems

**[🗂️ Location Type Registry](./docs/spec-page/specification/location-types.md)** — Supported spatial data formats (GeoJSON, H3, coordinates, etc.)

## Examples

**Minimal GeoJSON location:**
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

**H3 cell with timestamp:**
```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/EPSG/0/4326",
  "location_type": "h3",
  "location": "8928308280fffff",
  "event_timestamp": 1735689600
}
```

**Field observation with structured attributes:**
```json
{
  "lp_version": "1.0.0",
  "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
  "location_type": "geojson",
  "location": { "type": "Point", "coordinates": [-103.771556, 44.967243] },
  "attributes": "{\"species\": \"Pinus ponderosa\", \"height_m\": 18.2, \"dbh_cm\": 45.3}",
  "attributes_schema": "json:inline:eyJ0eXBlIjoib2JqZWN0In0="
}
```

Four required fields. Infinite extensions. Works everywhere.

## Get Started

- **Read the spec**: [docs.astral.global/location-protocol](https://docs.astral.global/location-protocol)
- **Implement it**: See [EAS Integration Guide](./docs/spec-page/appendices/eas-integration.md)
- **Contribute**: Open an issue or PR with proposed extensions or implementations
- **Join the discussion**: [GitHub Discussions](https://github.com/DecentralizedGeo/location-protocol-spec/discussions)
