# ZolaiDataset-vNext candidate

Status: **HUMAN_REVIEW_REQUIRED — TRAINING_DISABLED**. This is an audited dataset update candidate, not a trained model or app update.

- Discovery: 84 source entries: 1 ACCEPT for candidate audit, 62 REVIEW, 21 REJECT.
- Downloaded and hash-verified: 363,401 monolingual source rows, 177,717,625 bytes.
- Retained candidate: 361,348 rows; 2,053 excluded row decisions.
- Proposed train / validation / test: 292,416 / 34,558 / 34,374.
- Quality proxy: 0.700–0.725. These are conservative heuristic scores, not validated translation/spelling accuracy. Approved training rows: **0**.
- Existing committed allowlist: 121,857 unique normalized texts; 144 candidate input rows overlap and were excluded. Deployed/local corpus novelty remains UNKNOWN.

Read DiscoveryReport.md, DatasetCard.md, LicenseReport.md, QualityReport.md and TrainingGate.json before using data.

The `data/*.jsonl.gz` files contain preserved original and NFC/whitespace-normalized text. Every row has `training_eligible: false`. The split names are provisional candidate partitions only.

Quarantine contains source metadata or record ID/hash/reasons only. Excluded contact text is not redistributed. The original 177 MB input is not included; use the pinned checksum-verified download when reproducing.

## Rebuild in PowerShell

Requires Python 3.10+ and network access. It reads corpus allowlist files and writes a separate output folder. It does not replace application source or production datasets.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-ZolaiDataset.ps1 -ProjectPath 'C:\Users\cmfme\AndroidStudioProjects\MyApplication2'
```

Or:

```bash
python3 scripts/test_pipeline.py
python3 scripts/reproduce.py --project /path/to/zolai-gpt --output /path/to/separate-audit-output
```

For exact reproduction use the recorded baseline fingerprint artifacts or the baseline source commit. New project revisions intentionally result in a new baseline and may change overlap/splits. Algorithm and source are pinned. No HF/Kaggle publishing or model training occurs.

GitHub source review branch: https://github.com/Piangpi1997/zolai-gpt/tree/zolai-dataset-vnext-audit-20261007/datasets/ZolaiDataset-vNext

GitHub baseline audit evidence: https://github.com/Piangpi1997/zolai-gpt/actions/runs/37550623060

Large candidate data files are delivered in the downloadable package / GitHub Actions candidate artifact; they are not committed as large Git blobs. The authentic native-review sample is 100 rows per publisher and is not a prevalence estimate.
