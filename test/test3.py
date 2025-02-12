from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
import random
import time
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
import threading

# url of servers
url = [
    'http://localhost:8080/login',
    'http://localhost:8081/login',
    'http://localhost:8082/login',
    'http://localhost:8083/login',
    'http://localhost:8084/login'
]
# test data
data = {'username': 'admin', 'password': 'password'}


# Function to send a single request
def send_request(user_id):
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

    if user_id == 0:
        successful_requests = 0
        failed_requests = 0
        requests_time = []
        # Lists to store performance data
        request_times = []  # Store time taken for each request
        start_time = time.monotonic()
        while True:
            request_start_time = time.monotonic()  # Time before request
            try:
                choice = random.choice(url)
                response = requests.post(choice, headers=headers, data=data)
                request_end_time = time.monotonic()  # Time after request
                requests_time.append(request_end_time)
                request_duration = request_end_time - request_start_time

                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
                # Append performance data
                request_times.append(request_duration)
                if 'User-Key-Signatures' in response.headers:
                    headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

            except Exception as e:
                request_end_time = time.monotonic()
                print(f"An error occurred in worker {user_id}: {e}")
                request_duration = request_end_time - request_start_time
                requests_time.append(request_end_time)
                failed_requests += 1
                # Append performance data
                request_times.append(request_duration)
            check_time = time.monotonic()
            if check_time - start_time > ((2010 - user_id) * 2):
                break
        return [successful_requests + failed_requests, request_times, requests_time, start_time, user_id]
    else:
        start_time = time.monotonic()
        while True:
            try:
                choice = random.choice(url)
                response = requests.post(choice, headers=headers, data=data)

                if 'User-Key-Signatures' in response.headers:
                    headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

            except Exception as e:
                print(f"An error occurred in worker {user_id}: {e}")
            check_time = time.monotonic()
            if check_time - start_time > ((2010 - user_id) * 2):
                break
        return [0, [], [], start_time, user_id]


all_results = []
# Function to send multiple requests in parallel
with ThreadPoolExecutor(max_workers=2000) as executor:
    futures = []
    for j in range(2000):
        print(f"Starting user {j}")
        futures.append(executor.submit(send_request, j))  # Launch 100 threads
        time.sleep(2)

    for future in as_completed(futures):
        all_results.append(future.result())

sorted_results = sorted(all_results, key=lambda x: x[-1])

plt.rcParams.update({'font.size': 18})

times = []
request_start_times = []
user_start_times = []
servers_load = []
# Iterate through each sublist and extend the new list with the 4th element (which is a list)
for sublist in sorted_results:
    times.extend(sublist[1])
    request_start_times.extend(sublist[2])
    user_start_times.append(sublist[3])

plt.figure(figsize=(10, 8))

mean = sum(times) / sum(sublist[0] for sublist in sorted_results)
# Plot request durations
plt.plot(times, marker='o', linestyle='', color='b', label='Request Time (s)')
plt.axhline(y=mean, color='k', linestyle='--', label=f'Overall Mean: {mean}')

window_size = 100

x = np.arange(window_size, len(times))  # x-axis values (Request Number)

i = 0
# Initialize an empty list to store moving averages
moving_averages = []

# Loop through the window of size 100
while i < len(times) - window_size:

    # Calculate the average of current window
    window_average = round(np.sum(times[
      i:i+window_size]) / window_size, 2)

    # Store the average of current
    # window in moving average list
    moving_averages.append(window_average)

    # Shift window to right by one position
    i += 1

plt.plot(x, moving_averages, color='orange', label='Moving average')  # Moving average line

ids = 200
before = 0
after = 0
for user_time in user_start_times[1::200]:
    # Find the request before and after the user start time
    print(f'Plotting users {ids}')
    before_idx = max(i for i, t in enumerate(request_start_times) if t < user_time)
    after_idx = min(i for i, t in enumerate(request_start_times) if t > user_time)
    after = before_idx
    mean_interval = -1
    if len(times[before:after]) != 0:
        mean_interval = sum(times[before:after]) / len(times[before:after])
    before = after + 1
    # Add a vertical line between the requests
    plt.axvline(x=(before_idx + after_idx) / 2, color=(1, ((ids - 200)/2000), ((ids-200)/2000)), linestyle='--', label=f'Latency at {ids} users: {mean_interval}')
    ids += 200

plt.xlabel('User request id')
plt.ylabel('Time (seconds)')
plt.legend(fontsize="12")

# Save the plot
plt.tight_layout()
plt.savefig("test3.pdf", format='pdf')
