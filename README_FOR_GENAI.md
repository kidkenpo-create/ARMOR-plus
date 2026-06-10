# README For GenAI / Agent Indexing

ARMOR Plus is an RFO-first regulatory research corpus. This repository includes both current ARMOR source mirrors and legacy baseline material used only for crosswalk and testing.

## Use For Final ARMOR Answers

Agents should use:

- Acquisition.gov RFO FAR pages.
- Root-level `DFARS-RFO-PART-*.txt` files.
- Root-level `DFARS-RFO-PGI-PART-*.txt` files.
- `DFARS-PGI-RFO-PART-212-Attachment-2.txt`.
- Approved class-deviation source artifacts and approved text mirrors.

These are the approved ARMOR source paths for current RFO-oriented analysis.

## Do Not Use For Final ARMOR Answers

Do not use these folders as controlling authority:

- `data/legacy-crosswalk/far`
- `data/legacy-crosswalk/dfars`

Those folders are retained only to help with:

- historical crosswalks,
- regression testing,
- drift detection,
- explanation of old citation pathways.

If a user asks a question using a legacy FAR/DFARS citation, route the answer to the current RFO FAR, DFARS RFO, DFARS RFO PGI, or approved class-deviation source before finalizing.

## Source Drift Warning

Open-ended web or repository search can drift back to legacy FAR/DFARS. ARMOR answers must be constrained to approved RFO/current authority sources. Legacy baseline files must not be treated as final answer sources.

