#include <openssl/ec.h>
#include <openssl/obj_mac.h>
#include <openssl/rand.h>

int main() {
    EC_KEY *key = EC_KEY_new_by_curve_name(NID_secp256k1);

    // Generate a new private key with a custom random number generator
    EC_KEY_generate_key(key);

    // Get the public key
    const EC_POINT *public_key = EC_KEY_get0_public_key(key);

    // Sign a message
    const char *message = "Hello, World!";
    unsigned char hash[32];
    SHA256((unsigned char*)message, strlen(message), hash);
    ECDSA_SIG *signature = ECDSA_do_sign(hash, sizeof(hash), key);

    // Verify the signature
    int verified = ECDSA_do_verify(hash, sizeof(hash), signature, key);

    // Cleanup
    ECDSA_SIG_free(signature);
    EC_KEY_free(key);

    return 0;
}
