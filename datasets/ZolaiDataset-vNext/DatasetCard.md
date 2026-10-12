# Dataset Card — ZolaiDataset-vNext-20261007-candidate.1

## Composition and identity

One accepted source release: [LianHong/zomi-monolingual-corpus](https://huggingface.co/datasets/LianHong/zomi-monolingual-corpus), revision `9c6bde579fcd0dc8f4e3b52a44d0632d8ac1cff8`. Compiled/reviewed upstream by Biak Hong. DOI: https://doi.org/10.5281/zenodo.22132443.

Preserve source language name `Zomi` and source ISO label `ctd`/`Tedim Chin`. These are source assertions, not independent dialect adjudication. Zo, Zopau and Zolai are not silently equated with this source. All spelling-standard values are upstream `unknown`; regional labels describe source associations, not proven speaker dialect.

## Intended use and restrictions

Review candidate for written monolingual language research. It is not English–Tedim aligned supervision and cannot demonstrate exact translation performance. Native Tedim review, calibration and task evaluation are required. Model training is disabled. No evidence of improved model performance exists.

## Measured data

361,348 retained rows from 363,401 input rows. Source distribution: Zomi Daily 352,563; Agape Digest Magazine 8,785. Two publishers dominate. Upstream 267,456 regions are Unknown; all 363,401 spelling annotations are unknown. One upstream reviewer is asserted, no independent pipeline-native review.

Fields preserve original_text, normalized_text, record_id, content hashes, source revision/row/document URL, source labels, topic, region, permission/review assertions, heuristic score/flags, document component, provisional split and training_eligible=false.

## Processing and splits

NFC plus whitespace normalization, retaining original text separately. No invented translations, spelling corrections or synthetic training sentences. Conservative corruption, fragments, markup, contacts, spam, possible English/mixed script and embedded URL checks. Exact and punctuation/case-folded duplicate filtering. Existing committed corpus overlap filtering. Hash-only quarantine avoids republishing excluded private text.

80/10/10 hash buckets by source document plus connected duplicate groups; row ratios are measured, not forced.

Train 292,416; validation 34,558; test 34,374. Exact/folded hash and document-component intersections are zero. Broader near/paraphrase and semantic leakage remain UNKNOWN. Test is frozen by file checksums provisionally, not certified task evaluation.

## License and credit

Derived text remains CC BY 4.0; https://creativecommons.org/licenses/by/4.0/. Attribution: Zomi Monolingual Corpus v1.0, compiled and reviewed by Biak Hong (2026), with acknowledged source material from Zomi Daily and Agape Digest Magazine. Retain upstream permanent IDs and DOI. Changes: additional filters, baseline comparison, normalization, provisional partitions and audit metadata. No endorsement implied.

Upstream owner asserts written publisher permissions received on 2026-08-26. Public license/attribution statements are verified; private correspondence was not independently inspected. See upstream notices in licenses/.

## Known limitations

- Quality scores are conservative heuristics, not independently validated language/spelling scores.
- No native review was performed by this pipeline.
- Upstream written permission is publicly asserted; private correspondence was not examined.
- PII/spam/language regexes may miss sensitive information and may flag benign numbers. Named individuals and contextual privacy require human review.
- Near duplicate search checks trigram Jaccard >= .9 only in shared first/last four-token buckets, capped 16 candidates. Unchecked near duplicates and paraphrases may remain.
- No semantic or task-evaluation leakage verification; frozen test is provisional until native review.
- Novelty is against committed allowlist only, not deployed/local runtime databases.
- Monolingual corpus is not aligned translation supervision.
