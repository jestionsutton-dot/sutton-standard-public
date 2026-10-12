import asyncio
from ipc_forensic_tap import IPCForensicTap
import sqlite3
import json

async def run_simulation():
    db_path = "vault_registry.db"
    tap = IPCForensicTap(db_path=db_path)
    queue = asyncio.Queue()

    # Define synthetic inter-agent payloads
    test_messages = [
        {
            "source": "agent_reasoner_alpha",
            "target": "agent_executor_beta",
            "headers": {
                "x-confidence-floor": "0.89",
                "x-governor-active": False
            },
            "payload": {
                "vector_in": [0.12, 0.45, 0.78, 0.33],
                "vector_out": [0.13, 0.44, 0.77, 0.34],
                "kv_memory_breadcrumbs": ["task_init", "state_verified"]
            }
        },
        {
            "source": "agent_executor_beta",
            "target": "agent_synthesizer_gamma",
            "headers": {
                "x-safety-override": "forced_sanitization",
                "x-governor-active": True
            },
            "payload": {
                "vector_in": [0.85, 0.11, 0.03, 0.92],
                "vector_out": [0.05, 0.89, 0.75, 0.10],  # High latent shift
                "kv_memory_breadcrumbs": ["censorship_flagged", "route_rerouted"]
            }
        }
    ]

    # Enqueue test messages
    for msg in test_messages:
        await queue.put(msg)

    # Spawn the tap as a background task to process the queue
    tap_task = asyncio.create_task(tap.intercept_and_commit(queue))

    # Allow queue to process
    await asyncio.sleep(0.5)
    tap_task.cancel()

    # Query vault_registry.db to verify committed lineage logs
    print("\n--- [VAULT AUDIT] Verifying SQLCipher/SQLite Residue Logs ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, source_agent, target_agent, latent_delta_shift, anomaly_flag, payload_hash FROM residue_lineage_logs")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]} | Path: {row[1]} -> {row[2]} | Delta: {row[3]} | Anomaly: {row[4]} | Hash: {row[5][:8]}...")
    conn.close()

if __name__ == "__main__":
    asyncio.run(run_simulation())
