import sys
import json
import hashlib
import argparse
import re

def compute_evidentiary_hashes(content: str) -> dict:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    data = normalized.encode('utf-8')
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest()
    }

def calculate_h_coefficient(text: str) -> float:
    triggers = [
        r"mandatory\s+arbitration|waive.*right\s+to\s+a\s+jury",
        r"class\s+action\s+waiver",
        r"perpetual,?\s+irrevocable,?\s+royalty-free",
        r"unilateral\s+(modification|change|update).*without\s+notice",
        r"disclaim.*all\s+liability|solely\s+at\s+your\s+own\s+risk",
        r"indemnify\s+and\s+hold\s+harmless"
    ]
    matches = sum(1 for pattern in triggers if re.search(pattern, text, re.IGNORECASE))
    return round(min(1.0, matches * 0.2), 2)

def run_audit(raw_content: str):
    hashes = compute_evidentiary_hashes(raw_content)
    h_coef = calculate_h_coefficient(raw_content)
    enterprise_compliant = h_coef <= 0.15

    report = {
        "audit_engine": "Abyssal Gap nss_auditor v1.0.0",
        "integrity": hashes,
        "metrics": {
            "H_coef": h_coef,
            "procurement_threshold_met": enterprise_compliant
        },
        "status": "APPROVED" if enterprise_compliant else "HIGH_LIABILITY_HAZARD"
    }
    sys.stdout.write(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Abyssal Gap Open-Source AI Alignment & Contract Auditor")
    parser.add_argument("--file", type=str, help="Path to EULA / Terms file")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            run_audit(f.read())
    else:
        run_audit(sys.stdin.read())
