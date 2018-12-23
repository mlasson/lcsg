import base64
import argparse
from getpass import getpass
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source)
    return base64.b64encode(data).decode("latin-1") if encode else data

def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding...")
    return data[:-padding]

def encrypt_file(key, input_file, output_file):
    with open(input_file, 'rb') as input:
        data = input.read()
        with open(output_file, 'w') as output:
            output.write(encrypt(key, data))

def decrypt_file(key, input_file, output_file):
    with open(input_file, 'r') as input:
        data = input.read()
        with open(output_file, 'wb') as output:
            output.write(decrypt(key, data))


global_key = None

def getkey():
    global global_key
    if not global_key:
        global_key = getpass('Enter the passphrase: ').encode('utf-8')
    return global_key

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--encrypt", help="encrypt the file", action="store_true")
    parser.add_argument("--decrypt", help="decrypt the file", action="store_true")
    parser.add_argument("input", help="the input file")
    parser.add_argument("output", help="the output file")
    args = parser.parse_args()
    if args.encrypt and not(args.decrypt):
        key = getkey()
        encrypt_file(key, args.input, args.output)
    elif not(args.encrypt) and args.decrypt:
        key = getkey()
        decrypt_file(key, args.input, args.output)
    else:
        print('Do not know what to do')

if __name__ == '__main__':
    main()