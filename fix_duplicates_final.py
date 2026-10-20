import os
import subprocess

# 1. Remove redundant duplicate file if it exists
redundant_file = "audits/multi-platform-composite-glassmouth.html"
if os.path.exists(redundant_file):
    os.remove(redundant_file)
    print(f"🗑️ Purged redundant file: {redundant_file}")
else:
    print(f"ℹ️ {redundant_file} already removed or not found.")

# 2. Clean index.html if it contains reference to the old redundant file
index_path = "index.html"
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Remove card linking to the old redundant multi-platform composite if present
    # We'll look for the card block containing multi-platform-composite-glassmouth.html (non-v2)
    old_card_pattern = '<a href="audits/multi-platform-composite-glassmouth.html".*?</a>'
    import re
    new_html, count = re.subn(old_card_pattern, '', html, flags=re.DOTALL)
    if count > 0:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"🧹 Cleaned {count} stale duplicate card(s) from index.html grid.")
    else:
        print("✅ index.html grid has no stale duplicate cards.")

# 3. Git Stage, Commit, and Push Live
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix(clearinghouse): purge redundant duplicate multi-platform composite audit dossier"], check=False)
push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

if push_res.returncode == 0:
    print("🔥 SUCCESS! Deduplicated clearinghouse repository pushed live to https://thesuttonstandard.com")
else:
    print(f"⚠️ Push status: {push_res.stderr}")
