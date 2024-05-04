import requests 

ethz_url = "http://qrng.ethz.ch/api/randint"

params = {"min": 0, "max": 1, "size":256}
response = requests.get(ethz_url, headers=None, params=params)

#Calling ETHZ API
print(response.request.url)
print(response.json())
print(response.json()['result'])