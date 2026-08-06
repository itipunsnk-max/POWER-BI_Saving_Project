"""Validation gates for the sanitized public analytics assets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "analysis" / "data-profile.json"
DASHBOARD_PATH = ROOT / "data" / "dashboard-data.json"

BLOCKED_PUBLIC_KEYS = {
    "service_id",
    "service_no",
    "site_id",
    "site_name",
    "pmorder",
    "vendor_code",
    "vendor_name",
    "technician_name",
    "call_detail",
    "user_updated_new",
}


def walk_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key).lower())
            found.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(walk_keys(child))
    return found


def close(left: float, right: float, tolerance: float = 0.01) -> None:
    if abs(left - right) > tolerance:
        raise AssertionError(f"Expected {left} to reconcile to {right}")


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))

    leaked_keys = BLOCKED_PUBLIC_KEYS & walk_keys(dashboard)
    if leaked_keys:
        raise AssertionError(f"Sensitive keys leaked to dashboard data: {leaked_keys}")

    headline = profile["headline"]
    close(
        headline["baseline_comparable_cost"]
        - headline["current_comparable_cost"],
        headline["gross_apparent_reduction"],
    )
    close(
        headline["baseline_comparable_cost"] * 0.20,
        headline["target_saving"],
    )

    bridge = profile["engineering_decomposition"]
    close(
        bridge["baseline"]
        + bridge["volume_effect"]
        + bridge["work_type_mix_effect"]
        + bridge["rate_scope_and_exposure_effect"],
        bridge["current"],
    )

    if headline["finance_validated_saving"] is not None:
        raise AssertionError("Finance-validated saving must remain null until reconciled")

    quality = profile["quality"]
    gate_total = (
        quality["pass_count"]
        + quality["fail_count"]
        + quality["blocked_count"]
    )
    if gate_total != len(quality["gates"]):
        raise AssertionError("Data-quality gate counts do not reconcile")

    if DASHBOARD_PATH.stat().st_size > 250_000:
        raise AssertionError("Dashboard aggregate payload is unexpectedly large")

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in ("*.xlsx", "*.pbix", "*.pdf", "*.docx"):
        if pattern not in gitignore:
            raise AssertionError(f"Missing private-source ignore rule: {pattern}")

    print(
        "Analytics assets passed: privacy keys, financial arithmetic, "
        "bridge reconciliation, quality counts, payload size, and gitignore."
    )


if __name__ == "__main__":
    main()
