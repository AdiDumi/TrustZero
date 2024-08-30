from flask import Flask, request, jsonify
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

app = Flask(__name__)

own_id = 1

servers = [1, 2, 3, 4, 5]


def load_private_key_from_file():
    with open("/app/private_key.pem", "rb") as key_file:
        private_key_data = key_file.read()
    return private_key_data


def generate_certificate(user_pk, private_key):
    private_key = load_pem_private_key(private_key, password=None)

    signature = private_key.sign(
        base64.b64decode(user_pk),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def add_token_to_response(token_list, user_pk):
    # Load server private key
    private_key = load_private_key_from_file()
    # Generate certificate with it on the user public key
    signature = generate_certificate(user_pk, private_key)

    # search if the user already had a certificate from server and update it
    id_found = False
    for i in range(0, len(token_list), 2):
        pair = token_list[i:i + 2]
        key = pair[0]
        if int(key) == own_id:
            id_found = True
            token_list[i + 1] = signature
            break

    if not id_found:
        token_list.append(str(own_id))
        token_list.append(base64.b64encode(signature).decode('utf-8'))
    return token_list


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    specific_header_value = request.headers.get('User-Key-Signatures')

    # Simulate a login check (for demo purposes)
    if username != 'admin' or password != 'password':
        return jsonify({"message": "Login failed"}), 403

    status_code = 200
    response_data = {"message": "Login successful"}
    response = jsonify(response_data)

    parts = specific_header_value.split(":")
    user_public_key = parts[0]

    # Modify the response body to add the token
    header = add_token_to_response(parts[1:], user_public_key)
    response.headers['User-Key-Signatures'] = user_public_key + ":" + ":".join(header)
    return response, status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=88)
