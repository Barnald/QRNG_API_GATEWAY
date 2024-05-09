#Imports
import hashlib
from api import get_random_int
import asyncio
from EllipticCurve import Elliptic_curve

#Functions
def hash_text_to_int(text):
    hash = hashlib.sha1(text).hexdigest()
    return int(hash, 16)

def verify_signature(message:str, public_key, r:int, s:int, curve:Elliptic_curve):
    print("Verifying...")
    message = message.encode('ascii')
    hashed_message = hash_text_to_int(message)
    w = curve.mod_inverse(s, curve.n)
    u1 = hashed_message*w % curve.n
    u2 = r*w % curve.n
    X = curve.ecc_add(curve.double_and_add(curve.G, u1), curve.double_and_add(public_key, u2))
    v = int(X[0]) % curve.n
    print("->Got r=", r)
    print("->Calculated v=", v)
    return r == v

async def generate_key(curve: Elliptic_curve):
    response = await get_random_int(256, curve.n)
    if response['success']=='false':
        return generate_key(curve)
    private_key = response['data']
    if private_key == 0:
        return generate_key(curve)
    public_key = curve.double_and_add(curve.G, private_key)
    return [private_key, public_key]

async def ecdsa_sign(message:str, private_key:int, curve:Elliptic_curve):
    print("Signing...")
    message = message.encode('ascii')
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
    return [r, s]

async def demo():    
    #Preparation
    print("Generating keys:")
    curve = Elliptic_curve()
    private_key, public_key = await generate_key(curve)
    print("->Private key: ", private_key)
    print("->Public key: ", public_key)
    
    #Algorithm
    #Sign
    #message = 'Hello PARIPA!'
    message = input("Give the message: ")
    print("Message to be signed: ", message)
    r, s = await ecdsa_sign(message, private_key, curve)
    print("->Signature: (r, s): ({}, {})".format(r, s))

    #Verify
    output = verify_signature(message=message, public_key=public_key, r=r, s=s, curve=curve)
    if output:
        output = "Valid"
    else:
        output = "Invalid"
    print("Result of the verification: {} signature".format(output))

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(demo())
    loop.close()

if __name__ == "__main__":
    main()