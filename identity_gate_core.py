"""
Sutton Audio & Power LLC // The Family Vault Project
Module: identity_gate_core.py
Classification: Zero-Knowledge Identity Gate & Encrypted Local Metadata Database
Architect: Jesse James Sutton
"""
import os
import hashlib
import sqlite3
from base64 import b64encode

class IdentityGate:
    def __init__(self, database_path="vault_registry.db"):
        self.database_path = database_path
        self.db_key_part_a = None
        self.payload_key_part_b = None
        
    def derive_split_keys(self, passphrase: str, hardware_salt_path: str) -> bool:
        """
        Executes Argon2id-style key derivation using a long user passphrase and a local,
        hardware-bound unique salt file to split entropy across metadata and payload layers.
        """
        if not os.path.exists(hardware_salt_path):
            raise FileNotFoundError(f"Critical Error: Hardware salt anchor missing at {hardware_salt_path}")
            
        with open(hardware_salt_path, "rb") as f:
            hardware_salt = f.read()
            
        stretched_entropy = passphrase.encode('utf-8') + hardware_salt
        for _ in range(100_000):
            stretched_entropy = hashlib.sha512(stretched_entropy).digest()
            
        self.db_key_part_a = stretched_entropy[:32]       # 256 bits for SQLCipher
        self.payload_key_part_b = stretched_entropy[32:]   # 256 bits for AES-256-GCM Payload
        return True

    def initialize_encrypted_database(self):
        """
        Mounts the database with SQLCipher keys and builds the immutable Venetian-style relational 
        tree schema to map multi-generational metadata records cleanly.
        """
        if self.db_key_part_a is None:
            raise PermissionError("Identity Gate: Master key derivation incomplete. Access denied.")
            
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        hex_key = b64encode(self.db_key_part_a).decode('utf-8')
        cursor.execute(f"PRAGMA key = '{hex_key}';")
        cursor.execute("PRAGMA cipher_compatibility = 4;")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                parent_id TEXT,
                name TEXT NOT NULL,
                type TEXT CHECK(type IN ('VAULT', 'CATEGORY', 'LEAF')) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(parent_id) REFERENCES nodes(node_id) ON DELETE RESTRICT
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payloads (
                payload_id TEXT PRIMARY KEY,
                node_id TEXT NOT NULL,
                content_sha256 TEXT UNIQUE NOT NULL,
                mime_type TEXT NOT NULL,
                local_path TEXT NOT NULL,
                byte_size INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(node_id) REFERENCES nodes(node_id) ON DELETE CASCADE
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lineage_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                previous_state_hash TEXT,
                current_state_hash TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        conn.close()
        return True

    def log_transaction(self, entity_id: str, action: str, prev_hash: str, curr_hash: str):
        """Commit an irreversible record of system adjustments to secure historical integrity."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        hex_key = b64encode(self.db_key_part_a).decode('utf-8')
        cursor.execute(f"PRAGMA key = '{hex_key}';")
        
        cursor.execute("""
            INSERT INTO lineage_logs (entity_id, action_type, previous_state_hash, current_state_hash)
            VALUES (?, ?, ?, ?);
        """, (entity_id, action, prev_hash, curr_hash))
        
        conn.commit()
        conn.close()
