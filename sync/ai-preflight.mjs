/**
 * AI preflight coordinator. Node.js 20+; backend only.
 * Does NOT approve publication, start training, or call GitHub.
 * Adapters must implement durable private storage and a trusted AI provider.
 */
import { createHash, randomUUID } from "node:crypto";
const sha256 = data => createHash("sha256").update(data).digest("hex");
const json = x => JSON.stringify(x);
const LIMIT = 5000;
const norm = x => String(x ?? "").normalize("NFC").replace(/\s+/g," ").trim();
const FIELDS = ["zomi","myanmar","english"];
function validateRecord(r,index) {
  if (!r || typeof r !== "object" || Array.isArray(r)) throw new Error(`Invalid row ${index}`);
  const normalized = Object.fromEntries(FIELDS.map(k=>[k,norm(r[k])]));
  const issues = [];
  if (!normalized.zomi) issues.push("missing_zomi");
  if (FIELDS.every(k=>!normalized[k])) issues.push("empty_record");
  if (FIELDS.some(k=>normalized[k].length>20000)) issues.push("field_too_long");
  return { normalized, issues };
}
function split(records) {
  // Deterministic by content key, but NOT a substitute for group leakage checks.
  const train=[],validation=[],test=[];
  for (const r of records) {
    const key = r.group_id || r.source_document_id || r.record_id;
    const bucket = parseInt(sha256(String(key)).slice(0,8),16)%100;
    (bucket<80?train:bucket<90?validation:test).push(r);
  }
  return {train,validation,test};
}
/**
 * runPreflight({
 *   rows, datasetId,
 *   store: {savePrivateStage(datasetId, stage, payload)},
 *   ai: {translateAndCompare({raw,cleaned})},
 *   checkRights: async (datasetId) => {rights_confirmed,privacy_review_passed},
 * })
 *
 * AI output is untrusted. It must be evaluated by a human and an independent
 * quality gate. No model-generated flag is an owner approval.
 */
export async function runPreflight({rows,datasetId,store,ai,checkRights}) {
  if (!Array.isArray(rows) || rows.length===0 || rows.length>LIMIT) throw new Error("Invalid import size");
  if (!/^[\w-]{1,80}$/.test(datasetId)) throw new Error("Invalid dataset ID");
  if (typeof store?.savePrivateStage!=="function" ||
      typeof ai?.translateAndCompare!=="function" ||
      typeof checkRights!=="function") throw new Error("Trusted backend adapters required");
  const batchId=randomUUID();
  const raw=structuredClone(rows);
  await store.savePrivateStage(datasetId,"raw",{batchId,rows:raw});
  const seen=new Set();
  const cleaned=rows.map((row,i)=>{
    const {normalized,issues}=validateRecord(row,i);
    const key=sha256(FIELDS.map(k=>normalized[k].toLowerCase()).join("\u241f"));
    if(seen.has(key)) issues.push("exact_duplicate");
    seen.add(key);
    return {record_id:`row_${i}`,source_document_id:norm(row.source_document_id)||datasetId,
      ...normalized,category:norm(row.category),dialect:norm(row.dialect),
      issues,raw_sha256:sha256(json(row))};
  });
  await store.savePrivateStage(datasetId,"cleaned",{batchId,rows:cleaned});
  // Model provider must be authenticated server-side, with privacy/retention policy.
  const candidate=await ai.translateAndCompare({raw,cleaned});
  if (!Array.isArray(candidate) || candidate.length!==cleaned.length)
    throw new Error("AI provider returned invalid row count");
  const translated=candidate.map((r,i)=>{
    if (!r || typeof r!=="object") throw new Error("Malformed AI response");
    const translations=Object.fromEntries(FIELDS.map(k=>[k,norm(r[k])]));
    return {...cleaned[i],candidate:translations,
      ai_comparison:norm(r.comparison),ai_confidence:Number.isFinite(r.confidence)
        ? Math.max(0,Math.min(1,r.confidence)):null,
      review_status:"needs_human_review",
      issues:[...cleaned[i].issues,...(Array.isArray(r.issues)?r.issues.filter(x=>typeof x==="string").slice(0,20):[])]};
  });
  await store.savePrivateStage(datasetId,"translated",{batchId,rows:translated});
  const rights=await checkRights(datasetId);
  const reviewCandidates=translated.map(r=>({...r,verified:false,training_eligible:false}));
  await store.savePrivateStage(datasetId,"verified",{batchId,status:"CANDIDATES_ONLY",rows:reviewCandidates});
  const eligible=reviewCandidates.filter(r=>r.verified===true&&r.training_eligible===true);
  const splits=split(eligible);
  const manifest={batch_id:batchId,dataset_id:datasetId,training_status:"BLOCKED_PENDING_HUMAN_APPROVAL",
    rights_confirmed:rights?.rights_confirmed===true,
    privacy_review_passed:rights?.privacy_review_passed===true,
    candidate_count:reviewCandidates.length,approved_count:0,
    splits:Object.fromEntries(Object.entries(splits).map(([k,v])=>[k,v.length])),
    requires:["native_zomi_review","translation_accuracy","license_and_consent",
      "privacy","deduplication","group_leakage","owner_final_approval"]};
  await store.savePrivateStage(datasetId,"training",{batchId,manifest});
  const report={batch_id:batchId,dataset_id:datasetId,status:"AWAITING_OWNER_REVIEW",
    total_rows:rows.length,flagged_rows:reviewCandidates.filter(r=>r.issues.length).length,
    low_confidence_rows:reviewCandidates.filter(r=>r.ai_confidence===null||r.ai_confidence<0.8).length,
    rights_confirmed:manifest.rights_confirmed,privacy_review_passed:manifest.privacy_review_passed,
    training_ready:false,github_published:false};
  await store.savePrivateStage(datasetId,"review-report",{batchId,report});
  return report;
}
