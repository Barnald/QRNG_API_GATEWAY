import ecdsa
import os

# Define the secp256k1 curve
curve = ecdsa.SECP256k1

# Generate a custom random number
def custom_random_number(numbytes):
    return int.from_bytes(os.urandom(numbytes), byteorder='big')

# Generate a private key
private_key = ecdsa.SigningKey.generate(curve=curve, entropy=custom_random_number)

# Get the corresponding public key
public_key = private_key.get_verifying_key()

# Sign a message
message = b"Hello, World!"
signature = private_key.sign(message)

# Verify the signature
assert public_key.verify(signature, message)
