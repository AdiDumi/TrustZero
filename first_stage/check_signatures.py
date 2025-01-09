#!/usr/bin/env python3
import base64
import binascii
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature, InvalidKey
import sys


own_id = 5

public_keys_d = {
"1":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlgjRLGIr2FvP7izZHasu9p9CiUxFzy06maC0bZhU5VzGOElV7KdQQFvSGHP+QII0dfm+JXajZdVnXojuGan9JuIDftb8MA+HKoVYLBSPLW25kqPTbkJXh4ZaFew9UNZ5qb3B1+wNOfFoOLvqVHsgU8hmW6cKGqyuQXvTCGnVl7vmfbvpn7TYM/3TbbkvI36He4Qp9w3MRUROlDTCIbifxC67SNXIdb8oLapOBrCaazNrRu8SYleCFMSylCFrkfRKS/7WfPX3sDq8aacL0OUuIiwXvjVA5AMlz2TZYtUBgrVXZMdUlcPNJ/jqOTIttSg0+xCQNR5kW4FzTaajxJgjhwIDAQAB\n-----END PUBLIC KEY-----",
"2":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAr6Tc+unzxyeameSYtP/4d5nA9MoaMv1t9DgFnNQpeDAmag8aR0qZZSr4Uucz371Mx9e5M9pjdZiM+uFFf5qhAzbJpqrtvJdYfHfQlVcktquxxX3JMWETflaCZJThnizSAoZ9+lUTjXrZ2OsrTdGyLXZ39sGP2LIQRMTcOjYa9TwOYOG9VsbIIbzsS3ZOxLzpHbTiXYOQ8/I73VOmO3ETmY5Bn0CnoL3T5oiZz9KZtsVhM0OIQTn5b/e0JKJ/aKzmiIcfJZqY5dBvN6YdjY0XyiKYYzMHeNPda6+RPw5H5aQo5wnuDqzwN1SCggKmOOHRDS0sJzi0QGYEgBY+xXdplQIDAQAB\n-----END PUBLIC KEY-----",
"3":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA+ne/oNz7QS948LAl6MbLEB2ruzGvmHMAGcwOMfBphCtu+Vd7TQl9AS8+xkuE3RIvRiPPcGoR13n0v4lM940Fe569sABKK4wFl7vNeG54B2mxoF8ilksszMy1tNdVAfcbxntmprzl9wQNjzaMIhHdFg5M3yZn54f/jIgH4rdtHQxWNrEI+FCg7JllZ3HCow6vBdTdktk+SgXt3Na8GaRcg8E9Bpep74zGqDDY77Q0uOaPcjQYYGWCYUcLsT1y8wXj5JhQh+XVUdMUXrAbomOxtSLB50wLC++mBAS6HPb1YWduqQTu6fUVZsKfAYr6GBRSE/zTWIAvopnNIkmevptZ8QIDAQAB\n-----END PUBLIC KEY-----",
"4":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiDdRBy4U51Wk91aR5xJnOON7QmeIuPTUP4kDTV+z0hFmduwUlggg82QBtWExkux3Ye5YtJTKUC2dxv507lz6ojrOfa/hNa8xpXI6qqToig6RqoUisH6WX/UPf4cvG+5AVSD+5cfnLJf1RF8eeTtXixLqHBEGUnmCWhm3OBsBMEwW1AbMDiqnOG5iM3+qzJMVCQfc36WAqh1Vo3zRSpSUgwVMGn/OnTUbdcavluNHpsYDy0wp/exHs/mWahgKXxlf0o2oMzQqv1YhOhUp8omvBfPbsQREIKrfkSxEyDrpuRgFVB758NYOUbsGgi8Rx2ZTAS7hKr1UdYUdggd7lmiuXQIDAQAB\n-----END PUBLIC KEY-----",
"5":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlAx8xNOJEkK5tna1+gUcym4JTLSFNwKmFYjfZIjzMmqFOUtJALMBsAVFnlotWoJUhj6Go9DiPzSL5AVwrB22zIWDAWn7Pf6DuHQ2hlRh2l3fI8UUJYpKEiVmzfkF4atIbHKRC67liONaU+8gdG1psIGlSQdHZCc5+/BRkED4AU4Ke9w6xAdLTeTNKB3etnnf2aRPKGwmz3MivGu5//g9vFviCmSwPwrWVQrIcVzJJ74/3dSs+U/mfHXCkHKRR+geedN/TMQKO8k05AjQMoxvbyv/OBFegK7VFIxfgEG5IHIgATDN4cyaCbwdI4pQTTnZGoFRxDQBXXPLO4LcgwjiKQIDAQAB\n-----END PUBLIC KEY-----"
}

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
            # Attempt to load the public key
            serialization.load_pem_public_key(
                base64.b64decode(public_key_str.encode('utf-8'))  # Convert the string to bytes
            )
        except (ValueError, InvalidKey):
            sys.stdout.write("error")
        user_signatures = parts[1:]

        verify_trust_token(public_key_str, user_signatures, public_keys_d)

        return None


if __name__ == "__main__":
    main()
