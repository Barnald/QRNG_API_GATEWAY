#https://github.com/user8547/fast-ecc-python/blob/master/secp256r1_python.py
#Imports
import requests
import os
from dotenv import load_dotenv
import math
import hashlib
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

def hash_text(text):
    hash = hashlib.sha256(str(text).encode("utf-8")).hexdigest()
    return int(hash, 16)


def verify_signature(message, public_key, r, s, curve):
    print("Verifying...")
    hashed_message = hash_text(message)
    s1 = curve.mod_inverse(s, curve.p)
    R = curve.double_and_add(curve.G, (hashed_message*s1))
    R_second = curve.double_and_add(public_key, (r*s1))
    R = curve.ecc_add(R, R_second)
    r1 = R[0]
    print("r=", r)
    print("r1=", r1)
    return r1==r

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
        #print(self.G)

    def inv(self, P):
        x = P[0]

        if x==None:
            return [None,None]

        y = P[1]
        backer = [x,-y % self.p]
        return backer

    def mod_inverse(self, x, m):
        '''
        Calculates modular inverse for x mod m
        '''
        if x < 0:
            x = (x + m * int(abs(x)/m) + m) % m
        if math.gcd(x, m)!=1:
            return None
        u1, u2, u3 = 1, 0, x
        v1, v2, v3 = 0, 1, m
        while v3 != 0:
        
            # // is the integer division operator
            q = u3 // v3 
            v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
        return u1 % m
        
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
        lamb = ((y2-y1) * self.mod_inverse((x2-x1), self.p)) % self.p
        x3 = (lamb**2 - x1 - x2) % self.p
        y3 = (lamb*x1-lamb*x3 - y1) % self.p
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
        lamb = ((3 * (x**2) + self.a) * self.mod_inverse(2*y, self.p)) % self.p
        backer_x = (lamb**2 - 2*x) % self.p
        backer_y = (- lamb*backer_x + lamb*x - y) % self.p
        return [backer_x, backer_y]

    def double_and_add(self, P, n):
        '''
        Calculates nP mod m with
            P: Base point on curve
            n: Integer
        '''
        bits = bin(n)
        bits = bits[2:len(bits)] #get rid if unnecessary leading '0b'
        #bits = bits[1:len(bits)] #the first bit will be ignored
        backer = (P[0], P[1])
        for i in range(1, len(bits)):
            bit = bits[i:i+1]
            backer = self.ecc_double(backer)
            if bit == '1':
                backer = self.ecc_add(backer, P)
        return backer
    def get_n_leftmost_bits(self, hash):
        bits = bin(hash)
        return bits[:self.q]

#Preparation
print("GENERATING KEYS:")
curve = Elliptic_curve()
#private_key = random.getrandbits(256)
response, private_key = get_random_number(QRN_URL=QRN_URL, API_KEY=API_KEY)
private_key = private_key % curve.p
if private_key == 0:
    print("Failed to generate private_key --> aborting with response code: ", response)
    exit(1)
print("Private key: ", private_key)
public_key = curve.double_and_add(curve.G, private_key)
print("Public key: ", public_key)

#Algorithm

#prepearing message and its hash
message = "Hello PARIPA!"
print("Message: ", message)
hashed_message = hash_text(message)

#output = verify_signature(message=message, public_key=public_key, r=0xA7001557138BF1B5B434CC94D87B236235589087, s=0x172CE80F486EDE5B38EA180F0F65F6B41770272F, curve=curve)

#print(output)
#exit(0)

#generating random number for the signature
response, k = get_random_number(QRN_URL=QRN_URL, API_KEY=API_KEY) 
k = k % curve.p
#calculate the random point using k
R = curve.double_and_add(curve.G, k)

#get the first part of the signature, then calculate the sign proof
r = R[0]
s = curve.mod_inverse(k, curve.p) * (hashed_message + r*private_key) % curve.p
print("Sign: (r, s): ", r, s)

output = verify_signature(message=message, public_key=public_key, r=r, s=s, curve=curve)

print(output)

print(private_key)
print(public_key)
print(hashed_message)
print(k)
print(r)
print(s)
