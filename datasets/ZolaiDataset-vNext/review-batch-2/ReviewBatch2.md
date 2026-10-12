# ZolaiDataset-vNext — Review batch 2

Audit date: 2026-10-07. Scope: pinned public files; no training, no new eligible rows, no candidate.1 split changes. This report supplements the source manifest; its measured file counts supersede metadata-only size estimates for these files.

|Dataset / owner|Source URL|Declared language|License evidence|Measured size|Quality / duplicate status|Eligibility / decision|
|---|---|---|---|---|---|---|
|zomi_syllabified_human / zomi-language-corpora|https://huggingface.co/datasets/zomi-language-corpora/zomi_syllabified_human|Zomi, source-declared; native dialect UNKNOWN|MIT card claim; no standalone LICENSE in inspected repository snapshot; originating sheet rights UNKNOWN|233,236 bytes; 42,476 TSV records|Schema mismatch; 1,824 empty last_syl values; 40,544 repeated normalized last_syl values beyond first occurrences|0 approved; REVIEW/quarantine|
|Zomi-language-data / SayaMuang|https://huggingface.co/datasets/SayaMuang/Zomi-language-data|Myanmar / English / Zomi labels, source-declared|MIT YAML claim only; upstream provenance UNKNOWN|874 bytes; 6 translation records|Valid JSON; all fields present; zero exact duplicate records; native translation accuracy UNKNOWN|0 approved; REVIEW/quarantine|
|raw-text-corpus / zomi-language-corpora|https://huggingface.co/datasets/zomi-language-corpora/raw-text-corpus|ctd / zol tags, source-declared; independent identity UNKNOWN|CC-BY-SA-4.0 card plus LICENSE file; contributor-specific rights UNKNOWN|Index/license/README inspected; complete corpus size UNKNOWN|Index contains nested structures and Genesis/test/temp paths; full text quality, privacy and duplicate audit NOT PERFORMED|0 approved; REVIEW/quarantine|

## Verified structural findings

The syllabified README advertises word/syllables data. The pinned TSV instead has last_syl, recommendation, is_ambiguous columns. Only 129 recommendation and 33 is_ambiguous fields are nonempty. Normalized last_syl values have 1,932 distinct values (including empty). Repeated syllables are not necessarily duplicate examples: full words/context are unavailable, so semantic duplication and syllable reconstruction cannot be judged. Zero HTML-pattern and replacement-character rows were detected in last_syl only; this is not a full privacy/spam clearance.

The six translation records pass structural checks only. No native Tedim reviewer has validated spelling, meaning or alignment. They must not be presented as verified translation pairs.

Raw-text corpus has a license notice, but that alone does not establish rights to contributed third-party works. Genesis filenames are a rights-review signal, not proof of a specific copyrighted edition. Full content inspection remains pending.

## Evidence and gates

fetch-evidence.json records pinned revisions, source URLs, exact downloaded byte sizes and SHA-256 hashes. AuditMetrics.json records bounded checks. API metadata snapshots provide owner, lastModified and repository file inventory. Language identity remains SOURCE_DECLARED; native correctness and upstream permission remain UNKNOWN. No training quality score is assigned to unsupported schemas or unreviewed six-pair data. candidate.1 and its training-disabled gates remain unchanged. This review does not claim exhaustive corpus deduplication, privacy review, baseline novelty or new source acceptance.

Raw-text index contains 28 distinct file paths, not a measured sentence count.
