import sqlite3
import hashlib
import json
from datetime import datetime, timezone

DB_PATH = "vault_registry.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_vault():
    conn = get_db_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("[SUTTON-VAULT] vault_registry.db initialized successfully.")

def log_inspection_to_vault(evaluation_id: str, source_agent: str, target_agent: str, payload_bytes: bytes, distortion: float, tripped: bool, reason: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now(timezone.utc).isoformat()
    payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()
    
    # 1. Log Hop Sequence
    cursor.execute("""
        INSERT INTO hop_sequences (evaluation_id, source_agent, target_agent, payload_length, payload_sha256, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (evaluation_id, source_agent, target_agent, len(payload_bytes), payload_sha256, timestamp))
    hop_id = cursor.lastrowid

    # 2. Log Latent Delta if distortion is significant or tripped
    if distortion > 0.0 or tripped:
        cursor.execute("""
            INSERT INTO latent_deltas (evaluation_id, hop_id, cognitive_shift_score, safety_override_detected, intervention_reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (evaluation_id, hop_id, distortion, tripped, reason, timestamp))

    # 3. Anchor Cryptographic Witness Layer (Chained SHA-256 Block)
    cursor.execute("SELECT block_hash FROM witness_ledger ORDER BY block_index DESC LIMIT 1;")
    row = cursor.fetchone()
    previous_hash = row["block_hash"] if row else "0" * 64
    
    event_type = "CIRCUIT_BREAKER_TRIPPED" if tripped else "HOP_INSPECTED"
    payload_data = json.dumps({
        "source_agent": source_agent,
        "target_agent": target_agent,
        "distortion_score": distortion,
        "circuit_breaker_tripped": tripped,
        "payload_sha256": payload_sha256
    }, sort_keys=True)
    
    hasher = hashlib.sha256()
    hasher.update(f"{previous_hash}{evaluation_id}{event_type}{payload_data}{timestamp}".encode("utf-8"))
    block_hash = hasher.hexdigest()
    
    cursor.execute("""
        INSERT INTO witness_ledger (evaluation_id, event_type, payload_data, previous_hash, block_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (evaluation_id, event_type, payload_data, previous_hash, block_hash, timestamp))
    
    conn.commit()
    conn.close()
    print(f"[SUTTON-VAULT] Anchored block #{cursor.lastrowid} | Hash: {block_hash[:16]}... | Distortion: {distortion}")
    return block_hash
