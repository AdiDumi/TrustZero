#!/usr/bin/env python3
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature, InvalidKey
import sys

servers = {
    1: "asdad",
    2: "dafad",
}


own_id = 1


headers_file = "/app/stored_header.json"


def verify_trust_token(user_pk, token):
    score = 0
    result_list = []
    for i in range(0, len(token), 2):
        pair = token[i:i + 2]
        value = pair[1]
        key = pair[0]
        signature = bytes.fromhex(value)
        server = key
        server_public_key = load_pem_public_key(servers[server].encode())
        item = {
            "id": int(key),
            "signature": value
        }
        result_list.append(item)
        try:
            server_public_key.verify(
                signature,
                user_pk,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            score = score + 1
        except InvalidSignature:
            sys.stdout.write("error")
    return score, result_list


def main():
    if len(sys.argv) < 2:
        return 0  # Return 0 if User-Signature header is missing or not as expected
    else:
        parts = sys.argv[1].split(":")
        public_key_str = parts[0]
        try:
            # Attempt to load the public key
            serialization.load_pem_public_key(
                base64.b64decode(public_key_str.encode('utf-8'))  # Convert the string to bytes
            )
        except (ValueError, InvalidKey):
            sys.stdout.write("error")
        user_signatures = parts[1:]

        # Get the score of the signatures(if correct)
        score, token = verify_trust_token(public_key_str, user_signatures)

        # Print the score
        #sys.stdout.write(str(score))


if __name__ == "__main__":
    main()
