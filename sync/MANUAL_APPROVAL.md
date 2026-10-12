# Manual Final Approval — Dataset Studio Publication Gate

**Status: implementation scaffold committed, not deployed or end-to-end verified.**

## New files

- `sync/migrations/001_manual_publication.sql` — PostgreSQL snapshot, status, immutable payload and append-only audit.
- `sync/manual-publication.mjs` — authenticated owner request, final approval/rejection, and worker.
- `sync/github-sync.mjs` — server-side GitHub Contents API publishing, idempotent event paths and retry.

## Intended lifecycle

`raw → cleaned → translated → verified → training preparation → owner review → explicit approve → publish worker → GitHub`

Processing stages may run automatically **in private storage**. Nothing is published before final owner approval. Review is per immutable snapshot, not blanket permission for future imports. No AI model training is initiated by this implementation.

## Backend integration required

The Dataset Studio app must supply:

1. A PostgreSQL connection pool with a restricted server identity. Apply the SQL migration.
2. Session-verified `user = {id, authenticated:true}` created **server-side** from a trusted identity provider. Do not take user ID from JSON body.
3. `loadDataset(client, id, {lock:true})` that loads the record with `owner_id` and `export_snapshot` from the authoritative DB. The snapshot should contain approved *publishable* fields only, with no secrets, contact information, or private uploads.
4. `loadReview(client,datasetId,requestId)` that returns server-side rights, privacy, content and (if relevant) training approval for the **exact snapshot digest and request ID**. Implement and enforce digest binding in this callback. A user checking boxes in the browser is insufficient.
5. Explicit authenticated POST routes for requesting publication and approving/rejecting a particular snapshot. CSRF protection, rate limits and step-up authentication should be applied in the host.
6. Private worker scheduling with secure `GITHUB_TOKEN` or short-lived GitHub App installation token. No browser or Android GitHub token.
7. Retry scheduler for failed/stuck jobs with leases, bounded retry counts and audit logging. The sample worker is single-worker and deliberately does not silently republish failures.
8. Record-by-record export policy, privacy/license review, optional PII scanning, dataset provenance and GitHub branch protection.

## Example integration pseudocode

```js
// After verifying the logged-in session and loading the server DB:
const pending = await requestPublication({
  pool, user: sessionUser, datasetId: req.body.datasetId,
  stage: "verified", loadDataset
});
// After owner explicitly reviews the immutable snapshot:
const approved = await decidePublication({
  pool, user: sessionUser, requestId: req.body.requestId,
  approve: true, loadReview
});
// Private worker only:
const published = await publishNextApproved({pool});
```

**Do not run the worker until host-side review and snapshot-digest checks are integrated.**

## Security and correctness caveats

- This repository is public. Publish **only** licensed, consented, reviewed content; the repository history is not a secure deletion mechanism.
- The existing candidate dataset has `HUMAN_REVIEW_REQUIRED — TRAINING_DISABLED`; this change does not override that gate.
- The publication worker stamps approval metadata on the serialized GitHub payload; the source snapshot remains immutable in PostgreSQL.
- GitHub writes are not transactional with PostgreSQL. The event-based path allows safe retries; operations need monitoring and recovery.
- Publication status in the UI must be backed by the DB state, not by optimistic client messages.
- Code has not been run against a deployed Dataset Studio, PostgreSQL, or GitHub token.

## Acceptance tests before production

- Cross-user access is denied, with no request contents leaked.
- Approve and reject are owner-only; missing review flags deny.
- Review is bound to the exact snapshot hash.
- Training remains blocked without explicit training approval.
- DB snapshot cannot change after request creation.
- GitHub commit cannot happen before explicit approval.
- Same event retry never overwrites different content.
- GitHub rate limits, token expiry, network failure, crash recovery and audit consistency tested.
- Public PII/license gate tested using intentionally disallowed samples.
