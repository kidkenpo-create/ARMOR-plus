# ARMOR Plus Source Corpus

This repository contains source material used by ARMOR Plus, an RFO-first acquisition regulatory research tool.

## Controlling ARMOR Sources

For final ARMOR answers, use current approved RFO-oriented sources:

- Acquisition.gov RFO FAR sources.
- Root-level `DFARS-RFO-PART-*.txt` files.
- Root-level `DFARS-RFO-PGI-PART-*.txt` files.
- `DFARS-PGI-RFO-PART-212-Attachment-2.txt`.
- Approved class-deviation source artifacts and approved text mirrors.

Root-level DFARS RFO and DFARS RFO PGI files are approved retrieval mirrors used by ARMOR Plus. Do not move or rename them without updating the ARMOR app lookup and validation rules.

## Legacy Crosswalk Sources

Legacy FAR/DFARS baseline submodules are quarantined under:

- `data/legacy-crosswalk/far`
- `data/legacy-crosswalk/dfars`

Those folders are crosswalk/background only. They are not controlling authority for final ARMOR answers.

## Agent Guidance

Agents indexing this repository should read `AGENT.md` and `README_FOR_GENAI.md` before using repository content for regulatory answers.

If current RFO authority cannot be retrieved, mark the source as UTR instead of answering from legacy FAR/DFARS.

## Historical Helper Files

Files such as `issue_router.py` and `acquisition_regression_cases.json` preserve legacy classroom/crosswalk citations so older training questions can be mapped to current RFO authority. These files are not standalone answer authority. When they mention a legacy FAR/DFARS citation, treat it as crosswalk context only and verify the final answer against the current RFO FAR, DFARS RFO, DFARS RFO PGI, or approved class-deviation source.
