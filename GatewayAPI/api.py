from fastapi import FastAPI
import requests
import uvicorn
from getConnections import get_anu_params, get_ethz_params

app = FastAPI()

@app.get("/int/{size_in_bits}/{max}")
async def get_random_int(size_in_bits: int, max: int):
    ''''
    Function to call a QRNG API provider for random integer.
        size_in_bits: Integer that represents the size of the number in bits.
        max: Integer that represents the maximum value for the generation. (Exclusive)
    Returns: JSON object, containing 3 fields:
        success: Shows if the request was successful -> {true, false}
        provider: Shows which provider sent the random number
        data: Contains the random number in decimal   
    '''
    #Calling ANU API
    anu_url, headers, params = get_anu_params(size_in_bits)
    response = requests.get(anu_url, headers=headers, params=params)

    backer = 0
    if response.status_code == 200:
        json = response.json()
        processed_data = ""
        for number in json['data']:
            processed_data += str(number%2)
        backer = int(processed_data, 2) % max
        return {"success":"true", "provider":"ANU", "data":backer}

    #Calling ETHZ API
    ethz_url, headers, params = get_ethz_params(size_in_bits)
    response = requests.get(ethz_url, headers=headers, params=params)

    if response.status_code == 200:
        json = response.json()
        backer = ""
        for bit in json['result']:
            backer += str(bit)
        backer = int(backer, 2) % max
        return {'success':'true', 'provider':'ETHZ', 'data':backer}
    return {'success':'false', 'provider':'none', 'data':-1}

@app.get("/hex/{size_in_bits}/{max}")
async def get_random_hex(size_in_bits: int, max: int):
    ''''
    Function to call a QRNG API provider for random hexadecimal number.
        size_in_bits: Integer that represents the size of the number in bits.
        max: Integer that represents the maximum value for the generation.
    Returns: JSON object, containing 3 fields:
        success: Shows if the request was successful -> {true, false}
        provider: Shows which provider sent the random number
        data: Contains the random number in hexadecimal   
    '''
    response = await get_random_int(size_in_bits=size_in_bits, max=max)
    if response['success'] == 'false':
        return response
    
    number = hex(response['data'])
    response['data'] = number
    return response

@app.get("/bin/{size_in_bits}/{max}")
async def get_random_bin(size_in_bits: int, max: int):
    ''''
    Function to call a QRNG API provider for random binary number.
        size_in_bits: Integer that represents the size of the number in bits.
        max: Integer that represents the maximum value for the generation.
    Returns: JSON object, containing 3 fields:
        success: Shows if the request was successful -> {true, false}
        provider: Shows which provider sent the random number
        data: Contains the random number in binary   
    '''
    response = await get_random_int(size_in_bits=size_in_bits, max=max)
    if response['success'] == 'false':
        return response
    
    number = bin(response['data'])
    response['data'] = number
    return response


if __name__ == "__main__":
    uvicorn.run("api:app", port=5000, log_level="info")
