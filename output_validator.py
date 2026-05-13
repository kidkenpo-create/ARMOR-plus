from __future__ import annotations


REQUIRED_OUTPUT_MARKERS = [
    "0) BLUF",
    "STEP 1 -- Acquisition Facts",
    "STEP 2 -- Regulatory Framework",
    "STEP 3A -- Zoom-Out",
    "STEP 3B -- Rungs",
    "STEP 4 -- Synthesis",
    "STEP 5 -- Final Receipt",
    "STEP 6 -- Final Determination",
    "STEP 7 -- User Validation Required",
]


def validate_output_text(answer: str) -> list[str]:
    errors: list[str] = []
    for marker in REQUIRED_OUTPUT_MARKERS:
        if marker not in answer:
            errors.append(f"Missing required output marker: {marker}")

    step_6 = _section_text(answer, "STEP 6 -- Final Determination", "STEP 7 -- User Validation Required")
    if not step_6.strip() or step_6.strip() in {":", "N/A"}:
        errors.append("STEP 6 Final Determination is empty.")

    if "legacy FAR" in answer.lower() or "legacy dfars" in answer.lower():
        errors.append("Answer appears to rely on legacy FAR/DFARS wording.")

    return errors


def _section_text(answer: str, start: str, end: str) -> str:
    start_index = answer.find(start)
    if start_index == -1:
        return ""
    start_index += len(start)
    end_index = answer.find(end, start_index)
    if end_index == -1:
        end_index = len(answer)
    return answer[start_index:end_index].strip()

