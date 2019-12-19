import requests

url = 'http://127.0.0.1:5000/api/imageurl'

params = dict(
    query="Diana Lounger_F268",
    nitems=2
)

resp = requests.get(url=url, params=params)
data = resp.json()
print(data)
print(data["url"])
print(data["url"].split("\\"))
print(data["url"].split("\\")[-1])