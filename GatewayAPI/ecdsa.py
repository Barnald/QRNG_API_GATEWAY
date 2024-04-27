#Imports
import requests
import os
from dotenv import load_dotenv
#Defining constants
load_dotenv() 
API_KEY = os.getenv("API_KEY")
QRN_URL = "https://api.quantumnumbers.anu.edu.au/"
#Defines curve parameters: Brainpool P-160-r1
_a = 0x340E7BE2A280EB74E2BE61BADA745D97E8F7C300
_b = 0x1E589A8595423412134FAA2DBDEC95C8D8675E58
_p = 0xE95E4A5F737059DC60DFC7AD95B3D8139515620F
_Gx = 0xBED5AF16EA3F6A4F62938C4631EB5AF7BDBCDBC3
_Gy = 0x1667CB477A1A8EC338F94741669C976316DA6321
_q = 0xE95E4A5F737059DC60DF5991D45029409E60FC09

#Functions
'''
Calls remote API to get a Quatnum Random Number
'''
def get_random_number(QRN_URL, API_KEY):
	DTYPE = "hex16"  # uint8, uint16, hex8, hex16
	LENGTH = 1  # between 1--1024
	BLOCKSIZE = 10  # between 1--10. Only needed for hex8 and hex16

	params = {"length": LENGTH, "type": DTYPE, "size": BLOCKSIZE}
	headers = {"x-api-key": API_KEY}

	response = requests.get(QRN_URL, headers=headers, params=params)

	backer = 0
	if response.status_code == 200:
		backer = response.json()
	else:
		print(f"Error: {response.status_code}")

	return response, int(backer['data'][0], 16)

'''
Calculates P + Q on the elliptic curve
    P: Point on the curve
    Q: Point on the curve
'''
def ecc_add(P, Q, mod):
    x1 = P[0]; y1 = P[1]
    x2 = Q[0]; y2 = Q[1]
    beta = (y2-y1)/(x2-x1)
    x3 = (beta**2 - x1 - x2) % mod 
    y3 = (beta*(x1-x3) - y1) % mod
    return (x3, y3)

'''
Calculates 2P on the elliptic curve
    P: Point on the curve
    a: Curve parameter
'''   
def ecc_double(P, a, mod):
    x1  = P[0]; y1 = P[1]
    beta = (3 * (x1**2) - a)/(2*y1)
    x3 = beta**2 - 2*x1
    y3 = beta(x1 - x3) - y1
    return (x3, y3)

'''
Calculates nP mod m with
    P: Point on curve
    n: Integer
    a: Curve parameter
    mod: Prime modulo
'''
def double_and_add(P, n, a, mod):
    bits = bin(n)
    bits = bits[2:len(bits)] #get rid if unnecessary leading '0b'
    bits = bits[1:len(bits)] #in the algorithm the first bit is ignored
    backer = (P[0], P[1])
    for bit in bits:
        backer = ecc_double(backer, mod)
        if bit == '1':
            backer = ecc_add(backer, P, mod)
    return backer


#Preparation
print("GENERATING KEYS:")
private_key = get_random_number()
if private_key == 0:
    print("Failed to generate private_key --> aborting")
    exit(1)
public_key = double_and_add()

#Algorithm