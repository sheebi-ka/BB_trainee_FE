import requests

def get_api(base_url, endpoint):
    return requests.get(f"{base_url}{endpoint}")

def post_api(base_url, endpoint, data):
    url = f"{base_url}{endpoint}"
    return requests.post(url, json=data)

def put_api(base_url, endpoint, data):
    return requests.put(f"{base_url}{endpoint}", json=data)

def delete_api(base_url, endpoint):
    return requests.delete(f"{base_url}{endpoint}")
