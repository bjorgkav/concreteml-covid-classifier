import rsa, os, pandas, numpy
from pandas import DataFrame, read_csv

def generateKeys(bits):
    (publicKey, privateKey) = rsa.newkeys(bits)
    filename = "publicKey.pem"
    with open(os.path.join(os.path.dirname(__file__), filename), 'wb') as p:
        p.write(publicKey.save_pkcs1('PEM'))
    filename = "privateKey.pem"
    with open(os.path.join(os.path.dirname(__file__), filename), 'wb') as p:
        p.write(privateKey.save_pkcs1('PEM'))
    # with open('rsa_keys/privateKey.pem', 'wb') as p:
    #     p.write(privateKey.save_pkcs1('PEM'))

def loadKeys():
    with open('publicKey.pem', 'rb') as p:
        publicKey = rsa.PublicKey.load_pkcs1(p.read())
        # p.write(publicKey)
    with open('privateKey.pem', 'rb') as p:
        privateKey = rsa.PrivateKey.load_pkcs1(p.read())
        # p.write(privateKey)
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
    
# if not os.path.exists("rsa_keys"): os.mkdir(os.path.join(os.path.dirname(__file__), "rsa_keys"))

generateKeys(3072)
privateKey, publicKey = loadKeys()

file_path=os.path.join(os.path.dirname(__file__), "b.1.1.529output5.csv")
clear_size = get_size(file_path, 'kb')
print("Clear size (kB): ", clear_size)

ciphertext = []
clear_input = open(file_path, "r")
for line in clear_input.readlines():
    encrypted_input = encrypt(line, publicKey)
    ciphertext.append(encrypted_input)

# message = "encryptsdfgdsfsdfsdfsdfedsffedsfsdfdsfddffdsffd"

# ciphertext = encrypt(message, publicKey)
# signature = sign(message, privateKey)
# text = decrypt(ciphertext, privateKey)

# print(f'Cipher text: {ciphertext}')
# print(f'Signature: {signature}')

filename = "encrypted_input.txt"
with open(os.path.join(os.path.dirname(__file__), filename), "wb") as enc_file:
    for line in ciphertext:
        enc_file.write(line)
    # enc_file.write(ciphertext)

file_path=os.path.join(os.path.dirname(__file__), "encrypted_input.txt")
cipher_size = get_size(file_path, 'kb')
print("Ciphertext size (kB): ", cipher_size)

file_path=os.path.join(os.path.dirname(__file__), "publicKey.pem")
pub_size = get_size(file_path, 'kb')
print("Pubkey size (kB): ", pub_size)

file_path=os.path.join(os.path.dirname(__file__), "privateKey.pem")
priv_size = get_size(file_path, 'kb')
print("Privkey size (kB): ", priv_size)
