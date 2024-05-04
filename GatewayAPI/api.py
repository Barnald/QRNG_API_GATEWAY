from fastapi import FastAPI
import requests
import uvicorn
import ecdsa
from dotenv import load_dotenv 
import os

app = FastAPI()

@app.get("/int/{size_in_bits}/{max}")
async def get_random_int(size_in_bits: int, max: int):
    load_dotenv()
    anu_url = "https://api.quantumnumbers.anu.edu.au/"
    API_KEY = os.getenv("API_KEY")
    ethz_url = "http://qrng.ethz.ch/api/randint"

    #Calling ANU API
    DTYPE = "uint16"  # uint8, uint16, hex8, hex16
    LENGTH = 1  # between 1--1024

    params = {"length": LENGTH, "type": DTYPE}
    headers = {"x-api-key": API_KEY}

    response = requests.get(anu_url, headers=headers, params=params)

    backer = 0
    if response.status_code == 200:
        json = response.json()
        processed_data = []
        for number in json['data']:
            processed_data.append(number%(max+1))
        json['data'] = processed_data
        return json

    #Calling ETHZ API
    params = {"min": 0, "max": 1, "size":size_in_bits}
    print(params)
    response = requests.get(ethz_url, headers=None, params=params)
    if response.status_code == 200:
        json = response.json()
        print(json)
        backer = ""
        for bit in json['result']:
            backer += str(bit)
        backer = int(backer, 2) % max
        return {'random':backer}
    return {"error":-1}

async def get_random_hex(api_key: str, size_in_bytes: int, quantity: int):
    anu_url = "https://api.quantumnumbers.anu.edu.au/"
    ethz_url = "http://qrng.ethz.ch/api/"

    DTYPE = "hex16"  # uint8, uint16, hex8, hex16
    LENGTH = 1  # between 1--1024
    BLOCKSIZE = 10  # between 1--10. Only needed for hex8 and hex16

    params = {"length": LENGTH, "type": DTYPE, "size": BLOCKSIZE}
    headers = {"x-api-key": api_key}

    response = requests.get(anu_url, headers=headers, params=params)

    backer = 0
    if response.status_code == 200:
        backer = response.json()
    else:
        print(f"Error: {response.status_code}")

    return response, int(backer['data'][0], 16)

if __name__ == "__main__":
    uvicorn.run("api:app", port=5000, log_level="info")