import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import time
import matplotlib.pyplot as plt
import random


start_time = time.time()
url = [
    'http://localhost:8080/login',
    'http://localhost:8081/login',
    'http://localhost:8082/login',
    'http://localhost:8083/login',
    'http://localhost:8084/login'
]
data = {'username': 'admin', 'password': 'password'}


def multiple_signatures_client():
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

    for i in range(5):
        try:
            response = requests.post(url[i], headers=headers, data=data)

            if 'User-Key-Signatures' in response.headers:
                headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

        except Exception as e:
            print(f"An error occurred: {e}")

    total_requests = 0
    # Lists to store performance data
    request_times = []  # Store time taken for each request
    for i in range(500):
        request_start_time = time.monotonic()  # Time before request
        num = random.randint(0, 4)
        try:
            response = requests.post(url[num], headers=headers, data=data)
            request_end_time = time.monotonic()  # Time after request
            request_duration = request_end_time - request_start_time

            total_requests += 1
            # Append performance data
            request_times.append(request_duration)

        except Exception as e:
            print(f"An error occurred: {e}")
            request_end_time = time.time()
            request_duration = request_end_time - request_start_time

            total_requests += 1
            request_times.append(request_duration)
    return request_times


def no_signatures_client():
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
    for i in range(500):
        request_start_time = time.monotonic()  # Time before request
        num = random.randint(0, 4)
        try:
            requests.post(url[num], headers=headers, data=data)
            request_end_time = time.monotonic()  # Time after request
            request_duration = request_end_time - request_start_time

            total_requests += 1
            # Append performance data
            request_times.append(request_duration)

        except Exception as e:
            print(f"An error occurred: {e}")
            request_end_time = time.time()
            request_duration = request_end_time - request_start_time

            total_requests += 1
            request_times.append(request_duration)
    return request_times


# Plot the performance data
times1 = no_signatures_client()
times2 = multiple_signatures_client()
plt.figure(figsize=(10, 8))

mean1 = sum(times1) / 500
mean2 = sum(times2) / 500

# Plot request durations
plt.subplot(2, 1, 1)
plt.plot(times1, marker='o', linestyle='', color='b', label='Request Time (s)')
plt.axhline(y=mean1, color='k', linestyle='--', label=f'Mean: {mean1}')
plt.xlabel('Request Number')
plt.ylabel('Time (seconds)')
plt.title('Request Duration for 0 signatures user')
plt.legend()

# Plot success vs failure
plt.subplot(2, 1, 2)
plt.plot(times2, marker='o', linestyle='', color='r', label='Request Time (s)')
plt.axhline(y=mean2, color='k', linestyle='--', label=f'Mean: {mean2}')
plt.xlabel('Request Number')
plt.ylabel('Time (seconds)')
plt.title('Request Duration for 5 signatures user')
plt.legend()

# Show the plots
plt.tight_layout()
plt.savefig("test1.png", format='png')
plt.show()

# Box plot for the request durations
plt.figure(figsize=(8, 6))

# Create the box plot
plt.boxplot([times1, times2], tick_labels=['5 Signatures User', '0 Signatures User'], patch_artist=True,
            boxprops=dict(facecolor='yellow', color='black'),
            medianprops=dict(color='red'))

# Add grid lines
plt.grid(axis='y', linestyle='--', color='gray', alpha=0.7)  # Horizontal grid lines

# Add labels and title
plt.ylabel('Time (seconds)')
plt.title('Box Plot of Request Durations')

# Save the box plot to a file
plt.savefig("test1box.png", format='png')

# Show the box plot
plt.show()
