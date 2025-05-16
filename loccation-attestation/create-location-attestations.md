# Creating Location Attestations

This document provides a guide for creating location attestation objects for the Ethereum Attestation Service (EAS). It covers the steps to create, sign, and verify location attestations.

## Making an attestation

### Step 1: Identify the schema

The first step in creating a location attestation is to identify the schema that will be used. The schema defines the structure of the attestation and the data it will contain. A schema in EAS is defined by:

- **Schema UID**: A unique identifier for the schema on the EAS schema registry.
- **Schema String**: The string representation of the schema, which includes the fields and their types.

To create a location attestation, you can use the following schema:

```json
{
  "schema": {
    "schemaUID": "0xe1fc76535d5ab7a4e107a63e068af0fe51bb19ca27b8d2dcff1711ca5f55855c",
    "schemaString": "string srs, string locationType, string location, unit8 specVersion"
  }
}
```

This schema conforms to the base data model for creating location attestation objects.

### Step 2: Encode the location attestation object

Before creating the attestation object, you need to encode the data according to the schema. The encoding process ensures it conforms to the structure defined by the schema associated with the attestation. This encoding step is crucial for validating and processing the attestation correctly on-chain

**Create example of encoding the location attestation object**

### Step 3: Create the attestation object

Once you have identified the schema, you can create the attestation object. The attestation object contains the data, representing the location attestation object, and the required EAS properties. Here's an example of the structure of an attestation object:

```json
{
  "attestation object": {
    "schemaUID": "0xe1fc76535d5ab7a4e107a63e068af0fe51bb19ca27b8d2dcff1711ca5f55855c",
    "schemaString": "string srs, string locationType, string location, unit8 specVersion",
    "recipient": "0x1234567890abcdef1234567890abcdef12345678",
    "data": "encodedLocationAttestationObject"
    }
}
```
