import crypto from 'crypto';

export function normalizePayload(payload: string): string {
    return payload.replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim();
}

export async function computeEvidentiaryHashes(content: string) {
    const data = Buffer.from(content, 'utf-8');
    return {
        sha256: crypto.createHash('sha256').update(data).digest('hex'),
        sha512: crypto.createHash('sha512').update(data).digest('hex')
    };
}
