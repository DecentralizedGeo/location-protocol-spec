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
  "Schema Components": {
    "schemaUID": "0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a",
    "schemaString": "string srs, string locationType, string location, uint8 specVersion"
  }
}
```

This schema conforms to the base data model for creating location attestation objects.

### Step 2: Prepare a location attestation object

At it's core, attesting is a way to make a claim about some data. In this case, the claim is about a location. Whether that's a physical address, a GPS coordinate, or some other [form of location data](./location-attestation.md/#supported-location-types). As mentioned above, the `schemaString` defines the structure of the data that will be attested. Let's assign some values to the fields in the schema:

```json
{
  "locationAttestationObject": {
    "srs": "EPSG:4326",
    "locationType": "decimalDegrees",
    "location": "44.967243, -103.771556",
    "specVersion": 1
  }
}
```

### Step 3: Encode the location attestation object

Before creating the attestation object, you need to encode the data according to the schema. The encoding process ensures it conforms to the structure defined by the schema associated with the attestation. Why is the encoding necessary?

**On-chain Validation**: Smart contracts rely on structured data to verify the integrity and correctness of an attestation. The SchemaEncoder ensures the data adheres to the schema's format, making it possible for on-chain logic (e.g., verification or revocation) to process the data reliably.

**Consistency and Interoperability**: By encoding data according to a defined schema, different systems and parties can interpret and validate the data uniformly, ensuring compatibility across applications and platforms.

We'll take the `locationAttestationObject` and encode it using the schemaString. Here's what our encoded location attestation object looks like:

```string
0x000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000009455053473a343332360000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e646563696d616c44656772656573000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001634342e3936373234332c202d3130332e37373135353600000000000000000000
```

> You can verify this encoding with any ETH ABI Decoder tool such as [this](https://adibas03.github.io/online-ethereum-abi-encoder-decoder/decode). All you need to do is paste the encoding into the input box and enter the schema field types in the order they appear in the schema string. For example, for the above encoding, you would enter `string, string, string, uint8` as the types.

### Step 4: Create the attestation object

At this point, we are now ready to create the attestation object. The attestation object contains the data, representing the encoded location attestation object, and the required EAS properties. Here's an example of the structure of an attestation object:

```json
{
  "attestation object": {
    "schemaUID": "0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a",
    "schemaString": "string srs, string locationType, string location, unit8 specVersion",
    "recipient": "0x1234567890abcdef1234567890abcdef12345678",
    "data": "encodedLocationAttestationObject"
    }
}
```

After the attestation is signed, submitted and added to the blockchain, a UID is generated, that can be used to query the attestation and view it's details. Here's an attestation for the location attestation object we created above.

**Attestation UID**: 0x628f06c011351ef39b419718f29f20f0bc62ff3342d1e9c284531bf12bd20f31

**EAS Explorer Link**:  https://sepolia.easscan.org/attestation/view/0x628f06c011351ef39b419718f29f20f0bc62ff3342d1e9c284531bf12bd20f31

