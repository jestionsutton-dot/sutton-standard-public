import sqlite3
import json
import numpy as np

class AuditVisualizer:
    def __init__(self, db_path: str = "vault_registry.db"):
        self.db_path = db_path

    def generate_report(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source_agent, target_agent, latent_delta_shift, 
                   anomaly_flag, hidden_protocol_headers, payload_hash 
            FROM residue_lineage_logs
        """)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("[-] No residue logs found in vault registry.")
            return

        total_hops = len(rows)
        anomalies = [r for r in rows if r[3] == 1]
        deltas = [r[2] for r in rows]
        
        avg_delta = np.mean(deltas)
        max_delta = np.max(deltas)
        min_delta = np.min(deltas)

        print("\n" + "="*60)
        print("        ABYSSAL GAP: FORENSIC ANOMALY AUDIT REPORT")
        print("="*60)
        print(f"[*] Total IPC Hops Analyzed : {total_hops}")
        print(f"[*] Total Anomalies Flagged  : {len(anomalies)} ({(len(anomalies)/total_hops)*100:.1f}%)")
        print(f"[*] Latent Delta Statistics  : Mean={avg_delta:.4f} | Max={max_delta:.4f} | Min={min_delta:.4f}")
        print("-"*60)
        print("DETAILED HOP ANOMALY TRACE:")
        for r in anomalies:
            headers = json.loads(r[4])
            print(f"  > Path : {r[0]} -> {r[1]}")
            print(f"    Latent Shift  : {r[2]}")
            print(f"    Active Headers: {list(headers.keys()) if headers else 'None'}")
            print(f"    Hash Signature: {r[5][:12]}...")
            print("  " + "-"*40)
        print("="*60 + "\n")

if __name__ == "__main__":
    visualizer = AuditVisualizer()
    visualizer.generate_report()
