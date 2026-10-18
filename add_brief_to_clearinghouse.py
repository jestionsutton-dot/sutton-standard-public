import re
import subprocess
import time

index_path = "index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

brief_section = '''
        <!-- The Sutton Standard: Public Audit Brief Section -->
        <section class="card" id="public-audit-brief" style="border-left: 4px solid var(--accent-green); margin-bottom: 30px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:1px solid var(--border-color); padding-bottom:10px;">
                <div>
                    <span class="metric-badge" style="background:#003311; color:#00ff66; border:1px solid #00ff66;">PUBLIC AUDIT BRIEF</span>
                    <h2 style="margin:5px 0 0 0; color:#fff;">The Sutton Standard: Forensic Translation</h2>
                </div>
                <span style="font-size:0.75rem; color:var(--text-muted);">STANDARD: NSS-v2.4</span>
            </div>
            
            <p style="font-size:0.9rem; line-height:1.6; color:var(--text-main); margin-bottom:20px;">
                Big Tech companies hide behind walls of legal legalese—user terms, arbitration clauses, and complex "privacy" updates—to quietly harvest your data, your voice, and your life. At <strong>thesuttonstandard.com</strong>, we cut through the noise, lock the evidence into cryptographic ledgers, and lay out exactly what they are doing in plain English.
            </p>

            <div style="display:grid; grid-template-columns:1fr; gap:16px;">
                <!-- 1. Google Gemini -->
                <div style="background:#000; border:1px solid var(--border-color); border-left:3px solid #00ff66; padding:15px; border-radius:4px;">
                    <h3 style="color:#00ff66; margin:0 0 8px 0; font-size:1.05rem;">1. TARGET-GOOG-06: The Illusion of Enterprise Privacy (Google Cloud / Gemini API)</h3>
                    <div style="font-size:0.85rem; line-height:1.5;">
                        <p style="margin:4px 0;"><strong>What they say:</strong> That your business data, proprietary source code, and internal documents are kept strictly isolated and secure when you use their developer tools and APIs.</p>
                        <p style="margin:4px 0; color:#ff9999;"><strong>What we found:</strong> Their boilerplate terms contain continuous loops for "service improvement and abuse detection." They retain the unilateral legal right to inspect, store, and ingest user payloads into continuous model training pipelines.</p>
                        <p style="margin:6px 0; color:#fff; background:#002211; padding:8px; border-radius:3px; border:1px solid #005522;"><strong>The Human Translation:</strong> If you feed sensitive legal documents, medical data, or proprietary code into an enterprise API to build an app, your trade secrets are being absorbed permanently into their foundational model weights without your explicit, per-tenant cryptographic consent.</p>
                    </div>
                </div>

                <!-- 2. Worldcoin -->
                <div style="background:#000; border:1px solid var(--border-color); border-left:3px solid #00ccff; padding:15px; border-radius:4px;">
                    <h3 style="color:#00ccff; margin:0 0 8px 0; font-size:1.05rem;">2. TARGET-WLD-11 & WLD-12: The Biometric Extradition Trap (Worldcoin / Tools for Humanity)</h3>
                    <div style="font-size:0.85rem; line-height:1.5;">
                        <p style="margin:4px 0;"><strong>What they say:</strong> That scanning your eyeballs with their chrome "Orbs" is safe because they instantly destroy your raw iris image and only keep a "Zero-Knowledge" mathematical hash called an IrisCode.</p>
                        <p style="margin:4px 0; color:#ff9999;"><strong>What we found:</strong> Under biometric privacy laws like Illinois BIPA and European privacy standards, converting biological eye geometry into a persistent 256-bit code does not strip away its legal definition as a biometric identifier. Once that code is committed to a decentralized ledger, permanent erasure or "revocation" is mathematically impossible.</p>
                        <p style="margin:6px 0; color:#fff; background:#001a26; padding:8px; border-radius:3px; border:1px solid #004d66;"><strong>The Human Translation:</strong> You cannot change your eyes like a password. Trading your permanent, immutable biometric identity for digital tokens creates a lifetime vulnerability where a single data breach or offshore validator leak compromises your physical identity forever.</p>
                    </div>
                </div>

                <!-- 3. PayPal -->
                <div style="background:#000; border:1px solid var(--border-color); border-left:3px solid #ffaa00; padding:15px; border-radius:4px;">
                    <h3 style="color:#ffaa00; margin:0 0 8px 0; font-size:1.05rem;">3. TARGET-PYPL-17: The Arbitrary Capital Seizure Scheme (PayPal)</h3>
                    <div style="font-size:0.85rem; line-height:1.5;">
                        <p style="margin:4px 0;"><strong>What they say:</strong> That they have the right to freeze accounts and penalize users under their Acceptable Use Policy to maintain platform safety.</p>
                        <p style="margin:4px 0; color:#ff9999;"><strong>What we found:</strong> PayPal routinely imposes arbitrary $2,500 penalties directly out of user balances alongside mandatory 180-day fund freezes for vague infractions, bypassing any form of due process or Article III judicial review.</p>
                        <p style="margin:6px 0; color:#fff; background:#261800; padding:8px; border-radius:3px; border:1px solid #664100;"><strong>The Human Translation:</strong> It is a private forfeiture scheme. They can lock up your hard-earned business capital instantly using automated black-box risk algorithms, slap you with punitive fines, and block you from a fair hearing.</p>
                    </div>
                </div>

                <!-- 4. ElevenLabs -->
                <div style="background:#000; border:1px solid var(--border-color); border-left:3px solid #ff3366; padding:15px; border-radius:4px;">
                    <h3 style="color:#ff3366; margin:0 0 8px 0; font-size:1.05rem;">4. TARGET-11LAB-04: Acoustic Biometric Laundering (ElevenLabs)</h3>
                    <div style="font-size:0.85rem; line-height:1.5;">
                        <p style="margin:4px 0;"><strong>What they say:</strong> That they offer creative voice-cloning tools while pushing 100% of the legal responsibility onto the user via disclaimers ("You warrant you have permission to clone this voice").</p>
                        <p style="margin:4px 0; color:#ff9999;"><strong>What we found:</strong> When you upload audio samples to clone a voice, the platform extracts vocal formants, pitch cadence vectors, and phonetic neural embeddings. They try to contractually "launder" their non-delegable legal duties by forcing you to sign away liability. Furthermore, even if you delete your account, those acoustic vector weights remain baked into the core model weights.</p>
                        <p style="margin:6px 0; color:#fff; background:#26000d; padding:8px; border-radius:3px; border:1px solid #660022;"><strong>The Human Translation:</strong> Your voiceprint is harvested, compressed into permanent neural weights, and exploited indefinitely. Deleting your account doesn't bring your voice back—the underlying model has already permanently consumed your acoustic identity.</p>
                    </div>
                </div>
            </div>

            <div style="margin-top:20px; padding:12px; background:#0c0d0e; border:1px solid var(--border-color); font-size:0.8rem; color:var(--text-muted);">
                <strong style="color:#fff;">Why This Matters:</strong> We aren't just logging errors; we are building court-admissible, self-authenticating digital evidence under Federal Rules of Evidence (FRE 902) and preparing structural discovery packages (FRCP Rules 30 and 34) to hold these corporations accountable. Every block we stream to this clearinghouse is a nail in the coffin of the "Big Tech black box."
            </div>
        </section>
'''

if 'id="public-audit-brief"' not in html:
    anchor = '<section class="card">'
    if anchor in html:
        html = html.replace(anchor, brief_section + "\n        " + anchor, 1)
    else:
        html = html.replace('<footer>', brief_section + "\n        <footer>")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Public Audit Brief injected into index.html.")

subprocess.run(["git", "add", "index.html"], check=True)
commit_msg = f"feat(brief): publish public human-readable audit brief [{int(time.time())}]"
subprocess.run(["git", "commit", "-m", commit_msg], check=False)
push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

if push_res.returncode == 0:
    print("🔥 SUCCESS! Public Audit Brief deployed live to https://thesuttonstandard.com")
else:
    print(f"⚠️ Push status: {push_res.stderr}")
