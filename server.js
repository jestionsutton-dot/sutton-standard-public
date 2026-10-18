const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const { normalizePayload, computeEvidentiaryHashes } = require('./utils/cryptoNorm');
const { acquireRfc3161Timestamp } = require('./utils/timestampAuthority');

const app = express();
app.use(express.json({ limit: '10mb' }));

// Serve static frontend assets from 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

app.post("/api/procurement/evaluate-vendor", async (req, res) => {
    try {
        const { vendor_name, contract_payload } = req.body;
        if (!contract_payload) {
            return res.status(400).json({ error: "Missing contract_payload for procurement evaluation." });
        }

        const normalized = normalizePayload(contract_payload);
        const hashes = await computeEvidentiaryHashes(normalized);

        const pyProcess = spawn("python3", ["engine/nss_auditor.py"]);
        let stdout = "";
        let stderr = "";

        pyProcess.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
        pyProcess.stderr.on("data", (chunk) => { stderr += chunk.toString(); });

        pyProcess.on("close", async (code) => {
            if (code !== 0) {
                return res.status(500).json({ error: "Procurement Audit Pipeline Failure", details: stderr });
            }

            const auditResult = JSON.parse(stdout);
            const timestampReceipt = await acquireRfc3161Timestamp(hashes.sha256);

            const procurementDecision = {
                vendor: vendor_name || "Unknown-Vendor",
                evaluated_at_utc: new Date().toISOString(),
                cryptographic_integrity: hashes,
                timestamp_authority: timestampReceipt,
                audit_metrics: auditResult.metrics,
                procurement_verdict: auditResult.status,
                actionable_directive: auditResult.metrics.procurement_threshold_met 
                    ? "CLEAR: Vendor contract meets institutional safety and liability standards."
                    : "BLOCK: Vendor contract exceeds maximum allowable liability threshold (H_coef > 0.15). Legal review required."
            };

            return res.json(procurementDecision);
        });

        pyProcess.stdin.write(normalized);
        pyProcess.stdin.end();

    } catch (err) {
        return res.status(500).json({ error: "Internal Procurement Gateway Error", message: err.message });
    }
});

app.get("/health", (req, res) => {
    res.json({ status: "ONLINE", engine: "NSS-v2.4 Compliance Core" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`[SUTTON AUDIO & POWER] Abyssal Gap Clearinghouse active on port ${PORT}`);
});
