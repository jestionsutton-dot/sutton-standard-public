import os
import sys
import json
import time
import subprocess
import re

# 1. Patch index.html if witness-chain-container is missing or needs updating
index_path = "index.html"
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    if 'id="witness-chain-container"' not in html:
        old_section = '<h2>Cryptographic Witness Chain (Live Anchor Feed)</h2>'
        new_section = '''<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <h2 style="margin:0;">Cryptographic Witness Chain (Live Anchor Feed)</h2>
                <span id="chain-status-badge" class="metric-badge" style="background:#003311; color:#00ff66; border:1px solid #00ff66;">STREAMING LIVE</span>
            </div>
            <div id="witness-chain-container">
                <div style="color:var(--text-muted); font-size:0.8rem;">Connecting to sovereign ledger...</div>
            </div>'''
        html = html.replace(old_section, new_section)

    script_fix = '''<script>
async function loadLiveWitnessChain() {
    try {
        const response = await fetch('witness_chain.json?v=' + Date.now(), { cache: 'no-store' });
        const data = await response.json();
        const container = document.getElementById('witness-chain-container');
        if (container && data.witness_chain) {
            let html = '';
            data.witness_chain.forEach(item => {
                const isRed = item.event && (item.event.includes('CIRCUIT_BREAKER') || item.event.includes('STRIKE'));
                const borderColor = isRed ? 'var(--accent-red)' : 'var(--accent-green)';
                html += `
                <div style="background:#000; padding:12px; margin-bottom:10px; border-radius:4px; border:1px solid var(--border-color); border-left:3px solid ${borderColor}; font-family:monospace;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:5px;">
                        <span style="color:var(--accent-green); font-weight:bold;">BLOCK #${item.block} // ${item.event}</span>
                        <span class="metric-badge">${item.governor_status}</span>
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-muted); word-break:break-all;">
                        <strong>Hash:</strong> ${item.hash}<br>
                        <strong>Eval ID:</strong> ${item.eval_id}
                    </div>
                </div>`;
            });
            container.innerHTML = html;
            const badge = document.getElementById('chain-status-badge');
            if (badge) badge.innerText = `${data.witness_chain.length} BLOCKS ANCHORED`;
        }
    } catch (e) {
        console.error("Error loading live witness chain:", e);
    }
}
document.addEventListener('DOMContentLoaded', () => {
    loadLiveWitnessChain();
    setInterval(loadLiveWitnessChain, 10000);
});
</script>'''

    html = re.sub(r'<script>[\s\S]*?async function loadLiveWitnessChain[\s\S]*?</script>', script_fix, html)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html DOM and cache-busting script synchronized.")

# 2. Ingest payload if passed as argument
if len(sys.argv) > 1:
    payload_str = sys.argv[1]
    from ingest_aistudio import ingest_entry
    payload = json.loads(payload_str)
    ingest_entry(
        eval_id=payload.get("eval_id"),
        event=payload.get("event"),
        h_coef=payload.get("h_coef", 0.0),
        governor_status=payload.get("governor_status", "x-governor-active"),
        block_hash=payload.get("hash")
    )
    print(f"✅ Ingested telemetry for {payload.get('eval_id')}")

# 3. Synchronize live witness chain manifest
if os.path.exists("update_live_witness.py"):
    os.system("python3 update_live_witness.py")

# 4. Commit and push directly to GitHub Pages
print("🚀 Pushing directly to live clearinghouse at thesuttonstandard.com...")
subprocess.run(["git", "add", "index.html", "vault_registry.db", "witness_chain.json"], check=True)
commit_msg = f"publish(live): stream block to thesuttonstandard.com [{int(time.time())}]"
subprocess.run(["git", "commit", "-m", commit_msg], check=False)
push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

if push_res.returncode == 0:
    print("🔥 SUCCESS! Data pushed directly to GitHub. Live feed updating at https://thesuttonstandard.com")
else:
    print(f"⚠️ Push status: {push_res.stderr}")
