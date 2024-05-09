using Org.BouncyCastle.Asn1.Sec;
using Org.BouncyCastle.Asn1.X9;
using Org.BouncyCastle.Crypto;
using Org.BouncyCastle.Crypto.Generators;
using Org.BouncyCastle.Crypto.Parameters;
using Org.BouncyCastle.Security;

public class Program
{
    public static void Main()
    {
        // Define the secp256k1 curve
        X9ECParameters curve = SecNamedCurves.GetByName("secp256k1");
        ECDomainParameters domainParams = new ECDomainParameters(curve.Curve, curve.G, curve.N, curve.H, curve.GetSeed());

        // Generate a private key with a custom random number generator
        SecureRandom secureRandom = new SecureRandom();
        ECKeyGenerationParameters keyGenParams = new ECKeyGenerationParameters(domainParams, secureRandom);
        AsymmetricCipherKeyPair keyPair;
        ECKeyPairGenerator generator = new ECKeyPairGenerator();
        generator.Init(keyGenParams);
        keyPair = generator.GenerateKeyPair();

        // Get the public key
        ECPublicKeyParameters publicKey = (ECPublicKeyParameters)keyPair.Public;

        // Sign a message
        string message = "Hello, World!";
        byte[] messageBytes = Encoding.UTF8.GetBytes(message);
        ISigner signer = SignerUtilities.GetSigner("SHA-256withECDSA");
        signer.Init(true, keyPair.Private);
        signer.BlockUpdate(messageBytes, 0, messageBytes.Length);
        byte[] signature = signer.GenerateSignature();

        // Verify the signature
        signer.Init(false, publicKey);
        signer.BlockUpdate(messageBytes, 0, messageBytes.Length);
        bool isVerified = signer.VerifySignature(signature);
    }
}
