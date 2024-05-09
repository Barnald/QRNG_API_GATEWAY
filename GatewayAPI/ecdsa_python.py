import ecdsa
import os
from api import get_random_int
import asyncio

async def demo():
    # Define the secp256k1 curve
    curve = ecdsa.SECP256k1

    # Generate a private key
    private_key = ecdsa.SigningKey.generate(curve=curve, entropy=await get_random_int(256, 200000000))

    # Get the corresponding public key
    public_key = private_key.get_verifying_key()

    # Sign a message
    message = b"Hello, World!"
    signature = private_key.sign(message)

    # Verify the signature
    assert public_key.verify(signature, message)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(demo())
    loop.close()

if __name__ == "__main__":
    main()