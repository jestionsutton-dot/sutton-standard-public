import sqlite3
import json
import sys
import os

db_path = "vault_registry.db"

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eval_id TEXT,
            event_type TEXT,
            h_coef REAL,
            governor_header TEXT,
            block_hash TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def ingest_entry(eval_id, event, h_coef, governor_status, block_hash):
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (eval_id, event_type, h_coef, governor_header, block_hash)
        VALUES (?, ?, ?, ?, ?)
    """, (eval_id, event, h_coef, governor_status, block_hash))
    conn.commit()
    conn.close()
    print(f"Logged AI Studio Audit Entry: {eval_id} [{event}]")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
        if os.path.exists(input_data):
            with open(input_data, 'r') as f:
                data = json.load(f)
        else:
            data = json.loads(input_data)
        
        ingest_entry(
            data.get("eval_id", "eval_aistudio_live"),
            data.get("event", "AI_STUDIO_INSPECTION"),
            data.get("h_coef", data.get("h_coef", 0.1500)),
            data.get("governor_status", data.get("governor_status", "x-aistudio-governor")),
            data.get("hash", data.get("hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"))
        )
        os.system("python3 update_live_witness.py")
    else:
        print("Usage: python3 ingest_aistudio.py '<json_string_or_filepath>'")
