#!/usr/bin/env python3
import base64
import binascii
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature, InvalidKey
import sys


own_id = 5


def verify_trust_token(user_pk, token, public_keys):
    score = 0
    for i in range(0, len(token), 2):
        pair = token[i:i + 2]
        value = pair[1]
        server = pair[0]
        try:
            signature = base64.b64decode(value.encode('utf-8'))
            server_public_key = load_pem_public_key(public_keys[server].encode('utf-8'))
            server_public_key.verify(
                signature,
                base64.b64decode(user_pk.encode('utf-8')),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            score = score + 1
        except InvalidSignature:
            sys.stdout.write("error")
        except binascii.Error:
            sys.stdout.write("error")
    return score


def main():
    if len(sys.argv) < 2:
        sys.stdout.write("error")  # if User-Signature header is missing or not as expected
    else:
        parts = sys.argv[1].split(":")
        public_key_str = parts[0]
        try:
            with open("/app/public_keys.txt", 'r') as f:
                public_keys = json.load(f)
        except json.JSONDecodeError:
            public_keys = {}

        try:
            # Attempt to load the public key
            serialization.load_pem_public_key(
                base64.b64decode(public_key_str.encode('utf-8'))  # Convert the string to bytes
            )
        except (ValueError, InvalidKey):
            sys.stdout.write("error")
        user_signatures = parts[1:]

        score = verify_trust_token(public_key_str, user_signatures, public_keys)

        try:
            with open("/app/stored_header.json", 'r') as f:
                stored_data = json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or doesn't exist, or contains invalid JSON
            stored_data = {}

        # Update or insert new data for the public key
        stored_data[public_key_str] = score

        # Write updated data back to the file
        with open("/app/stored_header.json", 'w') as f:
            json.dump(stored_data, f, indent=4)

        return None


if __name__ == "__main__":
    main()
