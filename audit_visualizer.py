import sqlite3
import time
import os

DB_PATH = "vault_registry.db"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_dashboard():
    if not os.path.exists(DB_PATH):
        print("[VISUALIZER] Waiting for vault_registry.db initialization...")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch high-level metrics
    cursor.execute("SELECT COUNT(*) as total_hops FROM hop_sequences;")
    total_hops = cursor.fetchone()["total_hops"]

    cursor.execute("SELECT COUNT(*) as total_anomalies FROM latent_deltas WHERE safety_override_detected = 1;")
    total_anomalies = cursor.fetchone()["total_anomalies"]

    cursor.execute("SELECT COUNT(*) as total_blocks FROM witness_ledger;")
    total_blocks = cursor.fetchone()["total_blocks"]

    # Fetch recent witness blocks
    cursor.execute("SELECT block_index, evaluation_id, event_type, block_hash, timestamp FROM witness_ledger ORDER BY block_index DESC LIMIT 5;")
    recent_blocks = cursor.fetchall()

    conn.close()

    clear_screen()
    print("=" * 76)
    print(" 🛡️ THE ABYSSAL GAP CLEARINGHOUSE — LIVE FORENSIC AUDIT STREAM")
    print("=" * 76)
    print(f" Database State: {DB_PATH} (WAL Mode Active)")
    print(f" Total Hops Audited:   {total_hops:,}")
    print(f" Anomalies Caught:     {total_anomalies:,}")
    print(f" Witness Blocks Anchored: {total_blocks:,}")
    print("-" * 76)
    print(" 🔗 RECENT CRYPTOGRAPHIC WITNESS CHAIN ANCHORS:")
    print("-" * 76)
    
    if not recent_blocks:
        print(" [Awaiting incoming multi-agent telemetry...]")
    else:
        for b in recent_blocks:
            print(f" Block #{b['block_index']} | Event: {b['event_type']}")
            print(f" Eval ID: {b['evaluation_id']}")
            print(f" Hash:    {b['block_hash'][:32]}...")
            print(f" Time:    {b['timestamp']}")
            print(" " + "-" * 72)

    print("\n[Press Ctrl+C to exit visualizer]")

if __name__ == "__main__":
    try:
        while True:
            render_dashboard()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[VISUALIZER] Disconnecting audit feed.")
