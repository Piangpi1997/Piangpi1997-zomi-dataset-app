# AI-first preflight → Owner Final Approval → GitHub

**Implementation stage: backend preflight coordinator scaffold; not yet deployed or tested with a real AI provider.**

1. Import original rows to **private** `raw/` storage.
2. Deterministic Unicode NFC/whitespace cleanup, missing-field and exact-duplicate checks to `cleaned/`.
3. Trusted server-side AI provider returns Zomi/Myanmar/English translation **candidates**, comparison notes, confidence, and issues; save to `translated/`. The provider adapter is not yet implemented.
4. Create `verified/` **candidates only**. Every row has `verified=false` and `training_eligible=false` until independently reviewed. AI self-reported confidence is not verification.
5. Create `training/` manifest with `BLOCKED_PENDING_HUMAN_APPROVAL`. No model training is launched.
6. Show owner a comparison table, source rights/privacy evidence, flagged rows and manifest. Reviewers correct and approve each record as needed.
7. After a **separate authenticated owner action** and server-side snapshot-bound review, call the existing `requestPublication` and `decidePublication` services. The trusted publication worker then pushes approved immutable snapshot to GitHub. Clicking Approve never exposes a GitHub token.
8. **Actual model training** needs an approved training snapshot, independent rights/quality gate, model choice, compute provider, isolated job queue, checkpoints, metrics and versioned artifacts. Do not mistake a prepared JSONL file for a trained model.

## Host wiring still required

- Private persistent stage store; import file parsers and size/security limits
- AI translation and comparison adapter with provenance and no unapproved sensitive data sent to third parties
- Native Zomi reviewer workflow and corrections; quality/PII/license checks
- Server identity, DB integration, approval UI and immutable snapshot creation
- Worker scheduling, GitHub credential, failed-job recovery and end-to-end tests
- Training engine and model registry, with explicit approval to run training

## API example (server only)

```js
import { runPreflight } from "./ai-preflight.mjs";
const report = await runPreflight({
  rows: importedRows, datasetId: "zomi_batch_01",
  store: privateStageStore,
  ai: approvedTranslationProvider,
  checkRights: trustedRightsChecker
});
// report.status === "AWAITING_OWNER_REVIEW"
```

**Important:** A checkbox in ChatGPT is not the application's authenticated owner approval. The earlier publication SQL and worker are separate components; integrate them only after authoritative server review has confirmed the exact snapshot and permissions. This repository's existing `TRAINING_DISABLED` policy remains unchanged.
