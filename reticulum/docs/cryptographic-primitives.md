# Cryptographic Primitives
Reticulum nodes communicate with cryptographic identities, using asymmetric key cryptography to establish ephemeral symmetric keys for encryption.

|**Method**|**What it does**|
|:---|:---|
|Ed25519|Digital signature scheme for authentication. Creates a public-private key pair for each identity.|
|X25519 (Elliptic Curve Diffie-Hellman, ECDH)|Establishes a shared secret|
|HKDF|Turns the shared secret from ECDH into symmetric keys. The symmetric keys are ephemeral, ensuring Perfect Forward Secrecy|
|AES-256-CBC|Encrypts data using symmetric keys with a random IV (Initialisation Vector)|
|HMAC-SHA256|Authenticates the packet. Ensures no tampering/corruption of packets.|
|Fernet Style Tokens|Takes in ciphertext + IV + HMAC → token which is used to package encrypted data|

## How Authentication Works
When sending a message,

1. Have shared secret key (from HKDF)

2. Encrypt: ciphertext = AES(key_enc, message)

3. Authenticate: mac = HMAC(key_mac, ciphertext)

4. Send: [ciphertext | mac]

Attackers cannot forge a mac without knowing the shared key.

