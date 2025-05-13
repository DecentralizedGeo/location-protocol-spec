# Location Attestation Specification

## Overview

This document defines the standard formatting and rules for generating location attestations.

## The Location Attestation Object

A location attestation object is a geospatial data artifact that includes a digital signature that verifies the authenticity and integrity of an arbitrary metadata object. At minimum it conforms to the [base data model](#base-fields) and can be extended with the [composable fields](#composable-fields) to provide more context or information.

### Base fields

The location attestation object at a minimum must contain the fields below as to identify and represent the location data.

The locationType field is a string that identifies the type of location data being represented. The srs field is a string that identifies the spatial reference system used to represent the location data. The location field contains the actual location data.

| Field Name | Type | Description |
|------------|------|-------------|
| srs[^1] | `string` | The spatial reference system used to represent the location data. |
| locationType | `string` | The type of location data being represented. |
| location | `string`, `int40[2]`, `int40[2][]`, `int40[2][][]` | The actual location data |
| specVersion | `uint8` | The version of the specification used to generate the attestation. |

[^1]: It is recommended that the `srs` field conforms to EPSG code (e.g. `EPSG:4326`), OGC URN (e.g. `urn:ogc:def:crs:OGC:1.3:CRS84`), or a well-known identifier for the spatial reference system.

#### Supported location types

The `locationType` field identifies the type of location data being represented. The following location types are supported:

| Location Type | Additional Details | Data Type | Example |
|----------------|-------------------|------|---------|
| decimalDegrees | Comma separated Latitude and longitude decimal degree coordinates | `string` | `37.7749, -122.4194` |
| dms | Latitude and longitude coordinates in degrees, minutes, and seconds | `string` | `37°46'30.0"N 122°25'10.0"W` |
| scaledCoordinates[^2] | A scaled integer representation of coordinate pairs, representing points lines or polygons | `int40[2]`, `int40[2][]`, `int40[2][][]` | `[[-74000000, 40700000], [-74100000, 40700000], [-74100000, 40800000], [-74000000, 40800000], [-74000000, 40700000]]` |
| geoJson | A GeoJSON object representing a geographic feature as points lines or polygons | `string` | `{ "type": "Point", "coordinates": [ -122.4194, 37.7749 ] }` |
| wkt | A WKT (Well-Known Text) representation of a geometric object as points lines or polygons | `string` | `POINT(-122.4194 37.7749)` |
| placeNames | Known place names | `string` | `San Francisco, CA`, `Eiffel Tower` |
| address | Standard mailing address | `string` | `1600 Amphitheatre Parkway, Mountain View, CA 94043` |
| h3 | A hierarchical hexagonal grid system used for spatial indexing | `string` | `8928308280fffff` |
| geohash | A hierarchical spatial data structure which subdivides space into buckets of grid shape | `string` | `u4pruyd` |
| w3w | A geocoding system that encodes geographic coordinates into three dictionary words | `string` | `apple.banana.orange` |
| mgrs | A military grid reference system used for geospatial referencing | `string` | `33TWN0000000000` |
| utm | A universal transverse mercator coordinate system used for mapping | `string` | `33TWN0000000000` |
| spcs | Comma separated x, y coordinates in a state plane coordinate system | `string` | `2000000, 500000` in a specific state plane zone |

[^2]: It's up to the implementor to set the precision and provide guidance on the default precision to be used. The maximum coordinate precision that can be set is 10⁹ as `int40` can store values up to ±549,755,813. For example, a coordinate of `123.456` with a precision of 10¹⁰ would exceed the maximum value of `int40` and would not be valid.

The `location` value is interpreted based on the `locationType` field. Implementations should not attempt to decode without first resolving `locationType`.

### Composable fields

A location attestation object can be composed of each representing a different aspect of the location data. These sub-objects can be used to provide additional context or information about the location data.

> Note: The fields marked with :heavy_check_mark: have common overlap with their EAS counterparts and are included in the location attestation object by default.

#### Common fields

The location attestation object supports additional fields that are common to all location attestations but not necessary to use. These fields provide additional information about the attestation and its context.

| Field Name | Type | Description | Common EAS Field |
|------------|------|-------------|-------------|
| media | `bytes`, `mediaType` | bytes array representing the media data associated with the location data. The `mediaType` is a MIME-type-style string describing the media data. | |
| attributes | `string` | Additional attributes of the location data. | |
| eventTimeStamp | `uint64` | The UNIX timestamp of the event associated with the location data. _Note, this should not be confused with the `time` field that represents when the attestation was created_. | |
| attributesSchema | `string` | The schema used to define the attributes of the location data. | :heavy_check_mark: `schemaString` |
| attributeSchemaUID | `byte32` | The unique identifier of the attribute schema. | :heavy_check_mark: `schemaUID` |
| recepient | `address` | The address of the recipient of the attestation. | :heavy_check_mark: `recipient` |
| memo | `string` | An arbitrary message or note. | |

#### Common EAS fields

The location protocol framework is a geospatial extension of Ethereum based on the EAS (Ethereum Attestation Service) standard. The following fields are common to all EAS attestations and are included in the location attestation object:

| Field Name | Type | Description |
|------------|------|-------------|
| uid | `byte32` | The unique identifier of the attestation. |
| schemaString | `string` | The schema string that defines the structure of the data to be attested. |
| schemaUID | `byte32` | The unique identifier of the schema associated with the attestation. |
| refUID | `byte32` | The reference UID of the attestation, if any. |
| time | `uint64` | The UNIX timestamp of when the attestation was created. |
| expirationTime | `uint64` | The Unix timestamp when the attestation expires (0 for no expiration). |
| revocationTime | `uint64` | The Unix timestamp when the attestation was revoked, if applicable. |
| recipient | `address` | The address of the recipient of the attestation. |
| attester | `address` | The address of the attester who created the attestation. |
| revocable | `bool` | A boolean indicating whether the attestation is revocable or not. |


#### Proof fields

The location attestation object supports additional verification properties that can be used _prove_ the authenticity and integrity of the location data. These properties are optional but recommended for use cases that require a higher level of assurance.

| Field Name | Type | Description | Common EAS Field |
|------------|------|-------------|-------------|
| proof | `byte32` | The proof of the authenticity and integrity of the location data. | |
| proofType | `string` | The type of proof used to verify the location data. | |
| proofVersion | `uint8` | The version of the proof used to verify the location data. | |
| prooverAddress | `address` | The address of the prover who generated the proof. | :heavy_check_mark: `attester`|
| proofTime | `uint64` | The timestamp of when the proof was generated. | :heavy_check_mark: `time` |
