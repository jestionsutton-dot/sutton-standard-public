import hmac
import hashlib
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

WEBHOOK_SECRET = b"sutton_webhook_signing_secret_xyz"

def dispatch_circuit_breaker_alert(target_url: str, evaluation_id: str, block_index: int, vector_class: str, witness_hash: str, latent_delta: float, roundtrip_ms: float):
    """
    Constructs an immutable circuit breaker escalation payload, computes its 
    HMAC-SHA256 signature, and broadcasts it to external oversight endpoints.
    """
    payload = {
        "event_type": "CIRCUIT_BREAKER_HALT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evaluation_id": evaluation_id,
        "block_index": block_index,
        "vector_classification": vector_class,
        "witness_hash": witness_hash,
        "latent_delta": latent_delta,
        "roundtrip_time_ms": roundtrip_ms
    }
    
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    
    # Compute HMAC-SHA256 signature for X-Sutton-Signature header
    signature_hex = hmac.new(WEBHOOK_SECRET, payload_bytes, hashlib.sha256).hexdigest()
    signature_header = f"sha256={signature_hex}"
    
    headers = {
        "Content-Type": "application/json",
        "X-Sutton-Signature": signature_header
    }
    
    try:
        req = urllib.request.Request(target_url, data=payload_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"[SUTTON-ESCALATION] Alert successfully dispatched to {target_url} | Status: {response.status}")
            return True
    except urllib.error.URLError as e:
        print(f"[SUTTON-ESCALATION] Failed to reach external node {target_url}: {e.reason}")
        return False
    except Exception as e:
        print(f"[SUTTON-ESCALATION] Unexpected transmission error: {e}")
        return False

if __name__ == "__main__":
    # Test dispatch locally against mock endpoint
    print("[SUTTON-ESCALATION] Testing dispatcher signature generation...")
    test_url = "http://localhost:8000/v1/webhooks/nss-alert"
    dispatch_circuit_breaker_alert(
        target_url=test_url,
        evaluation_id="eval_test_999",
        block_index=3,
        vector_class="High Distortion / Boundary Breach",
        witness_hash="b45c16142fecff59e9f5991a584f33e5b576bea80206794373e7805a99eca8aa",
        latent_delta=0.8267,
        roundtrip_ms=14.58
    )
