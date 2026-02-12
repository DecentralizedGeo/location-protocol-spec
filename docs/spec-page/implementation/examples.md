This guide provides practical code examples and implementation patterns for developers integrating the Location Protocol. The snippets cover the full lifecycle, from creating a payload to verifying an attestation, and are provided in JavaScript/TypeScript, Python, and Solidity to accelerate adoption.

## Payload Creation Examples

A `LocationPayload` is a structured JSON object containing location information. Before encoding and attestation, you must construct and validate this object.

### JavaScript/TypeScript

This example demonstrates creating a basic payload object and performing a simple validation check in TypeScript.

```typescript
// Define the structure of a Location Protocol Payload
interface LocationPayload {
  specVersion: string;
  srs: string;
  locationType: string;
  location: any;
  eventTimestamp?: string; // Optional field
  mediaData?: string; // Optional field for CIDs
  mediaType?: string; // Optional field for MIME types
}

// Create a new payload instance
const payload: LocationPayload = {
  specVersion: "1.0",
  srs: "EPSG:4326",
  locationType: "coordinate-decimal.lon-lat",
  location: [-74.006, 40.7128], // [longitude, latitude]
  eventTimestamp: new Date().toISOString(),
};

// Basic validation function
function validatePayload(p: LocationPayload): boolean {
  if (!p.specVersion || !p.srs || !p.locationType || !p.location) {
    console.error("Validation Error: Missing required fields.");
    return false;
  }
  console.log("Payload structure is valid.");
  return true;
}

// Assert validation passes
const isValid = validatePayload(payload);
console.assert(isValid, "Payload should be valid");
```

### Python

This Python example builds an equivalent payload using a dictionary and includes a validation function.

```python
import json
from datetime import datetime, timezone

# Create a payload as a Python dictionary
payload = {
    "lp_version": "1.0",
    "srs": "EPSG:4326",
    "location_type": "coordinate-decimal+lon-lat",
    "location": [-74.0060, 40.7128],
    "event_timestamp": datetime.now(timezone.utc).isoformat()
}

# Basic validation function
def validate_payload(p: dict) -> bool:
    """Checks for the presence of required fields in the payload."""
    required_fields = ["lp_version", "srs", "location_type", "location"]
    if not all(field in p for field in required_fields):
        print("Validation Error: Missing one or more required fields.")
        return False
    print("Payload structure is valid.")
    return True

# Assert validation passes
is_valid = validate_payload(payload)
assert is_valid, "Payload should be valid"

# Print the JSON representation
print(json.dumps(payload, indent=2))
```

## Encoding and Decoding

Location Protocol payloads are encoded for efficient and deterministic transport, especially for on-chain use. The standard encoding process is:

1. Serialize the JSON payload to a canonical binary representation using CBOR (RFC 8949).
2. Encode the resulting CBOR binary data into a Base64url string for safe text-based transport.

### JavaScript/TypeScript (Node.js)

This example uses the `cbor-x` and built-in `Buffer` modules.

```typescript
import { encode, decode } from "cbor-x";

// Payload from the previous example
const payload = {
  specVersion: "1.0",
  srs: "EPSG:4326",
  locationType: "coordinate-decimal.lon-lat",
  location: [-74.006, 40.7128],
};

// 1. Encode payload to CBOR
const cborData = encode(payload);

// 2. Encode CBOR to Base64url
const encodedPayload = Buffer.from(cborData).toString("base64url");
console.log("Encoded Payload:", encodedPayload);

// --- Decoding ---
// 1. Decode Base64url to CBOR
const decodedCbor = Buffer.from(encodedPayload, "base64url");

// 2. Decode CBOR to JSON object
const decodedPayload = decode(decodedCbor);
console.log("Decoded Payload:", decodedPayload);

// Assert that the round trip was successful
console.assert(
  JSON.stringify(payload) === JSON.stringify(decodedPayload),
  "Decoded payload must match original"
);
```

### Python

This example uses the `cbor2` and `base64` libraries.

```python
import cbor2
import base64
import json

payload = {
    "lp_version": "1.0",
    "srs": "EPSG:4326",
    "location_type": "coordinate-decimal+lon-lat",
    "location": [-74.0060, 40.7128]
}

# 1. Encode payload to CBOR
# Use canonical=True for deterministic output
cbor_data = cbor2.dumps(payload, canonical=True)

# 2. Encode CBOR to Base64url
# Standard base64 uses '+' and '/', urlsafe uses '-' and '_'
encoded_payload = base64.urlsafe_b64encode(cbor_data).rstrip(b'=').decode('utf-8')
print(f"Encoded Payload: {encoded_payload}")


# --- Decoding ---
# 1. Decode Base64url to CBOR
# Add padding back if it was stripped
padding = '=' * (-len(encoded_payload) % 4)
decoded_cbor = base64.urlsafe_b64decode(encoded_payload + padding)

# 2. Decode CBOR to Python object
decoded_payload = cbor2.loads(decoded_cbor)
print(f"Decoded Payload: {decoded_payload}")

# Assert that the round trip was successful
assert payload == decoded_payload, "Decoded payload must match original"
```

