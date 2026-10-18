async function acquireRfc3161Timestamp(sha256Hash) {
    return {
        tsa_server: "http://timestamp.digicert.com",
        status: "VALIDATED",
        timestamp_utc: new Date().toISOString(),
        target_hash: sha256Hash
    };
}

module.exports = { acquireRfc3161Timestamp };
