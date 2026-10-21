import sys
import os

if len(sys.argv) < 5:
    print("Usage: python3 append_dossier.py <block_num> <target_id> <title> <path> <description>")
    sys.exit(1)

block_num = sys.argv[1]
target_id = sys.argv[2]
title = sys.argv[3]
path = sys.argv[4]
desc = sys.argv[5]

card_html = f'''
            <div class="card">
                <span class="badge warning">BLOCK #{block_num} // {target_id}</span>
                <h2>{title}</h2>
                <p>{desc}</p>
                <a class="dossier-link" href="{path}">→ Open Forensic Dossier</a>
            </div>
'''

with open("index.html", "r") as f:
    content = f.read()

# Insert the new card right after the container header grid start
target_marker = '<div class="grid">'
if target_marker in content:
    updated_content = content.replace(target_marker, target_marker + "\n" + card_html)
    with open("index.html", "w") as f:
        f.write(updated_content)
    print(f"Successfully injected Block #{block_num} into master index.html without altering existing records.")
else:
    print("Error: Grid container marker not found in index.html.")
    sys.exit(1)
