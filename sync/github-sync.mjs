/**
 * Server-only GitHub dataset sync. Node.js 20+.
 * Never expose GITHUB_TOKEN to browsers or Android clients.
 * Call after a committed Dataset Studio event through an authenticated backend job.
 */
import { createHash } from "node:crypto";

const REPO = "Piangpi1997/Piangpi1997-zomi-dataset-app";
const ALLOWED = new Set(["imported", "cleaned", "translated", "verified", "training-manifest", "evaluation"]);
const MAX_BYTES = 900_000;
const GH = "https://api.github.com";
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const sha256 = s => createHash("sha256").update(s).digest("hex");
const safeId = id => typeof id === "string" && /^[a-zA-Z0-9_-]{1,80}$/.test(id);
const isPublicApproved = record => record?.publication_approved === true && record?.rights_confirmed === true && record?.privacy_review_passed === true;
const forbidden = /(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)/;
const toBase64 = str => Buffer.from(str, "utf8").toString("base64");

async function request(url, token, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "zomi-dataset-studio-sync",
      ...options.headers
    },
    signal: AbortSignal.timeout(20_000)
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok && res.status !== 404) {
    const error = new Error(`GitHub API HTTP ${res.status}`);
    error.status = res.status;
    error.retryAfter = Number(res.headers.get("retry-after") || 0);
    throw error;
  }
  return { status: res.status, body };
}

/**
 * payload = { eventId, stage, recordId, record, trainingApproved? }
 * Caller MUST authenticate and authorize dataset ownership, and use a durable
 * outbox keyed by eventId. This function does not implement those controls.
 */
export async function syncDatasetEvent(payload, { token = process.env.GITHUB_TOKEN, branch = "main" } = {}) {
  if (!token) throw new Error("GITHUB_TOKEN is required on the server");
  if (!safeId(payload?.eventId) || !safeId(payload?.recordId) || !ALLOWED.has(payload?.stage))
    throw new Error("Invalid sync event identifiers or stage");
  if (!isPublicApproved(payload.record)) throw new Error("Publication rights/privacy approval required");
  if (payload.stage === "training-manifest" && payload.trainingApproved !== true)
    throw new Error("Training manifest requires explicit approval");
  if (payload.stage === "evaluation" && payload.trainingApproved !== true)
    throw new Error("Evaluation publication requires training approval");
  const document = {
    schema_version: 1,
    event_id: payload.eventId,
    stage: payload.stage,
    record_id: payload.recordId,
    record: payload.record
  };
  const data = JSON.stringify(document, null, 2) + "\n";
  if (Buffer.byteLength(data) > MAX_BYTES) throw new Error("Record too large; use artifact storage");
  if (forbidden.test(data)) throw new Error("Potential secret detected");
  const digest = sha256(data);
  const path = `datasets/studio-sync/${payload.stage}/${payload.recordId}/${payload.eventId}.json`;
  const url = `${GH}/repos/${REPO}/contents/${path}`;
  const query = `?ref=${encodeURIComponent(branch)}`;
  const existing = await request(url + query, token);
  if (existing.status === 200) {
    const current = Buffer.from(existing.body.content || "", "base64").toString("utf8");
    if (sha256(current) === digest) return { status: "already_synced", path, sha: existing.body.sha };
    throw new Error("Event ID conflict: existing GitHub content differs");
  }
  const body = JSON.stringify({
    message: `dataset-sync: ${payload.stage} ${payload.recordId} [${payload.eventId}]`,
    content: toBase64(data),
    branch
  });
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const result = await request(url, token, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body
      });
      return { status: "synced", path, sha: result.body.commit?.sha, digest };
    } catch (err) {
      if (![429, 500, 502, 503, 504].includes(err.status) || attempt === 2) throw err;
      await sleep(Math.max(err.retryAfter * 1000, 500 * 2 ** attempt));
    }
  }
}
