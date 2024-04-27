#https://github.com/user8547/fast-ecc-python/blob/master/secp256r1_python.py
#Imports
import requests
import os
from dotenv import load_dotenv
import gmpy2 as gmpy
#Defining constants
load_dotenv() 
API_KEY = os.getenv("API_KEY")
QRN_URL = "https://api.quantumnumbers.anu.edu.au/"

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

def bi(s):
    i = 0
    for c in s:
        i <<= 8
        i |= ord(c)
    return i

class Elliptic_curve:
    def __init__(self) -> None:
        #Defines curve parameters: Brainpool P-160-r1
        self.p = int(0xE95E4A5F737059DC60DFC7AD95B3D8139515620F)
        self.a = int(0x340E7BE2A280EB74E2BE61BADA745D97E8F7C300)
        self.b = int(0x1E589A8595423412134FAA2DBDEC95C8D8675E58)
        self.Gx = int(0xBED5AF16EA3F6A4F62938C4631EB5AF7BDBCDBC3)
        self.Gy = int(0x1667CB477A1A8EC338F94741669C976316DA6321)
        self.G = [self.Gx, self.Gy]
        self.q = int(0xE95E4A5F737059DC60DF5991D45029409E60FC09)

    def inv(self, P):
        x = P[0]

        if x==None:
            return [None,None]

        y = P[1]
        backer = [x,-y % self.p]
        return backer

    def ecc_add(self, P, Q):
        '''
        Calculates P + Q on the elliptic curve
            P: Point on the curve
            Q: Point on the curve
        '''
        if P==Q:
            return self.ecc_double(P)
        if P[0]==None:
            return Q
        if Q[0]==None:
            return P
        if Q==self.inv(P):
            return [None, None]
        x1 = P[0]; y1 = P[1]
        x2 = Q[0]; y2 = Q[1]
        beta = (y1-y2) * gmpy.invert((x1-x2), self.p) % self.p
        x3 = (pow(beta, 2, self.p) - x1 - x2) % self.p
        y3 = (beta*(x1-x3) - y1) % self.p
        return [x3, y3]

    def ecc_double(self, P):
        '''
        Calculates 2P on the elliptic curve
            P: Point on the curve
            a: Curve parameter
        '''
        if P[0]==None:
            return P
        if P[1]==0:
            return [None, None]
        x  = P[0]; y = P[1]
        beta = (3 * pow(x, 2, self.p) + self.a) * gmpy.invert(2*y, self.p) % self.p
        backer_x = (pow(beta, 2, self.p) - 2*x) % self.p
        backer_y = (beta*(x - backer_x) - y) % self.p
        return [backer_x, backer_y]

    def double_and_add(self, P, n):
        '''
        Calculates nP mod m with
            P: Point on curve
            n: Integer
            a: Curve parameter
            mod: Prime modulo
        '''
        bits = bin(n)
        bits = bits[2:len(bits)] #get rid if unnecessary leading '0b'
        bits = bits[1:len(bits)]
        backer = (None, None)
        while n:
            bit = n % 2
            n = n >> 1
            if bit == '1':
                backer = self.ecc_add(backer, P)
            backer = self.ecc_double(backer)
        return backer


#Preparation
print("GENERATING KEYS:")
curve = Elliptic_curve()
response, private_key = get_random_number(QRN_URL=QRN_URL, API_KEY=API_KEY)
if private_key == 0:
    print("Failed to generate private_key --> aborting with response code: ", response)
    exit(1)
print("Private key: ", private_key)
public_key = curve.double_and_add(curve.G, private_key)
print("Public key: ", public_key)
#Algorithm