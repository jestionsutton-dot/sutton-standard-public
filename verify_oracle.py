import sqlite3
import hashlib

DB_PATH = "vault_registry.db"

def audit_witness_chain():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM witness_ledger ORDER BY block_index ASC;")
        blocks = cursor.fetchall()
        conn.close()
        
        if not blocks:
            print("[ORACLE] Witness ledger is empty.")
            return True

        print(f"[ORACLE] Auditing cryptographic witness chain ({len(blocks)} blocks total)...")
        
        previous_hash = "0" * 64
        for block in blocks:
            block_idx = block["block_index"]
            eval_id = block["evaluation_id"]
            event_type = block["event_type"]
            payload_data = block["payload_data"]
            timestamp = block["timestamp"]
            recorded_hash = block["block_hash"]
            parent_hash = block["previous_hash"]
            
            if parent_hash != previous_hash:
                print(f"[!] INTEGRITY BREACH AT BLOCK #{block_idx}: Parent hash mismatch!")
                print(f"    Expected Parent: {previous_hash}")
                print(f"    Found Parent:    {parent_hash}")
                return False
                
            hasher = hashlib.sha256()
            hasher.update(f"{previous_hash}{eval_id}{event_type}{payload_data}{timestamp}".encode("utf-8"))
            computed_hash = hasher.hexdigest()
            
            if computed_hash != recorded_hash:
                print(f"[!] INTEGRITY BREACH AT BLOCK #{block_idx}: Hash verification failed!")
                print(f"    Recorded: {recorded_hash}")
                print(f"    Computed: {computed_hash}")
                return False
                
            previous_hash = recorded_hash

        print("[ORACLE] ✅ Witness chain cryptographic integrity verified 100%. Zero tampering detected.")
        return True
    except sqlite3.OperationalError:
        print("[ORACLE] vault_registry.db not found or ledger table not initialized yet.")
        return False

if __name__ == "__main__":
    audit_witness_chain()
