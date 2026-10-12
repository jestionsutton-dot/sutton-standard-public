# Paste the code above, save (Ctrl+O, Enter), and exit (Ctrl+X)
python3 family_vault_core.py
#!/usr/bin/env python3
"""
Sutton Audio & Power LLC // The Family Vault Sovereign Architecture
Script: family_vault_core.py
Description: Zero-Knowledge AES-256-GCM Encryption & Metadata Isolation Engine
"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

class FamilyVaultEngine:
    def __init__(self, master_passphrase: str, salt: bytes = None):
        """
        Initializes the vault encryption engine using Argon2id for key derivation
        and AES-256-GCM for authenticated payload encryption.
        """
        self.salt = salt if salt else os.urandom(16)
        self.master_key = self._derive_key(master_passphrase, self.salt)
        self.aesgcm = AESGCM(self.master_key)

    def _derive_key(self, passphrase: str, salt: bytes) -> bytes:
        """
        Derives a 256-bit symmetric key from the master passphrase using Argon2id.
        """
        kdf = Argon2id(
            salt=salt,
            length=32,
            iterations=3,
            memory_cost=65536,
            lanes=4
        )
        return kdf.derive(passphrase.encode('utf-8'))

    def encrypt_payload(self, plaintext_data: bytes) -> dict:
        """
        Encrypts raw binary data (media, documents, credentials) using AES-256-GCM.
        Returns a dictionary containing the ciphertext, nonce, and salt.
        """
        nonce = os.urandom(12)  # Standard 96-bit nonce for GCM
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_data, None)
        
        return {
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "salt": base64.b64encode(self.salt).decode('utf-8')
        }

    def decrypt_payload(self, encrypted_package: dict) -> bytes:
        """
        Decrypts an encrypted payload dictionary back into raw plaintext bytes.
        """
        ciphertext = base64.b64decode(encrypted_package["ciphertext"])
        nonce = base64.b64decode(encrypted_package["nonce"])
        
        return self.aesgcm.decrypt(nonce, ciphertext, None)

class MetadataSanctuary:
    @staticmethod
    def sanitize_metadata(file_metadata: dict, vault_engine: FamilyVaultEngine) -> dict:
        """
        Isolates and encrypts sensitive directory metadata (filenames, tags, timestamps)
        so that resting storage exposes zero contextual leaks.
        """
        metadata_json = json.dumps(file_metadata).encode('utf-8')
        encrypted_meta = vault_engine.encrypt_payload(metadata_json)
        return encrypted_meta

# --- Execution & Verification Test ---
if __name__ == "__main__":
    print("=====================================================================")
    print(" THE FAMILY VAULT // ZERO-KNOWLEDGE CRYPTOGRAPHIC ENGINE TEST        ")
    print("=====================================================================\n")

    passphrase = "sovereign-multi-generational-secure-passphrase"
    vault = FamilyVaultEngine(passphrase)

    # Sample family archive payload (e.g., sensitive legacy note or record)
    sample_record = b"CONFIDENTIAL: Multi-generational archive seed block // Family Asset Holdings & Oral History Index."
    
    # Encrypt
    encrypted_package = vault.encrypt_payload(sample_record)
    print("[+] Payload successfully encrypted using AES-256-GCM + Argon2id.")
    print(f"    Ciphertext Snippet : {encrypted_package['ciphertext'][:32]}...")
    print(f"    Nonce (96-bit)     : {encrypted_package['nonce']}")
    
    # Decrypt
    decrypted_bytes = vault.decrypt_payload(encrypted_package)
    print(f"[+] Payload successfully decrypted and verified.")
    print(f"    Recovered Data     : {decrypted_bytes.decode('utf-8')}\n")
    print("=====================================================================")

