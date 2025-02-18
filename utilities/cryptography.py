from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1, hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend

from base64 import b64decode, b64encode
import json


def load_private_key(private_key_path):
    with open(private_key_path, 'rb') as key_file:
        private_key = load_pem_private_key(
            key_file.read(),
            password='p@jar!t0Lindo'.encode("utf-8"),
            backend=default_backend()
        )
    return private_key


def load_public_key(public_key_path):
    with open(public_key_path, 'rb') as key_file:
        public_key = load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key


def decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
    try:
        # Decode the base64 encoded data
        encrypted_flow_data = b64decode(encrypted_flow_data_b64)
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)
        iv = b64decode(initial_vector_b64)

        # Load the private key
        private_key = load_private_key('private.pem')

        # Decrypt the AES key
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the Flow data
        # Assuming the encrypted flow data includes a tag for GCM mode
        encrypted_flow_data_body = encrypted_flow_data[:-16]
        encrypted_flow_data_tag = encrypted_flow_data[-16:]

        decryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, encrypted_flow_data_tag),
            backend=default_backend()
        ).decryptor()

        decrypted_data_bytes = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
        return decrypted_data, aes_key, iv
    except Exception as e:
        print(f'Error decrypting request: {e}')
        return None, None, None


def encrypt_response(response, aes_key, iv):
    try:
        # Flip the initialization vector
        flipped_iv = bytearray()
        for byte in iv:
            flipped_iv.append(byte ^ 0xFF)

        # Encrypt the response data
        encryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(flipped_iv),
            backend=default_backend()
        ).encryptor()

        encrypted_data = encryptor.update(json.dumps(response).encode("utf-8")) + encryptor.finalize()
        tag = encryptor.tag

        # Combine encrypted data and tag, then encode to base64
        encrypted_response = b64encode(encrypted_data + tag).decode("utf-8")
        print(f'Encrypted Response: {encrypted_response}')
        return encrypted_response
    except Exception as e:
        print(f'Error encrypting response: {e}')
        return None