## Attestation Submission

Once encoded, the payload can be submitted as an attestation. The Ethereum Attestation Service (EAS) is the reference implementation for this process.

### EAS SDK (JavaScript/TypeScript)

The EAS SDK simplifies interaction with the EAS smart contracts. This example demonstrates creating an off-chain attestation, which is gas-efficient as it only stores a hash on-chain.

```typescript
import {
  EAS,
  Offchain,
  SchemaEncoder,
} from "@ethereum-attestation-service/eas-sdk";
import { ethers } from "ethers";

// --- Prerequisites ---
// 1. Configure EAS
const EAS_CONTRACT_ADDRESS = "0x..."; // EAS contract address on your target network
const eas = new EAS(EAS_CONTRACT_ADDRESS);

// 2. Connect a signer (e.g., from a browser wallet or private key)
const provider = new ethers.JsonRpcProvider(
  "https://sepolia.infura.io/v3/YOUR_API_KEY"
);
const signer = new ethers.Wallet("YOUR_PRIVATE_KEY", provider);
eas.connect(signer);

// 3. Define the schema for the Location Protocol payload
const schemaEncoder = new SchemaEncoder("string locationPayload");
const schemaUID = "0x..."; // UID of your registered schema

// --- Create Attestation ---
async function createLocationAttestation(encodedPayload: string) {
  const offchain = await eas.getOffchain();

  const attestationData = {
    recipient: ethers.ZeroAddress, // Or a specific recipient
    expirationTime: 0, // No expiration
    revocable: true,
    schema: schemaUID,
    data: schemaEncoder.encodeData([
      { name: "locationPayload", value: encodedPayload, type: "string" },
    ]),
  };

  try {
    const signedOffchainAttestation = await offchain.signOffchainAttestation(
      attestationData,
      signer
    );
    console.log("Signed Off-chain Attestation:", signedOffchainAttestation);

    // This signed attestation can now be shared or stored.
    // To make it publicly available, you can submit its hash to a timestamping service or an on-chain registry.

    return signedOffchainAttestation;
  } catch (error) {
    console.error("Error creating attestation:", error);
  }
}

// Encoded payload from the previous step
const encodedPayload =
  "p2xWc3BlY1ZlcnNpb25jMS4wc3Nyc2ppRVBTRzo0MzI2bWxvY2F0aW9uVHlwZXVjb29yZGluYXRlLWRlY2ltYWwubG9uLWxhdGdsb2NhdGlvblgCGo4AAAAAAFlAnY5AQUFBQUFBRUE";
createLocationAttestation(encodedPayload);
```

### Solidity Smart Contract

For use cases requiring on-chain logic, attestations can be created directly by calling the `IEAS.attest` function.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import { IEAS, AttestationRequest } from "@eas/contracts/IEAS.sol";
import { ISchemaRegistry } from "@eas/contracts/ISchemaRegistry.sol";

contract LocationAttestor {
    IEAS private eas;
    bytes32 private locationSchemaUID;

    event LocationAttested(address indexed attester, bytes32 uid);

    constructor(address _easAddress, bytes32 _schemaUID) {
        eas = IEAS(_easAddress);
        locationSchemaUID = _schemaUID;
    }

    /**
     * @notice Creates an on-chain attestation with a Location Protocol payload.
     * @param recipient The address receiving the attestation.
     * @param encodedPayload The Base64url encoded location payload.
     * @return uid The UID of the newly created attestation.
     */
    function attestLocation(address recipient, string calldata encodedPayload) public returns (bytes32) {
        // ABI-encode the payload string as required by the schema
        bytes memory encodedData = abi.encode(encodedPayload);

        AttestationRequest memory request = AttestationRequest({
            schema: locationSchemaUID,
            data: AttestationRequestData({
                recipient: recipient,
                expirationTime: 0, // No expiration
                revocable: true,
                refUID: bytes32(0),
                data: encodedData,
                value: 0
            })
        });

        bytes32 uid = eas.attest(request);

        emit LocationAttested(msg.sender, uid);
        return uid;
    }
}
```

## Verification Patterns

Verification ensures a payload is structurally valid and confirms its associated attestation exists and is trusted.

### Local Payload Verification

This is the most common pattern. After receiving an attestation, you decode the payload and validate it against the official Location Protocol JSON Schema.

#### JavaScript/TypeScript (using AJV)

```typescript
import Ajv from "ajv";
import { decode } from "cbor-x";
import { Buffer } from "buffer";

