import requests

url = 'http://localhost/login'
data = {'username': 'admin', 'password': 'faspassword'}

for i in range(2):
    try:
        response = requests.post(url, data=data)
        print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")
