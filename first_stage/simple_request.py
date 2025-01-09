import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

url = [
    'http://localhost:8080/login',
    'http://localhost:8081/login',
    'http://localhost:8082/login',
    'http://localhost:8083/login',
    'http://localhost:8084/login'
]
data = {'username': 'admin', 'password': 'password'}

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Extract the public key
public_key = private_key.public_key()

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

encoded_key = base64.b64encode(public_pem).decode('utf-8')

headers = {
    'User-Key-Signatures': encoded_key
}

try:
    response = requests.post(url[0], headers=headers, data=data)

    print(response.headers)
    if 'User-Key-Signatures' in response.headers:
        headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

    response = requests.post(url[0], headers=headers, data=data)

    print(response.headers)


except Exception as e:
    print(f"An error occurred: {e}")