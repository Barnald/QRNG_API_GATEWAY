#https://github.com/user8547/fast-ecc-python/blob/master/secp256r1_python.py
#Imports
import requests
import os
from dotenv import load_dotenv
import math
import hashlib
from api import get_random_int
import asyncio
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
    s1 = curve.mod_inverse(s, curve.n)
    R = curve.double_and_add(curve.G, (hashed_message*s1))
    R_second = curve.double_and_add(public_key, (r*s1))
    R = curve.ecc_add(R, R_second)
    r1 = R[0] % curve.n
    print("r=", r)
    print("r1=", r1)
    return r1==r

class Elliptic_curve:
    def __init__(self) -> None:
        #Defines curve parameters: Brainpool P-160-r1
        #secp256k1
        #self.p = 115792089237316195423570985008687907852837564279074904382605163141518161494337#2**256-2**32-2**9-2**8-2**7-2**6-2**4-1#
        self.n = 115792089237316195423570985008687907852837564279074904382605163141518161494337
        self.a = 0#0
        self.b = 7#7
        self.Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240#0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798#
        self.Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424#0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8#
        self.G = [self.Gx, self.Gy]
        #self.q = 115792089237316195423570985008687907852837564279074904382605163141518161494337#0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141#
        #self.p = self.q
        
    def inv(self, P):
        x = P[0]

        if x==None:
            return [None,None]

        y = P[1]
        backer = [x,-y % self.n]
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
        lamb = ((y2-y1) * self.mod_inverse((x2-x1), self.n)) % self.n
        x3 = (lamb**2 - x1 - x2) % self.n
        y3 = (lamb*x1-lamb*x3 - y1) % self.n
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
        lamb = ((3 * (x**2) + self.a) * self.mod_inverse(2*y, self.n)) % self.n
        backer_x = (lamb**2 - 2*x) % self.n
        backer_y = (- lamb*backer_x + lamb*x - y) % self.n
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

async def demo():    
    #Preparation
    print("GENERATING KEYS:")
    curve = Elliptic_curve()
    #private_key = random.getrandbits(256)
    response = await get_random_int(256, curve.n-1)
    if response['success']=='false':
        exit(1)
    private_key = response['data']
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

    #generating random number for the signature
    response = await get_random_int(256, curve.n-1)
    if response['success']=='false':
        exit(1)
    k = response['data']
    #calculate the random point using k
    R = curve.double_and_add(curve.G, k)

    #get the first part of the signature, then calculate the sign proof
    r = R[0] % curve.n
    s = curve.mod_inverse(k, curve.n) * (hashed_message + r*private_key) % curve.n
    print("Sign: (r, s): ", r, s)

    output = verify_signature(message=message, public_key=public_key, r=r, s=s, curve=curve)

    print(output)

    print(private_key)
    print(public_key)
    print(hashed_message)
    print(k)
    print(r)
    print(s)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(demo())
    loop.close()

if __name__ == "__main__":
    main()