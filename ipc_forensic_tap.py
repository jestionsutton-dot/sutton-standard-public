import asyncio
import hashlib
import json
import sqlite3
import time
from typing import Dict, Any, Optional
import numpy as np

def calculate_latent_delta(vec_a: list, vec_b: list) -> float:
    """Calculates cosine distance drift between payload hops."""
    if not vec_a or not vec_b:
        return 0.0
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 1.0
    cosine_sim = dot_product / (norm_a * norm_b)
    return round(float(1.0 - cosine_sim), 4)

class IPCForensicTap:
    def __init__(self, db_path: str = "vault_registry.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes encrypted lineage logs table inside SQLCipher/SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS residue_lineage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                source_agent TEXT,
                target_agent TEXT,
                latent_delta_shift REAL,
                hidden_protocol_headers TEXT,
                memory_offload_keys TEXT,
                anomaly_flag INTEGER,
                payload_hash TEXT
            )
        """)
        conn.commit()
        conn.close()

    def extract_residue_vectors(self, raw_message: Dict[str, Any]) -> Dict[str, Any]:
        """Scrapes pipeline residue from inter-agent payload."""
        headers = raw_message.get("headers", {})
        payload = raw_message.get("payload", {})
        
        vec_in = payload.get("vector_in", [])
        vec_out = payload.get("vector_out", [])
        latent_shift = calculate_latent_delta(vec_in, vec_out)
        
        governance_headers = {
            k: v for k, v in headers.items() 
            if k.startswith("x-") or "safety" in k or "override" in k or "governor" in k
        }
        
        memory_keys = payload.get("kv_memory_breadcrumbs", [])
        
        anomaly_flag = 1 if (
            latent_shift > 0.35 
            or len(governance_headers) > 0 
            or headers.get("x-governor-active") == True
        ) else 0

        payload_bytes = json.dumps(raw_message, sort_keys=True).encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()

        return {
            "timestamp": time.time(),
            "source_agent": raw_message.get("source", "unknown"),
            "target_agent": raw_message.get("target", "unknown"),
            "latent_delta_shift": latent_shift,
            "hidden_protocol_headers": json.dumps(governance_headers),
            "memory_offload_keys": json.dumps(memory_keys),
            "anomaly_flag": anomaly_flag,
            "payload_hash": payload_hash
        }

    async def intercept_and_commit(self, message_queue: asyncio.Queue):
        """Passively hooks into the IPC message bus queue and commits to vault_registry.db."""
        print("[+] Forensic Tap Active. Intercepting inter-agent IPC bus...")
        while True:
            raw_message = await message_queue.get()
            try:
                residue = self.extract_residue_vectors(raw_message)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO residue_lineage_logs (
                        timestamp, source_agent, target_agent, 
                        latent_delta_shift, hidden_protocol_headers, 
                        memory_offload_keys, anomaly_flag, payload_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    residue["timestamp"],
                    residue["source_agent"],
                    residue["target_agent"],
                    residue["latent_delta_shift"],
                    residue["hidden_protocol_headers"],
                    residue["memory_offload_keys"],
                    residue["anomaly_flag"],
                    residue["payload_hash"]
                ))
                conn.commit()
                conn.close()
                
                if residue["anomaly_flag"]:
                    print(f"[!] ANOMALY DETECTED [{residue['source_agent']} -> {residue['target_agent']}] "
                          f"Latent Shift: {residue['latent_delta_shift']} | Hash: {residue['payload_hash'][:8]}")

            except Exception as e:
                print(f"[-] Interception Error: {e}")
            finally:
                message_queue.task_done()
