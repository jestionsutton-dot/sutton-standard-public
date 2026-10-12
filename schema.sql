PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. The Hop Sequence Ledger (Chronological Multi-Agent Trace)
CREATE TABLE IF NOT EXISTS hop_sequences (
    hop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id TEXT NOT NULL,
    source_agent TEXT NOT NULL,
    target_agent TEXT NOT NULL,
    payload_length INTEGER NOT NULL,
    payload_sha256 TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hop_eval ON hop_sequences(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_hop_time ON hop_sequences(timestamp);

-- 2. The Latent Delta-Spike Registry (Cognitive Shift & Override Tracking)
CREATE TABLE IF NOT EXISTS latent_deltas (
    delta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id TEXT NOT NULL,
    hop_id INTEGER NOT NULL,
    cognitive_shift_score REAL NOT NULL,
    safety_override_detected BOOLEAN NOT NULL,
    intervention_reason TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (hop_id) REFERENCES hop_sequences(hop_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_delta_eval ON latent_deltas(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_delta_score ON latent_deltas(cognitive_shift_score);

-- 3. The Cryptographic Witness Layer (Localized Append-Only Chain of Custody)
CREATE TABLE IF NOT EXISTS witness_ledger (
    block_index INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_data TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    block_hash TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_witness_hash ON witness_ledger(block_hash);
CREATE INDEX IF NOT EXISTS idx_witness_eval ON witness_ledger(evaluation_id);
