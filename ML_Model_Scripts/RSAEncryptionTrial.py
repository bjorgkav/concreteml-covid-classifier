import rsa, os

def generateKeys(bits = 1024):
    (publicKey, privateKey) = rsa.newkeys(bits)
    with open('publicKey.pem', 'wb') as p:
        p.write(publicKey.save_pkcs1('PEM'))
    with open('privateKey.pem', 'wb') as p:
        p.write(privateKey.save_pkcs1('PEM'))

def loadKeys():
    with open('publicKey.pem', 'rb') as p:
        publicKey = rsa.PublicKey.load_pkcs1(p.read())
    with open('privateKey.pem', 'rb') as p:
        privateKey = rsa.PrivateKey.load_pkcs1(p.read())
    return privateKey, publicKey

def encrypt(message, key):
    return rsa.encrypt(message.encode('ascii'), key)

def decrypt(ciphertext, key):
    try:
        return rsa.decrypt(ciphertext, key).decode('ascii')
    except:
        return False
    
def sign(message, key):
    return rsa.sign(message.encode('ascii'), key, 'SHA-1')

def verify(message, signature, key):
    try:
        return rsa.verify(message.encode('ascii'), signature, key,) == 'SHA-1'
    except:
        return False

def get_size(file_path, unit='bytes'):
        file_size = os.path.getsize(file_path)
        exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
        if unit not in exponents_map:
            raise ValueError("Must select from \
            ['bytes', 'kb', 'mb', 'gb']")
        else:
            size = file_size / 1024 ** exponents_map[unit]
            return round(size, 3)

generateKeys(3072)
privateKey, publicKey = loadKeys()

message = "Sample messagwserdtcvfgybuhnijmoke"

ciphertext = encrypt(message, publicKey)
signature = sign(message, privateKey)
text = decrypt(ciphertext, privateKey)

# print(f'Cipher text: {ciphertext}')
# print(f'Signature: {signature}')

with open(os.path.join(os.path.dirname(__file__), 'encrypted_input.txt'), "wb") as f:
    f.write(ciphertext)

print(f"size of RSA-encrypted message \"{message}\" : {get_size(os.path.join(os.path.dirname(__file__), 'encrypted_input.txt'),'kb')} kB")


message = "other sample messageextfcygvubhinjkml"

ciphertext = encrypt(message, publicKey)
signature = sign(message, privateKey)
text = decrypt(ciphertext, privateKey)

print(f"size of RSA-encrypted message \"{message}\" : {get_size(os.path.join(os.path.dirname(__file__), 'encrypted_input.txt'),'kb')} kB")

# if text:
#     print(f'Message text: {text}')
# else:
#     print(f'Unable to decrypt the message.')

# if verify(text, signature, publicKey):
#     print("Successfully verified signature")
# else:
#     print('The message signature could not be verified')
