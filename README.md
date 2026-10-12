# Zomi dataset audit workspace

ZOLAI GPT နှင့်ဆက်စပ်သော Dataset Discovery၊ License Audit၊ Quality Review နှင့် candidate build လုပ်ငန်းများကို ဒီ repository ထဲမှာ စုစည်းထားပါတယ်။

**HUMAN_REVIEW_REQUIRED — TRAINING_DISABLED**

This is a dataset workflow and review package, not a trained model or finished application. Candidate inclusion does not mean training approval.

## Contents

- [Discovery report](datasets/ZolaiDataset-vNext/DiscoveryReport.md): 84 source entries, not 84 distinct downloaded corpora.
- [Source manifest](datasets/ZolaiDataset-vNext/SourceManifest.json), dataset card, license/quality reports, changelog and provisional split manifest.
- [Review batch 2](datasets/ZolaiDataset-vNext/review-batch-2/): syllabification schema mismatch, six translation pairs and full pinned raw-text snapshot audit.
- Reproducible Python scripts, PowerShell commands and frozen existing-corpus fingerprints.
- Original upstream license and attribution notices.

The audited candidate has 361,348 retained rows from 363,401 input rows. Provisional train/validation/test counts: 292,416 / 34,558 / 34,374. All candidate rows have `training_eligible: false`; approved training rows remain zero. Native Tedim correctness, spelling and full deployed-corpus novelty are not independently verified.

## Build locally

Requires Python 3.10+, approximately 1 GB of free disk space, network access and several minutes. The pinned upstream CSV download is about 178 MB. No paid model jobs or model training are started.

```powershell
gh repo clone Piangpi1997/Piangpi1997-zomi-dataset-app
cd Piangpi1997-zomi-dataset-app
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-Candidate.ps1
```

```bash
python3 datasets/ZolaiDataset-vNext/scripts/test_pipeline.py
python3 datasets/ZolaiDataset-vNext/scripts/reproduce.py --baseline datasets/ZolaiDataset-vNext/baseline --output candidate-audit
```

The frozen baseline contains only normalized text hashes plus a file inventory. It does not contain operational users, payments, chat history, credentials or Bible text. It covers the recorded committed allowlist only, not private/deployed/local runtime databases.

## Candidate download

Open this repository's **Actions → Dataset candidate audit**. A successful run uploads `ZolaiDataset-vNext-candidate` with the compressed provisional splits and audit reports. GitHub artifact download may require sign-in and artifacts expire after 30 days. Large text data are not stored as Git source blobs; rebuild using the pinned public source and checksums when an artifact expires. A workflow definition alone is not evidence of a successful run.

## Provenance and limits

The original audit was preserved from `Piangpi1997/zolai-gpt` review branch, without merging application changes. See [MigrationManifest.json](datasets/ZolaiDataset-vNext/MigrationManifest.json) for the exact source commit and file hashes. Historical PublicationVerification and report URLs refer to the original audit, not proof of a new target-repository build.

Unclear-license sources remain quarantine metadata only. Raw contributors' personal metadata and quarantined text are not copied. Dialect labels remain source-declared until native review; do not collapse Tedim, Zo, Zopau and Zolai identities based on name similarity.

Next gates: native Tedim review, rights/provenance confirmation, further near-duplicate and privacy review, then explicit training approval. There is no training command in this workflow.
