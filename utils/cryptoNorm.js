const crypto = require('crypto');

function normalizePayload(payload) {
    return payload.replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim();
}

function computeEvidentiaryHashes(content) {
    const data = Buffer.from(content, 'utf-8');
    return {
        sha256: crypto.createHash('sha256').update(data).digest('hex'),
        sha512: crypto.createHash('sha512').update(data).digest('hex')
    };
}

module.exports = { normalizePayload, computeEvidentiaryHashes };
