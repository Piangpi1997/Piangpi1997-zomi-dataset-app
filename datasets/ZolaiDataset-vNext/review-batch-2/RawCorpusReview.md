# Raw text corpus — Full pinned snapshot audit

Date: 2026-10-07. Source: https://huggingface.co/datasets/zomi-language-corpora/raw-text-corpus
Revision: b03bb5552f3d272269bd78566747cdc874e992b5.

## VERIFIED fetch and structural measurements

All 60 requested files were fetched: 30 text files and 30 metadata JSON files. Actual text files total 10,361 bytes and 82 nonempty lines. NFKC/casefold/whitespace normalization gives 77 distinct lines, with 5 repeated-line occurrences beyond first instances. One file is an exact byte duplicate of another. These line counts are not sentence counts. The index inspected in batch 2 lists 28 distinct paths; the repository snapshot actually contains 30 text files. Therefore index coverage is incomplete.

## License and provenance: REVIEW

The repository carries a CC-BY-SA-4.0 license notice. Of 30 metadata records, 29 have absent/null license values and one claims CC-BY-4.0. No nonempty permission/permission_url/rights_holder_permission field was found. This bounded schema check does not prove permission is absent elsewhere, nor does contributor metadata establish rights-holder authorization. Genesis/test/temp filenames require provenance review; no particular Bible edition is inferred. Independent dialect correctness remains UNKNOWN.

## Quality / privacy limits

Checks scan complete downloaded text files for normalized exact repetition, byte duplicates, HTML tags, replacement characters, email and URL patterns. There are zero email/URL pattern hits. This is not comprehensive personal-data detection: names, addresses and contextual sensitive content still need human review. Contributor identities and metadata values are not republished in this report. No native language accuracy score or training readiness claim is made. Near-duplicate semantic detection and baseline corpus overlap remain pending for this source.

## Decision

REVIEW / quarantine. Newly approved training rows: 0. Training remains disabled. Candidate.1 data and splits are unchanged. Raw text and contributor metadata are retained only as audit inputs, not included in training or published with this report. RawCorpusAudit.json and raw-fetch-evidence.json provide bounded metrics and pinned file hashes. This report supersedes the earlier NOT_PERFORMED full-text audit status for this pinned raw-text snapshot only.
