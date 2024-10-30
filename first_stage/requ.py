import requests
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
import matplotlib.colors as mcolors
import threading


url = [
    'http://localhost:8080/login',
    'http://localhost:8081/login',
    'http://localhost:8082/login',
    'http://localhost:8083/login',
    'http://localhost:8084/login'
]
data = {'username': 'admin', 'password': 'password'}


# Function to send a single request
def send_request(user_id):
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
    if user_id == 0:
        successful_requests = 0
        failed_requests = 0
        requests_time = []
        # Lists to store performance data
        request_times = []  # Store time taken for each request
        start_time = time.time()
        while True:
            request_start_time = time.time()  # Time before request
            try:
                choice = random.choice(url)
                chosen.append(choice)
                response = requests.post(choice, headers=headers, data=data)
                request_end_time = time.time()  # Time after request
                requests_time.append(request_end_time)
                request_duration = request_end_time - request_start_time

                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
                # Append performance data
                request_times.append(request_duration)
                if 'User-Key-Signatures' in response.headers:
                    #number_of_sign.append((len(response.headers['User-Key-Signatures'].split(":")) - 1) / 2)
                    headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

            except Exception as e:
                request_end_time = time.time()
                print(f"An error occurred in worker {user_id}: {e}")
                request_duration = request_end_time - request_start_time
                requests_time.append(request_end_time)
                failed_requests += 1
                # Append performance data
                request_times.append(request_duration)
            check_time = time.time()
            if check_time - start_time > ((1000 - user_id) * 3):
                break
        return [successful_requests + failed_requests, request_times, requests_time, start_time, user_id]
    else:
        start_time = time.time()
        while True:
            try:
                choice = random.choice(url)
                chosen.append(choice)
                response = requests.post(choice, headers=headers, data=data)

                if 'User-Key-Signatures' in response.headers:
                    headers['User-Key-Signatures'] = response.headers['User-Key-Signatures']

            except Exception as e:
                print(f"An error occurred in worker {user_id}: {e}")
            check_time = time.time()
            if check_time - start_time > ((1000 - user_id) * 3):
                break
        return [0, [], [], start_time, user_id]


all_results = []
# Function to send multiple requests in parallel
with ThreadPoolExecutor(max_workers=1000) as executor:
    futures = []
    for j in range(1000):
        print(f"Starting user {j}")
        futures.append(executor.submit(send_request, j))  # Launch 100 threads
        time.sleep(3)

    for future in as_completed(futures):
        all_results.append(future.result())

sorted_results = sorted(all_results, key=lambda x: x[-1])

plt.figure(figsize=(10, 8))

new_list = []
request_start_times = []
user_start_times = []
# Iterate through each sublist and extend the new list with the 4th element (which is a list)
for sublist in sorted_results:
    new_list.extend(sublist[1])
    request_start_times.extend(sublist[2])
    user_start_times.append(sublist[3])


mean = sum(new_list) / sum(sublist[0] for sublist in sorted_results)
# Plot request durations
plt.subplot(1, 1, 1)
plt.plot(new_list, marker='o', linestyle='-', color='b', label='Request Time (s)')
plt.axhline(y=mean, color='k', linestyle='--', label=f'Overall Mean: {mean}')
ids = 100
before = 0
after = 0
for user_time in user_start_times[1::100]:
    # Find the request before and after the user start time
    print(f'Plotting users {ids}')
    before_idx = max(i for i, t in enumerate(request_start_times) if t < user_time)
    after_idx = min(i for i, t in enumerate(request_start_times) if t > user_time)
    after = before_idx
    mean_interval = sum(new_list[before:after]) / len(new_list[before:after])
    before = after + 1
    # Add a vertical line between the requests
    color = mcolors.to_rgba((1, 0, 0), alpha=1 - 0.1 * (ids/100))
    plt.axvline(x=(before_idx + after_idx) / 2, color=color, linestyle='--', label=f'Latency with {ids} users is {mean_interval}')
    ids += 100

plt.xlabel('Request Number')
plt.ylabel('Time (seconds)')
plt.title('Request Duration Over Time')
plt.legend()

# # Plot success vs failure
# plt.subplot(3, 1, 2)
# plt.plot(res_request_statuses, marker='o', linestyle='-', color='r', label='Success (1) / Failure (0)')
# plt.xlabel('Request Number')
# plt.ylabel('Status')
# plt.title('Request Success and Failure Over Time')
# plt.legend()
#
# # Plot success vs failure
# plt.subplot(3, 1, 3)
# plt.plot(res_number_of_sign, marker='o', linestyle='-', color='g', label='Signatures')
# plt.xlabel('Signatures per request')
# plt.ylabel('Number of signatures')
# plt.title('Signatures per request')
# plt.legend()

# mean = sum(res_request_times) / len(res_request_times)
# print(f"Mean request time is {mean}")
# Show the plots
plt.tight_layout()
plt.savefig("test3.png", format='png')
plt.show()
