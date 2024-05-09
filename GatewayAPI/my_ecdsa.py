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
def hash_text_to_int(text):
    hash = hashlib.sha1(text).hexdigest()
    return int(hash, 16)


def verify_signature(message, public_key, r, s, curve):
    print("Verifying...")
    hashed_message = hash_text_to_int(message)
    w = curve.mod_inverse(s, curve.n)
    u1 = hashed_message*w % curve.n
    u2 = r*w % curve.n
    X = curve.ecc_add(curve.double_and_add(curve.G, u1), curve.double_and_add(public_key, u2))
    v = int(X[0]) % curve.n
    print("r=", r)
    print("v=", v)
    return r == v

class Elliptic_curve:
    #secp256k1 parameters based on: https://www.secg.org/sec2-v2.pdf
    def __init__(self, p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
            a=0, b=7, Gx=55066263022277343669578718895168534326250603453777594175500187360389116729240,
            Gy=32670510020758816978083085130507043184471273380659243275938904335757337482424,
            n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141) -> None:
        self.p = p
        self.a = a
        self.b = b
        self.Gx = Gx
        self.Gy = Gy
        self.G = [self.Gx, self.Gy]
        self.n = n
        
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
        y3 = (lamb*(x1-x3) - y1) % self.p
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
        backer_y = (lamb*(x-backer_x)-y) % self.p
        return [backer_x, backer_y]

    def double_and_add(self, P, n):
        '''
        Calculates nP mod m with
            P: Base point on curve
            n: Integer
        '''
        bits = bin(n)
        bits = bits[2:len(bits)] #get rid if unnecessary leading '0b'
        bits = bits[1:len(bits)] #the first bit will be ignored
        backer = (P[0], P[1])
        for bit in bits:
            backer = self.ecc_double(backer)
            if bit == '1':
                backer = self.ecc_add(backer, P)
        return backer

async def demo():    
    #Preparation
    print("GENERATING KEYS:")
    curve = Elliptic_curve()
    response = await get_random_int(256, curve.n)
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
    message = b'Hello PARIPA!'
    print("Message: ", message.decode('ascii'))
    hashed_message = hash_text_to_int(message)

    #generating random number for the signature
    k = 0
    while k<1:
        response = await get_random_int(256, curve.n)
        if response['success']=='false':
            exit(1)
        k = response['data']

    #calculate the random point using k
    R = curve.double_and_add(curve.G, k)

    #get the first part of the signature, then calculate the sign proof
    r = int(R[0]) % curve.n
    if r == 0:
        print("r is 0")
        exit(1)
    s = curve.mod_inverse(k, curve.n) * (hashed_message + private_key*r) % curve.n
    if s == 0:
        print('s is 0')
        exit(1)
    print("Sign: (r, s): ", r, s)

    output = verify_signature(message=message, public_key=public_key, r=r, s=s, curve=curve)

    print("Result of the verification: ", output)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(demo())
    loop.close()

if __name__ == "__main__":
    main()