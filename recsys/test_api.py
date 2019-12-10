import requests

url = 'http://127.0.0.1:5000/api/similar'

params = dict(
    productid=100,
    nitems=50
)

resp = requests.get(url=url, params=params)
data = resp.json()
print(data)