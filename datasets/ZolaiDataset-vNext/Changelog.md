# Changelog

## 2026-10-07 — candidate.1

- Discovered 84 bounded-search source entries; 1 candidate ACCEPT / 62 REVIEW / 21 out-of-scope REJECT.
- Downloaded pinned CC-BY-4.0 monolingual release; canonical checksum and 363,401 rows verified.
- Quarantined metadata-only unclear sources; no unlicensed text added.
- Audited all input rows; retained 361,348; excluded 2,053 unique row decisions.
- Compared to committed language inventory through reproducible GitHub read-only fingerprint audit; 144 overlapping input rows excluded.
- Preserved distinct source language/dialect labels and unknown spelling annotations; no generated translations or synthetic training data.
- Built provisional document-connected partitions and hash-only excluded-row ledger.
- Added source/license/quality cards, reproducible Python/PowerShell scripts and training gate.
- No training, runtime database replacement, model deployment, app release or user-memory write occurred.