const ajv = new Ajv();

// A simplified Location Protocol JSON Schema
const locationProtocolSchema = {
  type: "object",
  properties: {
    specVersion: { type: "string" },
    srs: { type: "string", pattern: "^EPSG:[0-9]+$" },
    locationType: { type: "string" },
    location: {}, // Can be an array, object, or string depending on location_Type
  },
  required: ["lp_version", "srs", "location_type", "location"],
  srs: "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
};

const validate = ajv.compile(locationProtocolSchema);

function verifyPayload(encodedPayload: string): boolean {
  try {
    // 1. Decode from Base64url to CBOR, then to a JS object
    const decodedCbor = Buffer.from(encodedPayload, "base64url");
    const payload = decode(decodedCbor);

    // 2. Validate against the JSON schema
    const isValid = validate(payload);
    if (!isValid) {
      console.error("Schema validation failed:", validate.errors);
      return false;
    }

    console.log("Payload verified successfully against schema.");
    return true;
  } catch (error) {
    console.error("Verification failed:", error);
    return false;
  }
}

// Encoded payload from a trusted source
const encodedPayload =
  "p2xWc3BlY1ZlcnNpb25jMS4wc3Nyc2ppRVBTRzo0MzI2bWxvY2F0aW9uVHlwZXVjb29yZGluYXRlLWRlY2ltYWwubG9uLWxhdGdsb2NhdGlvblgCGo4AAAAAAFlAnY5AQUFBQUFBRUE";
const isVerified = verifyPayload(encodedPayload);
console.assert(isVerified, "Payload verification should succeed");
```

### On-Chain Attestation Verification

Full on-chain payload validation is often too gas-intensive. Instead, smart contracts typically verify the _existence and validity_ of an attestation UID on the EAS contract. The off-chain application is still responsible for decoding and validating the payload content itself.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import { IEAS } from "@eas/contracts/IEAS.sol";

contract LocationVerifier {
    IEAS private eas;

    constructor(address _easAddress) {
        eas = IEAS(_easAddress);
    }

    /**
     * @notice Checks if an attestation with the given UID is valid on the EAS contract.
     * @param attestationUID The UID of the attestation to check.
     * @return True if the attestation exists and has not been revoked.
     */
    function isAttestationValid(bytes32 attestationUID) public view returns (bool) {
        // getAttestation will revert if the UID does not exist.
        // We also check that the attestation has not been revoked.
        try eas.getAttestation(attestationUID) returns (IEAS.Attestation memory att) {
            return !att.revoked;
        } catch {
            return false;
        }
    }

    /**
     * @notice Checks that an attestation was made by a specific trusted attester.
     * @param attestationUID The UID of the attestation.
     * @param trustedAttester The address of the attester to verify against.
     * @return True if the attestation is valid and was made by the trusted attester.
     */
    function isAttestationFromTrustedSource(bytes32 attestationUID, address trustedAttester) public view returns (bool) {
         try eas.getAttestation(attestationUID) returns (IEAS.Attestation memory att) {
            return !att.revoked && att.attester == trustedAttester;
        } catch {
            return false;
        }
    }
}
```

## Best Practices and Anti-Patterns

Following best practices ensures your implementation is secure, efficient, and interoperable.

| Category         | :white_check_mark: Best Practices (Do)                                                                                          | :x: Anti-Patterns (Don't)                                                                        |
| :--------------- | :------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------- |
| **Payloads**     | Validate payloads against the JSON Schema before encoding and attesting.                                                        | Don't create attestations with unvalidated or malformed payloads.                                |
|                  | Use CIDs (Content Identifiers) in the `media_data` field to reference large files stored on IPFS or other decentralized storage. | Don't embed large binary data (e.g., images, videos) directly into the payload.                  |
| **Encoding**     | Use a library that supports canonical CBOR to ensure deterministic output.                                                      | Don't manually construct JSON strings, as this can lead to non-deterministic serialization.      |
| **Attestations** | Prefer off-chain attestations for cost-effectiveness, especially for high-frequency data.                                       | Don't create on-chain attestations for every location update unless required for on-chain logic. |
|                  | Pin the UID of the specific schema version you are targeting to avoid unexpected changes.                                       | Don't use a mutable schema tag (like `latest`) in a production environment.                      |
| **Security**     | Securely manage the private keys used for signing attestations using hardware wallets or secure enclaves.                       | Don't hardcode private keys or expose them in client-side applications.                          |
| **Verification** | Verify the attester's address against a list of trusted sources before accepting an attestation's claims.                       | Don't blindly trust any attestation found on-chain without verifying its origin and content.     |

---

[:material-arrow-left: Back to Implementation Overview](index.md){ .md-button .md-button--primary }
