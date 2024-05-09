from dotenv import load_dotenv 
import os

def get_anu_params(size_in_bits:int):
    load_dotenv()

    anu_url = "https://qrng.anu.edu.au/API/jsonI.php"
    API_KEY = os.getenv("API_KEY")
    DTYPE = "uint8"

    params = {"length": size_in_bits, "type": DTYPE}
    headers = {"x-api-key": API_KEY}

    return [anu_url, headers, params]

def get_ethz_params(size_in_bits):
    ethz_url = "http://qrng.ethz.ch/api/randint"
    params = {"min": 0, "max": 1, "size":size_in_bits}
    return ethz_url, None, params