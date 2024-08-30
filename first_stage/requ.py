import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

url = 'http://localhost:80/login'
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

for i in range(1):
    try:
        response = requests.post(url, headers=headers, data=data)
        print(response.text)
        print(response.headers)
        if 'User-Signatures' in response.headers:
            headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']
    except Exception as e:
        print(f"An error occurred: {e}")
