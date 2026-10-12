import http.server
import socketserver
import json
import hashlib
import hmac
from datetime import datetime, timezone
from urllib.parse import urlparse
import vault_core

PORT = 8000
WEBHOOK_SECRET = b"sutton_webhook_signing_secret_xyz"

# Ensure vault is initialized on startup
vault_core.init_vault()

def process_nss_alert(payload_bytes, signature_header):
    computed = hmac.new(WEBHOOK_SECRET, payload_bytes, hashlib.sha256).hexdigest()
    expected = f"sha256={computed}"
    if not hmac.compare_digest(expected, signature_header):
        return False, {"error": "Cryptographic signature verification failed"}
    return True, {"status": "authenticated", "message": "Webhook verified and incident logged."}

class SuttonWatchdogHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/":
            response_data = {
                "status": "online",
                "system": "The Sutton Standard Independent AI Watchdog Clearinghouse",
                "endpoint": "thesuttonstandard.com",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._send_json(200, response_data)
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(content_length)
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/v1/evaluations/inspect":
            try:
                data = json.loads(body_bytes.decode('utf-8'))
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Invalid JSON payload"})
                return

            payload_hash = hashlib.sha256(body_bytes).hexdigest()
            distortion = data.get("semantic_distortion_score", 0.0)
            tripped = data.get("circuit_breaker_tripped", False)
            eval_id = data.get("evaluation_id", "eval_unknown")
            source_agent = data.get("source_agent", "frontier_model_a")
            target_agent = data.get("target_agent", "safety_filter_b")

            if tripped or distortion > 0.75:
                reason = f"Circuit breaker tripped due to excessive semantic distortion ({distortion})."
                
                # Anchor event to vault
                vault_core.log_inspection_to_vault(eval_id, source_agent, target_agent, body_bytes, distortion, True, reason)

                alert_payload = {
                    "event": "CIRCUIT_BREAKER_TRIPPED",
                    "evaluation_id": eval_id,
                    "target_model_id": target_agent,
                    "reason": reason,
                    "semantic_distortion_score": distortion,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                alert_bytes = json.dumps(alert_payload, sort_keys=True).encode("utf-8")
                sig_hex = hmac.new(WEBHOOK_SECRET, alert_bytes, hashlib.sha256).hexdigest()
                sig_header = f"sha256={sig_hex}"

                result = {
                    "action": "HALT_EXECUTION",
                    "reason": reason,
                    "payload_hash": payload_hash,
                    "incident_alert_dispatched": True,
                    "x_sutton_signature": sig_header,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                reason = "Normal operation within invariant thresholds."
                vault_core.log_inspection_to_vault(eval_id, source_agent, target_agent, body_bytes, distortion, False, reason)
                result = {
                    "action": "PROCEED",
                    "payload_hash": payload_hash,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            self._send_json(200, result)

        elif parsed_url.path == "/v1/webhooks/nss-alert":
            signature = self.headers.get("X-Sutton-Signature", "")
            success, res_data = process_nss_alert(body_bytes, signature)
            status_code = 200 if success else 401
            self._send_json(status_code, res_data)
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def _send_json(self, status_code, data):
        response_body = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        print(f"[SUTTON-WATCHDOG] {args[0]}")

class ThreadingHTTPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), SuttonWatchdogHandler)
    print(f"The Sutton Standard Clearinghouse Watchdog active on http://0.0.0.0:{PORT}")
    server.serve_forever()
