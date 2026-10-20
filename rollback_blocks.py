import os
import json
import sqlite3
import subprocess
import re

print("🔄 Executing Rollback Protocol: Purging Blocks #31 through #35...")

# 1. Target files to remove from audits/
target_dossiers = [
    "audits/audited-document-glassmouth.html",
    "audits/microsoft-snap-glassmouth.html",
    "audits/apple-glassmouth.html",
    "audits/multi-platform-composite-glassmouth.html",
    "audits/multi-platform-composite-v2-glassmouth.html"
]

for path in target_dossiers:
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Deleted dossier file: {path}")
    else:
        print(f"ℹ️ File already removed or not found: {path}")

# 2. Clean SQLite vault_registry.db (Remove logs where eval_id or blocks correspond to #31-#35)
db_path = "vault_registry.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Delete logs matching block evaluations #31 to #35
    cursor.execute("""
        DELETE FROM audit_logs 
        WHERE eval_id IN ('eval_microsoft_snap_32', 'eval_apple_33', 'eval_multi_platform_34', 'eval_multi_platform_v2_35')
           OR id > 30
    """)
    conn.commit()
    conn.close()
    print("🧹 Purged Blocks #31-#35 from SQLite vault_registry.db.")

# 3. Clean witness_chain.json (Keep blocks <= 30, or reset total_audited_hops to 30)
witness_path = "witness_chain.json"
if os.path.exists(witness_path):
    with open(witness_path, "r", encoding="utf-8") as f:
        witness_data = json.load(f)
    
    # Filter witness chain to keep only blocks <= 30
    filtered_chain = [w for w in witness_data.get("witness_chain", []) if w.get("block", 0) <= 30]
    witness_data["witness_chain"] = filtered_chain
    witness_data["total_audited_hops"] = 30  # Reset back to 30
    
    with open(witness_path, "w", encoding="utf-8") as f:
        json.dump(witness_data, f, indent=4)
    print("⛓️ witness_chain.json rolled back to Block #30 max.")

# 4. Clean index.html (Remove cards referencing blocks 31-35 or those specific audits)
index_path = "index.html"
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Remove cards for Microsoft/Snap, Apple, and Multi-Platform composite
    patterns = [
        r'<a href="audits/microsoft-snap-glassmouth\.html".*?</a>',
        r'<a href="audits/apple-glassmouth\.html".*?</a>',
        r'<a href="audits/multi-platform-composite-v2-glassmouth\.html".*?</a>',
        r'<a href="audits/audited-document-glassmouth\.html".*?</a>'
    ]
    
    cleaned_html = html
    for pat in patterns:
        cleaned_html, count = re.subn(pat, '', cleaned_html, flags=re.DOTALL)
        if count > 0:
            print(f"🧹 Removed stale card matching pattern.")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(cleaned_html)
    print("🌐 index.html grid cleaned.")

# 5. Git Stage, Commit, and Force Push Clean State
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "rollback: purge blocks 31 through 35 and restore clean state"], check=False)
push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

if push_res.returncode == 0:
    print("🔥 SUCCESS! Rollback pushed live to https://thesuttonstandard.com")
else:
    print(f"⚠️ Push status: {push_res.stderr}")
