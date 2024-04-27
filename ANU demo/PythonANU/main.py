import json
import requests

def fetch_and_print_articles(api_url):
    response = requests.get(api_url)
    articles = ""

    if response.status_code == 200:
        articles = response.json()
    else:
        print(f"Error: {response.status_code}")
    return response, articles

def get_random_uint16(api_url):
    response = requests.get(api_url)
    articles = ""

    if response.status_code == 200:
        articles = response.json()
    else:
        print(f"Error: {response.status_code}")
    backer = articles['data'][0]
    return response, backer


api_endpoint = f"https://qrng.anu.edu.au/API/jsonI.php?length=1&type=uint16"

response, random_number = get_random_uint16(api_endpoint)

def jprint(obj):
	print(json.dumps(obj, sort_keys=True, indent=4))

#item = {'type': 'uint16', 'length': 1, 'data': [5786], 'success': True}
#print(item['data'][0])
print("Return code: {}".format(response.status_code))
print(random_number)