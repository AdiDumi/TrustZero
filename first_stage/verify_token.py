from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import sys

servers = {
    1: "asdad",
    2: "dafad",
}

own_id = 1


def delete_token_to_request(request_body):
    if "token" in request_body:
        token = request_body.pop("token", None)
        with open("/token_storage.txt", "w") as file:
            file.write(token)
    return request_body


def verify_trust_token(request_body):
    if "token" not in request_body:
        return 0
    certificates_list = request_body['token']
    pas = 0
    for certificate in certificates_list:
        signature = bytes.fromhex(certificate['signature'])
        server = certificate['id']
        public_key = servers[server]
        if server != own_id:
            try:
                public_key.verify(
                    signature,
                    certificate.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                pas = pas + 1
            except:
                sys.exit(1)
    return pas


def main():
    # Read the response body from stdin
    request_body = sys.stdin.read()

    if verify_trust_token(request_body) >= 0:
        # Modify the response body to add the token
        modified_request_body = delete_token_to_request(request_body)

        # Print the modified response body to stdout
        sys.stdout.write(modified_request_body)


if __name__ == "__main__":
    main()
