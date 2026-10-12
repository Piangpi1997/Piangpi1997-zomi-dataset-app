# Dataset update policy

This policy records the user's dataset workflow requirements for this repository.

1. Discover relevant public or authorized GitHub, Hugging Face, Kaggle and other sources.
2. Record source URL, owner, license, last update, measured/declared size and source language/dialect labels.
3. Quarantine datasets whose license or rights provenance is unclear; public visibility is not training permission.
4. Check duplicates, corrupted text, spam, HTML and privacy-sensitive content. Report check coverage and limitations.
5. Keep Tedim/Zomi/Zo/Zopau/Zolai identities separate; source tags do not prove independent dialect identity.
6. Quality scores must state their rubric and whether they are heuristics or human-validated measurements.
7. Compare against the existing committed corpus allowlist. Private/deployed corpus novelty remains UNKNOWN unless examined with authorization.
8. Prepare provisional train/validation/test splits with document and duplicate-group separation. Do not certify an evaluation set without review.
9. Maintain Dataset Card, Source Manifest, License Report, Quality Report and Changelog.
10. Build a candidate first. Do not start model training or change a production model.
11. Publish repository updates only with verified write access and retain attribution, license obligations and audit history.
12. If publishing access is unavailable, produce READY_TO_PUBLISH and state the access limitation.

Every claim must be scoped as VERIFIED, UNVERIFIED, UNKNOWN or SOURCE_DECLARED. Never fabricate repositories, APIs, uploads, training outcomes or native language accuracy.

Current gate: HUMAN_REVIEW_REQUIRED; training_enabled=false; approved_training_rows=0. ACCEPT in discovery means acceptance for candidate audit only. It does not authorize training. Human-review sample fields remain pending; no native reviewer results are invented.

Quarantine publishing contains identifiers/hashes/reasons or source metadata, not rejected personal text. Operational users, payment records, private chats and credentials must never be treated as corpus data.
