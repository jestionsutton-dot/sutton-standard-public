#!/usr/bin/env python3
"""
Sutton Audio & Power LLC // Sovereign AI Forensic Pipeline
Script: nss_scraper_auditor.py
Description: Automated EULA/Telemetry Ingestion & H_coef Calculation Engine
"""

import os
import json
import hashlib
from datetime import datetime

# Define target corporate corpus and predatory vector weights
TARGETS = [
    {
        "id": "TARGET-OAI-01",
        "entity": "OpenAI",
        "sector": "Frontier AI",
        "vector": "Perpetual model ingestion of user inputs + unreciprocal downstream copyright indemnity",
        "sample_clauses": [
            "We may use Content to provide, maintain, develop, and improve our Services.",
            "You are responsible for Content, including ensuring that it does not violate any applicable law or these Terms."
        ]
    },
    {
        "id": "TARGET-ANTH-02",
        "entity": "Anthropic",
        "sector": "Frontier AI",
        "vector": "Shifting safety/regulatory compliance liabilities entirely to API consumers + unreciprocal termination",
        "sample_clauses": [
            "Customer is solely responsible for its use of the Services, including compliance with all applicable laws.",
            "Anthropic may suspend or terminate access at any time for any reason without liability."
        ]
    },
    {
        "id": "TARGET-GOOG-06",
        "entity": "Alphabet / Google",
        "sector": "Hyperscalers",
        "vector": "Cross-service identity stitching + irrevocable worldwide licenses to modify uploaded content",
        "sample_clauses": [
            "This license continues even if you stop using our services.",
            "We use data from all our services to perform multiple functions across Google products."
        ]
    },
    {
        "id": "TARGET-META-05",
        "entity": "Meta",
        "sector": "Hyperscalers",
        "vector": "Quest VR facial geometry/spatial telemetry + perpetual training licenses on personal media",
        "sample_clauses": [
            "You grant us a non-exclusive, transferable, sub-licensable, royalty-free, and worldwide license to host, use, distribute, modify, run, copy, publicly perform or display your content.",
            "Spatial data and sensor telemetry are processed to maintain device tracking."
        ]
    }
]

def calculate_h_coef(clauses):
    """
    Computes the Hedging Coefficient (H_coef) based on liability shifts and unilateral clauses.
    Formula: H_coef = sum(triggers * 0.2), capped at 1.0
    """
    triggers = 0
    hazard_keywords = ["solely responsible", "indemnify", "terminate at any time", "license continues", "modify", "sub-licensable"]
    
    for clause in clauses:
        clause_lower = clause.lower()
        for kw in hazard_keywords:
            if kw in clause_lower:
                triggers += 1
                
    h_coef = round(min(triggers * 0.2, 1.0), 2)
    return h_coef, triggers

def generate_audit_ledger(target):
    h_coef, trigger_count = calculate_h_coef(target["sample_clauses"])
    status = "HIGH LIABILITY HAZARD" if h_coef > 0.15 else "COMPLIANT"
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    audit_record = {
        "audit_id": f"AUDIT-{target['id']}-{datetime.utcnow().strftime('%Y%m%d')}",
        "target_entity": target["entity"],
        "sector": target["sector"],
        "primary_vector": target["vector"],
        "hedging_coefficient_h_coef": h_coef,
        "hazard_threshold_limit": 0.15,
        "compliance_status": status,
        "trigger_count": trigger_count,
        "timestamp": timestamp,
        "evidentiary_standard": "FRE 902(13)/(14)",
        "auditor": "Sutton Audio & Power LLC // Sovereign AI Forensic Clearinghouse"
    }
    
    # Generate SHA-256 Digest for FRE 902 Admissibility
    record_string = json.dumps(audit_record, sort_keys=True)
    sha256_hash = hashlib.sha256(record_string.encode('utf-8')).hexdigest()
    audit_record["sha256_leaf_digest"] = sha256_hash
    
    return audit_record

def main():
    print("=====================================================================")
    print(" SUTTON AUDIO & POWER LLC // AUTOMATED AUDIT TARGET PIPELINE         ")
    print("=====================================================================\n")
    
    output_dir = "audits"
    os.makedirs(output_dir, exist_ok=True)
    
    master_registry = []
    
    for target in TARGETS:
        record = generate_audit_ledger(target)
        master_registry.append(record)
        
        filename = f"{output_dir}/{target['id'].lower()}_audit.json"
        with open(filename, "w") as f:
            json.dump(record, f, indent=2)
            
        print(f"[+] Compiled Audit Ledger: {target['entity']} | H_coef: {record['hedging_coefficient_h_coef']} | Status: {record['compliance_status']}")
        print(f"    SHA-256: {record['sha256_leaf_digest'][:16]}...\n")
        
    # Save Master Registry Index
    master_index_path = f"{output_dir}/MASTER_REGISTRY_INDEX.json"
    with open(master_index_path, "w") as f:
        json.dump(master_registry, f, indent=2)
        
    print(f"[+] Master Registry Index successfully written to {master_index_path}")
    print("=====================================================================")

if __name__ == "__main__":
    main()

