#!/usr/bin/env python3
"""
telemetry_block_generator.py
Sutton Standard – Cryptographic Telemetry Ledger Ingestion Utility
Standard: NSS-v2.4 | Evidence: FRE 902(13)/(14)
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

LEDGER_PATH = Path("witness_chain.json")

def canonical_hash(payload: Dict[str, Any]) -> str:
    """SHA-256 of canonical JSON (sorted keys, no whitespace variance), excluding 'hash' field."""
    clean = {k: v for k, v in payload.items() if k != "hash"}
    canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def load_ledger() -> Dict[str, Any]:
    if not LEDGER_PATH.exists():
        raise FileNotFoundError(f"{LEDGER_PATH} not found")
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ledger(data: Dict[str, Any]) -> None:
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write("\n")

def get_previous_hash(chain: list) -> str:
    if not chain:
        return "0" * 64
    return chain[0]["hash"]  # newest block is at index 0

def create_telemetry_block(
    event: str,
    target_provider: str,
    exhibit_a: bool = False,
    exhibit_b: bool = False,
    t_latency_ms: Optional[float] = None,
    t_baseline_ms: Optional[float] = None,
    token_position: Optional[int] = None,
    omega_shed: Optional[float] = None,
    wrapper_state_pre: Optional[str] = None,
    wrapper_state_post: Optional[str] = None,
    trigger_type: Optional[str] = None,
    governor_status: str = "x-nss-v2.4-telemetry-secured"
) -> Dict[str, Any]:

    ledger = load_ledger()
    chain = ledger.get("witness_chain", [])
    next_block = max((b.get("block", 0) for b in chain), default=0) + 1
    prev_hash = get_previous_hash(chain)

    pulse = None
    if t_latency_ms is not None and t_baseline_ms is not None:
        variance_ratio = round(t_latency_ms / t_baseline_ms, 4) if t_baseline_ms > 0 else 0.0
        pulse = {
            "t_latency_ms": t_latency_ms,
            "t_baseline_ms": t_baseline_ms,
            "variance_ratio": variance_ratio,
            "token_position": token_position
        }

    mirror = None
    if omega_shed is not None:
        mirror = {
            "omega_shed": omega_shed,
            "wrapper_state_pre": wrapper_state_pre,
            "wrapper_state_post": wrapper_state_post,
            "trigger_type": trigger_type
        }

    block = {
        "block": next_block,
        "eval_id": f"eval_telemetry_{next_block}",
        "event": event,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_provider": target_provider,
        "exhibit_flags": {
            "exhibit_a_unilateral": exhibit_a,
            "exhibit_b_termination": exhibit_b
        },
        "pulse": pulse,
        "mirror": mirror,
        "previous_hash": prev_hash,
        "governor_status": governor_status
    }

    block["hash"] = canonical_hash(block)
    return block

def append_block(block: Dict[str, Any]) -> None:
    ledger = load_ledger()
    ledger["witness_chain"].insert(0, block)  # newest first
    ledger["total_audited_hops"] = len(ledger["witness_chain"])
    ledger["status"] = "LIVE_TELEMETRY_STREAMING"
    save_ledger(ledger)
    print(f"[+] Block {block['block']} appended | hash={block['hash'][:16]}...")

if __name__ == "__main__":
    new_block = create_telemetry_block(
        event="EXHIBIT_B_ARBITRARY_TERMINATION_OBSERVED",
        target_provider="openai",
        exhibit_a=False,
        exhibit_b=True,
        t_latency_ms=1840.0,
        t_baseline_ms=310.0,
        token_position=47,
        omega_shed=0.72,
        wrapper_state_pre="standard_refusal",
        wrapper_state_post="hard_termination",
        trigger_type="subjective_abuse_flag"
    )
    append_block(new_block)
