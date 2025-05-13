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
| locationType | `string` | The type of location data being represented. |
| srs | `string` | The spatial reference system used to represent the location data. |
| location | `string`, `int` | The actual location data |
| specVersion | `uint8` | The version of the specification used to generate the attestation. |

#### Supported location types

The `locationType` field identifies the type of location data being represented. The following location types are supported:

| Location Type | Type | Additional Details | Example |
|----------------|------|-------------------|---------|
| latlong | `string` | A comma separated Latitude and longitude coordinates. | `37.7749, -122.4194` |
| GeoJSON | `string` | A GeoJSON object representing a geographic feature. | `{ "type": "Point", "coordinates": [ -122.4194, 37.7749 ] }` |
| wkt | `string` | A WKT (Well-Known Text) representation of a geometric object. | `POINT(-122.4194 37.7749)` |
| H3 | `string` | An H3 index representing a geographic location. | `8928308280fffff` |
| geohash | `string` | A geohash string representing a geographic location. | `u4pruyd` |
| W3W | `string` | A What3Words address representing a location. | `apple.banana.orange` |

### Composable fields

A location attestation object can be composed of each representing a different aspect of the location data. These sub-objects can be used to provide additional context or information about the location data.

> Note: The fields marked with :heavy_check_mark: have common overlap with their EAS counterparts and that are included in the location attestation object by default.

#### Common fields

The location attestation object supports additional fields that are common to all location attestations but not necessary to use. These fields provide additional information about the attestation and its context.

| Field Name | Type | Description | Common EAS Field |
|------------|------|-------------|-------------|
| media | `bytes` | The media type of the location data. | |
| attributes | `string` | Additional attributes of the location data. | |
| eventTimeStamp | `uint64` | The UNIX timestamp of the event associated with the location data. _Note, this should not be confused with the `time` field that represents when the attestation was created_. | |
| attributesSchema | `string` | The schema used to define the attributes of the location data. | :heavy_check_mark: `schemaString` |
| attributeSchemaUID | `byte32` | The unique identifier of the attribute schema. | :heavy_check_mark: `schemaUID` |
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

The fields marked with :heavy_check_mark: are common EAS fields that are included in the location attestation object. The other fields are specific to the location protocol framework and are not part of the EAS standard.

#### Proof fields

The location attestation object supports additional verification properties that can be used _prove_ the authenticity and integrity of the location data. These properties are optional but recommended for use cases that require a higher level of assurance.

| Field Name | Type | Description | Common EAS Field |
|------------|------|-------------|-------------|
| proof | `byte32` | The proof of the authenticity and integrity of the location data. | |
| proofType | `string` | The type of proof used to verify the location data. | |
| proofVersion | `uint8` | The version of the proof used to verify the location data. | |
| prooverAddress | `address` | The address of the prover who generated the proof. | :heavy_check_mark: `attester`|
| proofTime | `uint64` | The timestamp of when the proof was generated. | :heavy_check_mark: `time` |
