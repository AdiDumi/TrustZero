import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import random
import time
import matplotlib.pyplot as plt
import numpy as np

url = [
    'http://localhost:8080/login',
    'http://localhost:8081/login',
    'http://localhost:8082/login',
    'http://localhost:8083/login',
    'http://localhost:8084/login'
]
data = {'username': 'admin', 'password': 'password'}


def good_client():
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

    total_requests = 0
    # Lists to store performance data
    request_times = []  # Store time taken for each request
    request_result = []  # Store the result of the request(1/0)
    request_signatures = []  # Store the number if signatures of a request
    for i in range(50):
        time.sleep(0.5)
        request_start_time = time.monotonic()  # Time before request
        num = random.randint(0, 4)
        try:
            request_signatures.append(headers['User-Key-Signatures'].count(":") / 2)
            response = requests.post(url[num], headers=headers, data=data)
            request_end_time = time.monotonic()  # Time after request
            request_duration = request_end_time - request_start_time

            if 'User-Key-Signatures' in response.headers:
                headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

            if response.status_code == 200:
                request_result.append(1)
            else:
                headers['User-Key-Signatures'] = encoded_key
                request_result.append(0)

            total_requests += 1
            # Append performance data
            request_times.append(request_duration)

        except Exception as e:
            print(f"An error occurred: {e}")
            request_end_time = time.time()
            request_duration = request_end_time - request_start_time

            headers['User-Key-Signatures'] = encoded_key

            total_requests += 1
            request_times.append(request_duration)
            request_result.append(0)
    return request_times, request_result, request_signatures


def bad_client():
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

    total_requests = 0
    # Lists to store performance data
    request_times = []  # Store time taken for each request
    request_result = []  # Store the result of the request(1/0)
    request_signatures = []  # Store the number if signatures of a request
    for i in range(50):
        time.sleep(0.5)
        request_start_time = time.monotonic()  # Time before request
        num = random.randint(0, 4)
        try:
            request_signatures.append(headers['User-Key-Signatures'].count(":") / 2)
            response = requests.post(url[num], headers=headers, data=data)
            request_end_time = time.monotonic()  # Time after request
            request_duration = request_end_time - request_start_time

            if 'User-Key-Signatures' in response.headers:
                headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

            if response.status_code == 200:
                request_result.append(1)
            else:
                headers['User-Key-Signatures'] = encoded_key
                request_result.append(0)

            if num % 2 == 0:
                headers['User-Key-Signatures'] =  headers['User-Key-Signatures'][:-20]

            total_requests += 1
            # Append performance data
            request_times.append(request_duration)

        except Exception as e:
            print(f"An error occurred: {e}")
            request_end_time = time.time()
            request_duration = request_end_time - request_start_time

            headers['User-Key-Signatures'] = encoded_key

            total_requests += 1
            request_times.append(request_duration)
            request_result.append(0)
    return request_times, request_result, request_signatures


# Plot the performance data
times1, results1, signatures1 = bad_client()
times2, results2, signatures2 = good_client()

requests_time = times1 + times2
success_status = results1 + results2
signatures = signatures1 + signatures2

# Calculate mean request time
mean_request_time1 = np.mean(times1)
mean_request_time2 = np.mean(times2)
request_numbers = np.arange(1, len(requests_time) + 1)

# Middle point (based on half the data)
middle_point = len(request_numbers) // 2

# Create a figure with three subplots
fig, axs = plt.subplots(3, 1, figsize=(10, 12))

# Plot 1: Request Duration Over Time
axs[0].plot(request_numbers, requests_time, label='Request Time (s)', color='blue', marker='o')
axs[0].plot(
    request_numbers[:middle_point],  # X-values limited to the first half
    [mean_request_time1] * middle_point,  # Y-values constant at mean_request_time1
    color='black', linestyle='--', label=f'Mean "bad" user: {mean_request_time1:.4f}'
)
axs[0].plot(
    request_numbers[middle_point:],
    [mean_request_time2] * middle_point,
    color='black', linestyle='--', label=f'Mean "good" user: {mean_request_time2:.4f}'
)
axs[0].axvline(middle_point, color='purple', linestyle='-', label='User Separator')
axs[0].set_title('Request Duration Over Time')
axs[0].set_xlabel('Request Number')
axs[0].set_ylabel('Time (seconds)')
axs[0].legend()
axs[0].grid(True)

# Plot 2: Request Success and Failure Over Time
axs[1].plot(request_numbers, success_status, label='Success (1) / Failure (0)', color='red', marker='o')
axs[1].axvline(middle_point, color='purple', linestyle='-', label='User Separator')
axs[1].set_title('Request Success and Failure')
axs[1].set_xlabel('Request Number')
axs[1].set_ylabel('Status')
axs[1].legend()
axs[1].grid(True)

# Plot 3: Signatures per Request
axs[2].plot(request_numbers, signatures, label='Signatures', color='green', marker='o')
axs[2].axvline(middle_point, color='purple', linestyle='-', label='User Separator')
axs[2].set_title('Signatures per request')
axs[2].set_xlabel('Request Number')
axs[2].set_ylabel('Number of signatures')
axs[2].legend()
axs[2].grid(True)

# Adjust layout
plt.tight_layout()
plt.savefig("test2.png", format='png')
plt.show()
