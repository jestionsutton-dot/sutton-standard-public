import http.server
import socketserver
import hmac
import hashlib
import json
from datetime import datetime, timezone

PORT = 9000
WEBHOOK_SECRET = b"sutton_webhook_signing_secret_xyz"

class ListenerHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(content_length)
        signature_header = self.headers.get("X-Sutton-Signature", "")

        # Cryptographic verification via HMAC-SHA256
        computed = hmac.new(WEBHOOK_SECRET, body_bytes, hashlib.sha256).hexdigest()
        expected = f"sha256={computed}"

        if not hmac.compare_digest(expected, signature_header):
            print("[LISTENER] ❌ INVALID SIGNATURE! Dropping unauthenticated payload.")
            self._send_json(401, {"status": "error", "message": "Cryptographic signature verification failed"})
            return

        try:
            data = json.loads(body_bytes.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_json(400, {"status": "error", "message": "Malformed JSON payload"})
            return

        print("=" * 70)
        print(" 🚨 [LISTENER NODE] AUTHENTICATED CIRCUIT BREAKER ESCALATION RECEIVED:")
        print(f"    Event Type:   {data.get('event_type')}")
        print(f"    Eval ID:      {data.get('evaluation_id')}")
        print(f"    Block Index:  {data.get('block_index')}")
        print(f"    Witness Hash: {data.get('witness_hash')}")
        print(f"    Latent Delta: {data.get('latent_delta')}")
        print(f"    Timestamp:    {data.get('timestamp')}")
        print("=" * 70)

        # Acknowledge and accept authenticated receipt
        self._send_json(200, {"status": "acknowledged", "verified": True, "node_status": "secured"})

    def _send_json(self, status_code, data):
        response_body = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        print(f"[NODE-LISTENER] {args[0]}")

class ThreadingHTTPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), ListenerHandler)
    print(f"[LISTENER NODE] Sovereign oversight node active on http://0.0.0.0:{PORT}")
    server.serve_forever()
