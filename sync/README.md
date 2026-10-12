# Dataset Studio Fully Automatic GitHub Sync — Integration Contract

Status: **server-side sync module committed; NOT yet connected to Dataset Studio runtime**.

## Existing repository safety gates

The current README states `HUMAN_REVIEW_REQUIRED — TRAINING_DISABLED`, with zero approved training rows. This integration does not change that gate, approve training data, or start model training.

## Server setup

Node.js 20+. Configure `GITHUB_TOKEN` **only** in the backend secrets store. Use a fine-grained token or GitHub App installation token with **Contents: Read and write** permission limited to this repository. Never put tokens in mobile, web bundles, logs, or committed files.

```js
import { syncDatasetEvent } from "./sync/github-sync.mjs";
const result = await syncDatasetEvent({
  eventId: "evt_123",
  recordId: "row_123",
  stage: "verified",
  record: {
    publication_approved: true,
    rights_confirmed: true,
    privacy_review_passed: true,
    source: "approved-source",
    text: "example"
  }
});
```

The sample is an integration example, **not evidence of a successful live push**.

## Required Dataset Studio integration (still pending)

1. On committed import, clean, translation, verification, training-manifest or evaluation event, write a **durable outbox** entry in the same database transaction.
2. Authenticate the user, authorize the record owner, and evaluate explicit publication consent and rights/privacy gates server-side. Client-provided booleans alone must never grant publication permission.
3. A server worker reads pending events and invokes `syncDatasetEvent`; persist returned commit SHA/digest/path. Retry transient errors with backoff; send permanent failures to review.
4. Display `pending`, `synced`, `failed`, `blocked` truthfully. Do not report success until GitHub confirms the commit.
5. Use unique stable event IDs; same-content retries are idempotent. Changed content with same event ID is rejected. Create a **new event** for edits.
6. For datasets exceeding per-record limits, store approved data in appropriate artifact storage, and commit a checksum/provenance manifest rather than large blobs.
7. Keep training disabled until separate rights, native-language review, and explicit training approval. Publishing an evaluation report is not equivalent to executing a training job.

## Security limitations and future hardening

The module checks size, IDs, publication gates, and obvious token/private-key patterns. This is **not comprehensive PII detection**. A public-repo publication requires server-enforced consent, provenance, content moderation/privacy review, and audit logs. Consider protected branches and PR approval for policy/schema changes while allowing automatic publication of already-approved records.

## Verification checklist

- Unauthorized user cannot enqueue another user's records
- Private/unapproved records never reach GitHub
- Missing token fails without leakage
- Duplicate event is idempotent
- GitHub 429/5xx retries and 4xx fails clearly
- Offline worker retains pending outbox events
- Training-disabled repository remains training-disabled
- GitHub content matches SHA-256 of approved payload
- Real end-to-end import → verify → commit tested in deployed Dataset Studio

No end-to-end test or production deployment has been performed by this change.
