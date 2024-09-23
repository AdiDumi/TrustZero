import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import random
import time
import concurrent.futures
import matplotlib.pyplot as plt
import threading


start_time = time.time()
url = [
    'http://localhost:8080/login',
    'http://localhost:8081/login',
    'http://localhost:8082/login',
    'http://localhost:8083/login',
    'http://localhost:8084/login'
]
data = {'username': 'admin', 'password': 'password'}
# Shared list to store results
results = {}


def good_client():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    chosen = []
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
    successful_requests = 0
    failed_requests = 0
    number_of_sign = []
    # Lists to store performance data
    request_times = []  # Store time taken for each request
    request_statuses = []  # Store whether the request was successful (1) or failed (0)
    for i in range(40):
        request_start_time = time.time()  # Time before request
        try:
            choice = random.choice(url)
            chosen.append(choice)
            response = requests.post(choice, headers=headers, data=data)
            request_end_time = time.time()  # Time after request
            request_duration = request_end_time - request_start_time

            total_requests += 1
            if response.status_code == 200:
                successful_requests += 1
                request_statuses.append(1)  # 1 for success
            else:
                number_of_sign.append(0)
                failed_requests += 1
                request_statuses.append(0)
            # Append performance data
            request_times.append(request_duration)
            if 'User-Key-Signatures' in response.headers:
                number_of_sign.append((len(response.headers['User-Key-Signatures'].split(":")) - 1)/2)
                headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

        except Exception as e:
            print(f"An error occurred: {e}")
            request_end_time = time.time()
            request_duration = request_end_time - request_start_time

            total_requests += 1
            failed_requests += 1
            number_of_sign.append(0)
            # Append performance data
            request_times.append(request_duration)
            request_statuses.append(0)  # 0 for failure
    results['good'] = [total_requests, successful_requests, failed_requests, request_times, request_statuses, number_of_sign]


def hacked_client():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    chosen = []
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
    successful_requests = 0
    failed_requests = 0
    number_of_sign = []
    # Lists to store performance data
    request_times = []  # Store time taken for each request
    request_statuses = []  # Store whether the request was successful (1) or failed (0)
    for i in range(40):
        request_start_time = time.time()  # Time before request
        try:
            choice = random.choice(url)
            chosen.append(choice)
            response = requests.post(choice, headers=headers, data=data)
            request_end_time = time.time()  # Time after request
            request_duration = request_end_time - request_start_time

            total_requests += 1
            if response.status_code == 200:
                successful_requests += 1
                request_statuses.append(1)  # 1 for success
            else:
                number_of_sign.append(0)
                failed_requests += 1
                request_statuses.append(0)
            # Append performance data
            request_times.append(request_duration)
            if 'User-Key-Signatures' in response.headers:
                number_of_sign.append((len(response.headers['User-Key-Signatures'].split(":")) - 1)/2)
                hacked = random.randint(1, 10)
                if hacked < 4:
                    headers['User-Key-Signatures'] = response.headers['User-Key-Signatures'][:-20]
                else:
                    headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']
            else:
                headers = {
                    'User-Key-Signatures': encoded_key
                }

        except Exception as e:
            print(f"An error occurred: {e}")
            request_end_time = time.time()
            request_duration = request_end_time - request_start_time

            total_requests += 1
            failed_requests += 1
            number_of_sign.append(0)
            # Append performance data
            request_times.append(request_duration)
            request_statuses.append(0)  # 0 for failure
            headers = {
                'User-Key-Signatures': encoded_key
            }
    results['bad'] = [total_requests, successful_requests, failed_requests, request_times, request_statuses, number_of_sign]


# Create threads
thread1 = threading.Thread(target=good_client())
thread2 = threading.Thread(target=hacked_client())

# Start threads
thread1.start()
thread2.start()

# Wait for both threads to finish
thread1.join()
thread2.join()
# Number of threads to use
# num_threads = 10  # Increase this to send more concurrent requests
#
# # Use ThreadPoolExecutor to send multiple requests concurrently
# with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
#     # Submit multiple tasks
#     futures = [executor.submit(send_request) for _ in range(num_threads)]
#
#     # Optional: Sleep to avoid overwhelming the server immediately
#     time.sleep(0.1)  # Reduce this to increase request rate

# print("\n--- Performance Summary ---")
# print(f"Total Requests: {total_requests}")
# print(f"Successful Requests: {successful_requests}")
# print(f"Failed Requests: {failed_requests}")
# print(f"Total Time: {total_duration:.2f} seconds")
# print(f"Average Time per Request: {total_duration / total_requests:.4f} seconds")
# print(chosen)
# Plot the performance data
res_total_requests = results['good'][0] + results['bad'][0]
res_successful_requests = results['good'][1] + results['bad'][1]
res_failed_requests = results['good'][2] + results['bad'][2]
res_request_times = results['good'][3] + results['bad'][3]
res_request_statuses = results['good'][4] + results['bad'][4]
res_number_of_sign = results['good'][5] + results['bad'][5]
plt.figure(figsize=(10, 8))

mean = sum(res_request_times) / len(res_request_times)

# Plot request durations
plt.subplot(3, 1, 1)
plt.plot(res_request_times, marker='o', linestyle='-', color='b', label='Request Time (s)')
plt.axhline(y=mean, color='k', linestyle='--', label=f'Mean: {mean}')
plt.xlabel('Request Number')
plt.ylabel('Time (seconds)')
plt.title('Request Duration Over Time')
plt.legend()

# Plot success vs failure
plt.subplot(3, 1, 2)
plt.plot(res_request_statuses, marker='o', linestyle='-', color='r', label='Success (1) / Failure (0)')
plt.xlabel('Request Number')
plt.ylabel('Status')
plt.title('Request Success and Failure Over Time')
plt.legend()

# Plot success vs failure
plt.subplot(3, 1, 3)
plt.plot(res_number_of_sign, marker='o', linestyle='-', color='g', label='Signatures')
plt.xlabel('Signatures per request')
plt.ylabel('Number of signatures')
plt.title('Signatures per request')
plt.legend()

# mean = sum(res_request_times) / len(res_request_times)
# print(f"Mean request time is {mean}")
# Show the plots
plt.tight_layout()
plt.savefig("experiment.png", format='png')
plt.show()
