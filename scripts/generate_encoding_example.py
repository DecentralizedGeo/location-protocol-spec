import json
import base64
import cbor2

def generate_examples_payload():
    # Constructing payload based on examples.md content
    # Note: examples.md uses camelCase keys which violates the spec (snake_case), 
    # but I must match the example's code structure to avoid confusing the user 
    # (unless I fix the keys too, but the task is SRS).
    # I will stick to the keys used in the example code so the example remains self-consistent.
    
    payload = {
        "specVersion": "1.0",
        "srs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
        "locationType": "coordinate-decimal+lon-lat",
        "location": [-74.006, 40.7128]
        # omitting eventTimestamp as it complicates the static string (dynamic in logic)
    }

    # Re-encode
    # canonical=True to ensure deterministic
    new_cbor = cbor2.dumps(payload, canonical=True)
    
    # Encode to Base64url
    new_b64 = base64.urlsafe_b64encode(new_cbor).rstrip(b'=').decode('utf-8')
    
    print("\nPayload Data:", payload)
    print("\nNew Base64 Encoded:", new_b64)

if __name__ == "__main__":
    generate_examples_payload()
