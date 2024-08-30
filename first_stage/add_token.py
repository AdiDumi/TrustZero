#!/usr/bin/env python3
import sys
import json
import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key


servers = {
    1: "asdad",
    2: "dafad",
}

own_id = 1

headers_file = "/app/stored_header.json"


def main():
    if len(sys.argv) < 2:
        return 0
    parts = sys.argv[1].split(":")
    user_public_key = parts[0]
    server_token = parts[1:]

    try:
        with open(headers_file, 'r') as f:
            stored_data = json.load(f)
    except json.JSONDecodeError:
        # If the file is empty or doesn't exist, or contains invalid JSON
        stored_data = {}

    # Update or insert new data for the public key
    stored_data[user_public_key] = {"token": ":".join(server_token), "score": len(server_token)/2}

    # Write updated data back to the file
    with open(headers_file, 'w') as f:
        json.dump(stored_data, f, indent=4)

    sys.stdout.write("1")


if __name__ == "__main__":
    main()
