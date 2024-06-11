import sys
import time
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key


own_id = 1


def read_token():
    # Define the path to the file where the token is stored
    token_file = "/token_storage.txt"

    # Read the token from the file
    if os.path.exists(token_file):
        with open(token_file, "r") as file:
            token = file.read().strip()
        return token
    return None


def load_private_key_from_file():
    with open("/app/private_key.pem", "rb") as key_file:
        private_key_data = key_file.read()
    return private_key_data


def generate_certificate(user_info, private_key):
    certificate = f"{user_info}|{time.time()}"
    private_key = load_pem_private_key(private_key, password=None)
    signature = private_key.sign(
        certificate.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return certificate, signature


def add_token_to_response(response_body):
    # Add token to the response body
    private_key = load_private_key_from_file()
    certificate, signature = generate_certificate(response_body, private_key)
    trust_token = {
        "id": 1,
        "certificate": certificate,
        "signature": signature.hex()
    }
    token = read_token()

    if token:
        index_to_delete = None
        for index, obj in enumerate(token):
            if obj.get("id") == own_id:
                index_to_delete = index
                break

        if index_to_delete is not None:
            del token[index_to_delete]
        # Append the token to the response JSON
        response_body["token"] = token
    else:
        response_body["token"] = []
    response_body["token"].append(trust_token)
    modified_response_body = response_body
    return modified_response_body


def main():
    # Read the response body from stdin
    response_body = sys.stdin.read()

    # Modify the response body to add the token
    modified_response_body = add_token_to_response(response_body)

    # Print the modified response body to stdout
    sys.stdout.write(modified_response_body)


if __name__ == "__main__":
    main()
