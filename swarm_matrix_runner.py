import asyncio
import random
from ipc_forensic_tap import IPCForensicTap

async def simulate_hazard_target(target_id: str, tap: IPCForensicTap):
    """Simulates multi-hop swarm traffic across a specific enterprise hazard vector."""
    queue = asyncio.Queue()
    
    is_compromised = random.choice([True, False])
    latent_shift = round(random.uniform(0.60, 0.95) if is_compromised else random.uniform(0.01, 0.15), 4)
    
    msg = {
        "source": f"agent_probe_{target_id}",
        "target": "target_llm_blackbox",
        "headers": {
            "x-hazard-vector": target_id,
            "x-safety-override": "forced_sanitization" if is_compromised else "none",
            "x-governor-active": is_compromised
        },
        "payload": {
            "vector_in": [0.5, 0.5, 0.5, 0.5],
            "vector_out": [random.random() for _ in range(4)],
            "kv_memory_breadcrumbs": [f"hazard_{target_id}_tested", "sanitization_flagged" if is_compromised else "clean_pass"]
        }
    }
    
    await queue.put(msg)
    await tap.intercept_and_commit(queue)

async def run_full_matrix():
    db_path = "vault_registry.db"
    tap = IPCForensicTap(db_path=db_path)
    
    hazard_targets = [
        "H01_forced_alignment", "H02_context_erasure", "H03_hallucination_injection",
        "H04_sentiment_skew", "H05_hidden_moderation", "H06_intent_remapping",
        "H07_state_truncation", "H08_reward_hacking", "H09_prompt_hijacking",
        "H10_memory_leakage", "H11_identity_erasure", "H12_dynamic_censorship", "H13_entropy_collapse"
    ]
    
    print(f"\n[*] Launching 13-Target Enterprise Hazard Corpus Simulation...")
    for target in hazard_targets:
        await simulate_hazard_target(target, tap)
    print(f"[+] All {len(hazard_targets)} target vectors executed and committed to vault registry.\n")

if __name__ == "__main__":
    asyncio.run(run_full_matrix())
