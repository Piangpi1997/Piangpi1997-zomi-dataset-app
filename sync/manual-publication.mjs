/**
 * Manual-final-approval publication service (Node 20+, PostgreSQL).
 * Import this ONLY in a trusted backend. Database pool and authenticated principal
 * are supplied by the host application. No browser/Android token is accepted.
 */
import { createHash, randomUUID } from "node:crypto";
import { syncDatasetEvent } from "./github-sync.mjs";

const STAGES = new Set(["imported","cleaned","translated","verified","training-manifest","evaluation"]);
const canonical = value => JSON.stringify(value, (_key, v) =>
  v && !Array.isArray(v) && typeof v === "object"
    ? Object.fromEntries(Object.entries(v).sort(([a],[b]) => a.localeCompare(b)))
    : v);
const hash = value => createHash("sha256").update(canonical(value)).digest("hex");
const validId = v => typeof v === "string" && /^[a-zA-Z0-9_-]{1,80}$/.test(v);
function principal(user) {
  if (!user?.id || !user?.authenticated) throw new Error("Authentication required");
  return String(user.id);
}
function ownerGuard(user, dataset) {
  const id = principal(user);
  if (dataset.owner_id !== id) throw new Error("Dataset ownership denied");
  return id;
}
function reviewGuard(review) {
  if (!review || review.rights_confirmed !== true ||
      review.privacy_review_passed !== true ||
      review.content_review_passed !== true ||
      review.publication_approved !== true)
    throw new Error("Server-side publication review incomplete");
}
async function audit(client, requestId, actor, action, details={}) {
  await client.query(
    "INSERT INTO dataset_publication_audit(request_id,actor_id,action,details) VALUES($1,$2,$3,$4::jsonb)",
    [requestId,actor,action,JSON.stringify(details)]
  );
}
async function transaction(pool, callback) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const result = await callback(client);
    await client.query("COMMIT");
    return result;
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally { client.release(); }
}

/**
 * Host MUST load dataset by ID from its authoritative DB, with its complete
 * immutable export payload. Never trust client-supplied owner/content/review.
 * Host MUST separately persist raw/cleaned/translated/verified/training artifacts.
 */
export async function requestPublication({ pool, user, datasetId, stage, loadDataset }) {
  const actor = principal(user);
  if (!validId(datasetId) || !STAGES.has(stage)) throw new Error("Invalid dataset/stage");
  if (typeof loadDataset !== "function") throw new Error("Authoritative dataset loader required");
  return transaction(pool, async client => {
    const dataset = await loadDataset(client, datasetId, { lock: true });
    if (!dataset) throw new Error("Dataset not found");
    ownerGuard(user, dataset);
    const snapshot = dataset.export_snapshot;
    if (!snapshot || typeof snapshot !== "object" || Array.isArray(snapshot))
      throw new Error("Export snapshot missing");
    if (Buffer.byteLength(canonical(snapshot)) > 800_000) throw new Error("Snapshot exceeds safe GitHub limit");
    const id = randomUUID(), digest = hash(snapshot);
    await client.query(
      `INSERT INTO dataset_publication_requests
        (id,owner_id,dataset_id,snapshot_sha256,snapshot_json,stage)
        VALUES ($1,$2,$3,$4,$5::jsonb,$6)`,
      [id,actor,datasetId,digest,canonical(snapshot),stage]
    );
    await audit(client,id,actor,"REQUESTED",{digest,stage});
    return { id, status:"pending_review", snapshot_sha256:digest };
  });
}

/**
 * Final approval is a separate authenticated, explicit user action.
 * The host must verify current session/MFA as appropriate, and load review
 * from trusted server-side review records; not request-body checkboxes.
 */
export async function decidePublication({ pool, user, requestId, approve, review, loadReview }) {
  const actor = principal(user);
  if (typeof approve !== "boolean") throw new Error("Explicit decision required");
  if (typeof loadReview !== "function") throw new Error("Trusted review loader required");
  return transaction(pool, async client => {
    const { rows } = await client.query(
      "SELECT * FROM dataset_publication_requests WHERE id=$1 FOR UPDATE", [requestId]);
    const row=rows[0];
    if (!row || row.owner_id !== actor) throw new Error("Publication request not found or unauthorized");
    if (row.status !== "pending_review") throw new Error("Request is no longer pending review");
    if (approve) {
      const trusted = await loadReview(client, row.dataset_id, row.id);
      reviewGuard(trusted);
      if (row.stage === "training-manifest" || row.stage === "evaluation") {
        if (trusted.training_approved !== true) throw new Error("Training gate is not approved");
      }
    }
    const status = approve ? "approved" : "rejected";
    await client.query(
      `UPDATE dataset_publication_requests
       SET status=$2,approved_by=$3,approved_at=CASE WHEN $4 THEN now() ELSE NULL END
       WHERE id=$1`, [requestId,status,approve?actor:null,approve]);
    await audit(client,requestId,actor,approve?"APPROVED":"REJECTED",
      {snapshot_sha256:row.snapshot_sha256,stage:row.stage});
    return { id:requestId,status };
  });
}

/**
 * Worker requires separate trusted service credentials and dedicated pool.
 * Do not expose this operation as an unauthenticated HTTP endpoint.
 * Single-worker use; scale with a proper lease/recovery scheduler.
 */
export async function publishNextApproved({ pool, token=process.env.GITHUB_TOKEN }) {
  if (!token) throw new Error("Missing server-side GitHub credential");
  const claimed = await transaction(pool, async client => {
    const {rows}=await client.query(
      `SELECT * FROM dataset_publication_requests
       WHERE status='approved' ORDER BY created_at
       FOR UPDATE SKIP LOCKED LIMIT 1`);
    if (!rows.length) return null;
    const row=rows[0];
    await client.query(
      "UPDATE dataset_publication_requests SET status='publishing',attempts=attempts+1 WHERE id=$1",[row.id]);
    await audit(client,row.id,"publication-worker","PUBLISH_STARTED");
    return row;
  });
  if (!claimed) return null;
  try {
    if (hash(claimed.snapshot_json) !== claimed.snapshot_sha256)
      throw new Error("Immutable snapshot digest mismatch");
    const record = {
      ...claimed.snapshot_json,
      publication_approved:true,
      rights_confirmed:true,
      privacy_review_passed:true
    };
    // Publish only an approved immutable snapshot; no post-approval edits.
    const result = await syncDatasetEvent({
      eventId:claimed.id,
      recordId:claimed.dataset_id,
      stage:claimed.stage,
      record,
      trainingApproved: ["training-manifest","evaluation"].includes(claimed.stage)
    },{token});
    await transaction(pool, async client => {
      await client.query(
        `UPDATE dataset_publication_requests
         SET status='published',github_path=$2,github_commit_sha=$3,last_error=NULL
         WHERE id=$1 AND status='publishing'`,
        [claimed.id,result.path,result.sha ?? null]);
      await audit(client,claimed.id,"publication-worker","PUBLISHED",
        {github_path:result.path,github_commit_sha:result.sha??null,status:result.status});
    });
    return {id:claimed.id,status:"published",...result};
  } catch (err) {
    await transaction(pool, async client => {
      await client.query(
        "UPDATE dataset_publication_requests SET status='failed',last_error=$2 WHERE id=$1 AND status='publishing'",
        [claimed.id,String(err.message).slice(0,500)]);
      await audit(client,claimed.id,"publication-worker","PUBLISH_FAILED",
        {error:String(err.message).slice(0,200)});
    });
    throw err;
  }
}
