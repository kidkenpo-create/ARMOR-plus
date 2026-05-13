from __future__ import annotations

from armor_types import ThresholdDecision


MICRO_PURCHASE_THRESHOLD = 15_000.00


def evaluate_threshold(amount: float, threshold: float, operator: str = "exceeds") -> ThresholdDecision:
    if operator == "exceeds":
        result = amount > threshold
    elif operator == "at_or_below":
        result = amount <= threshold
    elif operator == "equals_or_exceeds":
        result = amount >= threshold
    elif operator == "below":
        result = amount < threshold
    else:
        raise ValueError(f"Unsupported threshold operator: {operator}")

    return ThresholdDecision(
        amount=amount,
        threshold=threshold,
        operator=operator,
        result=result,
        convention_c_applies=True,
    )


def resolve_thresholds(amounts: list[float], threshold: float = MICRO_PURCHASE_THRESHOLD) -> list[ThresholdDecision]:
    return [evaluate_threshold(amount, threshold, "exceeds") for amount in amounts]

