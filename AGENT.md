# ARMOR Agent Retrieval Policy

This repository supports ARMOR Plus regulatory research. Agents using this repository must follow the source-authority rules below.

## Controlling Sources

Use these sources for ARMOR final answers:

- RFO FAR sources from Acquisition.gov.
- Root-level `DFARS-RFO-PART-*.txt` files.
- Root-level `DFARS-RFO-PGI-PART-*.txt` files.
- Root-level `DFARS-PGI-RFO-PART-212-Attachment-2.txt`.
- Approved class-deviation source artifacts and approved text mirrors.

## Legacy Sources

The folders under `data/legacy-crosswalk/` are legacy FAR/DFARS baseline references only.

They are not controlling authority for ARMOR answers.

Do not use `data/legacy-crosswalk/far` or `data/legacy-crosswalk/dfars` to support a final ARMOR determination unless the user explicitly asks for historical or crosswalk context.

## Required Answer Behavior

- Prefer current RFO FAR, DFARS RFO, DFARS RFO PGI, and approved class-deviation text.
- Treat legacy FAR/DFARS as background/crosswalk only.
- If RFO and legacy text differ, RFO controls for ARMOR.
- Do not cite a legacy FAR/DFARS path as the final controlling source.
- If an approved RFO source cannot be retrieved, mark the source as UTR instead of falling back to legacy FAR/DFARS.

