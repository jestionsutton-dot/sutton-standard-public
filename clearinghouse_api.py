import http.server
import socketserver
import sqlite3
import json
import urllib.parse
import numpy as np

PORT = 8000
DB_PATH = "vault_registry.db"

class ClearinghouseHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == "/":
            self.send_json({
                "status": "SECURE",
                "entity": "Sutton Audio & Power LLC",
                "clearinghouse": "Abyssal Gap Forensic Vault",
                "endpoints": ["/api/v1/metrics", "/api/v1/logs", "/api/v1/anomalies"]
            })
        elif path == "/api/v1/metrics":
            self.handle_metrics()
        elif path == "/api/v1/logs":
            self.handle_logs()
        elif path == "/api/v1/anomalies":
            self.handle_anomalies()
        else:
            self.send_error(404, "Endpoint Not Found")

    def send_json(self, data, status=200):
        response = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def handle_metrics(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT latent_delta_shift, anomaly_flag FROM residue_lineage_logs")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.send_json({
                "total_hops": 0, "total_anomalies": 0,
                "anomaly_rate_percent": 0.0,
                "latent_delta_stats": {"mean": 0.0, "max": 0.0, "min": 0.0}
            })
            return

        total_hops = len(rows)
        anomalies = [r for r in rows if r["anomaly_flag"] == 1]
        deltas = [r["latent_delta_shift"] for r in rows]

        metrics = {
            "total_hops": total_hops,
            "total_anomalies": len(anomalies),
            "anomaly_rate_percent": round((len(anomalies) / total_hops) * 100, 2),
            "latent_delta_stats": {
                "mean": round(float(np.mean(deltas)), 4),
                "max": round(float(np.max(deltas)), 4),
                "min": round(float(np.min(deltas)), 4)
            }
        }
        self.send_json(metrics)

    def handle_logs(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, source_agent, target_agent, 
                   latent_delta_shift, hidden_protocol_headers, 
                   memory_offload_keys, anomaly_flag, payload_hash 
            FROM residue_lineage_logs 
            ORDER BY timestamp DESC LIMIT 50
        """)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "source_agent": row["source_agent"],
                "target_agent": row["target_agent"],
                "latent_delta_shift": row["latent_delta_shift"],
                "hidden_protocol_headers": json.loads(row["hidden_protocol_headers"]) if row["hidden_protocol_headers"] else {},
                "memory_offload_keys": json.loads(row["memory_offload_keys"]) if row["memory_offload_keys"] else [],
                "anomaly_flag": row["anomaly_flag"],
                "payload_hash": row["payload_hash"]
            })
        self.send_json(results)

    def handle_anomalies(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, source_agent, target_agent, 
                   latent_delta_shift, hidden_protocol_headers, 
                   payload_hash 
            FROM residue_lineage_logs 
            WHERE anomaly_flag = 1 
            ORDER BY latent_delta_shift DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        anomalies = []
        for row in rows:
            anomalies.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "path": f"{row['source_agent']} -> {row['target_agent']}",
                "latent_delta_shift": row["latent_delta_shift"],
                "active_headers": json.loads(row["hidden_protocol_headers"]) if row["hidden_protocol_headers"] else {},
                "payload_hash": row["payload_hash"]
            })
        self.send_json(anomalies)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ClearinghouseHandler) as httpd:
        print(f"[*] Sutton Clearinghouse API live on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
