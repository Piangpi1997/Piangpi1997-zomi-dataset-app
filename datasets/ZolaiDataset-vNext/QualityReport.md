# Quality Report

Status: HUMAN_REVIEW_REQUIRED; training disabled. Full canonical CSV audited: 363,401 rows / 177,717,625 bytes. SHA-256 verified: `7c84b835e45fdb26aef8822367dbc698988c5a28bdfd7d992cc50bed011353fd`.

Retained candidate: 361,348; excluded rows: 2,053. Reasons may overlap; do not add them to derive unique excluded rows.

| Exclusion reason | Flagged rows |
|---|---:|
| fragment_or_abnormal_length | 1,182 |
| possible_english_review | 221 |
| mixed_script_or_language_review | 5 |
| possible_contact_or_sensitive_identifier | 342 |
| embedded_link_review | 34 |
| existing_committed_corpus_overlap | 144 |
| punctuation_case_duplicate_review | 130 |
| corrupt_or_control_text | 5 |
| html_markup | 1 |
| repetitive_spam_review | 15 |
| spam_or_boilerplate_review | 2 |

## Duplicate and baseline coverage

Input normalized exact duplicates: 0; additional punctuation/case duplicate flags: 130. Near-duplicate checks are bounded, not exhaustive.
Checked pairs: 2645; detected: 5; bucket-cap skips: 37.

Committed baseline fingerprints cover all five backend Bible corpus JSON files (including the aggregate), recognized app Bible SQLite text columns and seeded monolingual/translation/syllable text fields. Aggregate and mirrored text is deduplicated. 121,857 exact and 120,381 folded unique texts. Existing source code and corpus blobs were unchanged from base main commit 528b6d1b33276374f3e7f1d849d19aa919eb816e.
144 input rows overlap this baseline. Retained rows are new against this scoped committed inventory; novelty against deployed/private/local databases is UNKNOWN. Operational records were never included.

## Score method

Weights: language 30%, human review 20%, provenance 15%, completeness 10%, format 5%, license notice 10%, domain 5%, duplicate 5%. Language and upstream human-review proxies are 0.5 because native correctness has not been independently verified. Domain proxy is 0.5 for a two-publisher corpus. Near flags reduce duplicate proxy to 0.5. These proxies are policy choices, not measured probabilities. Scores 0.725 for 361,343 rows and 0.700 for 5 rows; no row meets the 0.8 production threshold. Native review may change scores or reject rows.

## Proposed partitions

| Partition | Rows | Connected document groups |
|---|---:|---:|
| train | 292,416 | 10,305 |
| validation | 34,558 | 1,244 |
| test | 34,374 | 1,246 |

All three exact-hash, folded-hash and document-component intersection checks pass with zero overlap. Broader semantic/paraphrase contamination is not certified.

## Verification

Six pipeline tests pass. Full-data checks assert input = retained + excluded, unique retained IDs, no split intersections, and training_eligible=false on every row. A second independent package verifier checks the serialized output files and source hash.

## Limitations

- Quality scores are conservative heuristics, not independently validated language/spelling scores.
- No native review was performed by this pipeline.
- Upstream written permission is publicly asserted; private correspondence was not examined.
- PII/spam/language regexes may miss sensitive information and may flag benign numbers. Named individuals and contextual privacy require human review.
- Near duplicate search checks trigram Jaccard >= .9 only in shared first/last four-token buckets, capped 16 candidates. Unchecked near duplicates and paraphrases may remain.
- No semantic or task-evaluation leakage verification; frozen test is provisional until native review.
- Novelty is against committed allowlist only, not deployed/local runtime databases.
- Monolingual corpus is not aligned translation supervision.
