"""Build sanitized analytics assets from the private service-tracking workbook.

The source workbook is intentionally ignored by git. This script exports only
aggregated statistics that are safe to use in the public dashboard mock-up.
It never emits site, vendor, technician, user, free-text call detail, or raw IDs.
"""

from __future__ import annotations

import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "service_tracking_cleaned-Rev.1.xlsx"
ANALYSIS_DIR = ROOT / "analysis"
DATA_DIR = ROOT / "data"
BASELINE_YEAR = 2025
REVIEW_DATE = date(2026, 8, 7)
DOCUMENTED_BASELINE = 15_359_352.14
DOCUMENTED_PM_CM_BASELINE = 12_590_005.44


def to_builtin(value: Any) -> Any:
    """Convert pandas/numpy values into deterministic JSON-compatible values."""
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if math.isnan(float(value)) or math.isinf(float(value)):
            return None
        return round(float(value), 6)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {str(key): to_builtin(value) for key, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def coverage(series: pd.Series) -> tuple[int, float]:
    text = series.astype("string").str.strip()
    valid = series.notna() & text.ne("")
    return int(valid.sum()), float(valid.mean())


def parse_mixed_datetime(series: pd.Series) -> pd.Series:
    """Parse Excel datetimes plus month-first text explicitly.

    WORKINPROGRESS and RESOLVED_DATE contain a mixture of native Excel
    datetimes and month-first text. ``format='mixed', dayfirst=False`` locks the
    observed source convention so Power BI/local machine locale cannot silently
    swap day and month. Upstream ISO 8601 remains the target remediation.
    """
    return pd.to_datetime(series, format="mixed", dayfirst=False, errors="coerce")


def gate(
    key: str,
    label: str,
    actual: float | None,
    target: float | None,
    unit: str,
    direction: str,
    note: str,
) -> dict[str, Any]:
    if actual is None or target is None:
        status = "blocked"
    elif direction == "gte":
        status = "pass" if actual >= target else "fail"
    elif direction == "lte":
        status = "pass" if actual <= target else "fail"
    elif direction == "eq":
        status = "pass" if actual == target else "fail"
    else:
        raise ValueError(f"Unsupported direction: {direction}")
    return {
        "key": key,
        "label": label,
        "actual": to_builtin(actual),
        "target": to_builtin(target),
        "unit": unit,
        "direction": direction,
        "status": status,
        "note": note,
    }


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source workbook: {SOURCE}")

    clean = pd.read_excel(SOURCE, sheet_name="Clean_Data")
    source_column_count = len(clean.columns)
    if clean.empty:
        raise ValueError("Clean_Data is empty")

    required = {
        "SERVICE_ID",
        "SERVICE_DATE",
        "CLOSE_DATE",
        "PMACTTYPES",
        "SLA_STATUS",
        "PROBLEM_TYPE_DESC",
        "PROB_DETAIL_DESC",
        "PROB_RESOLVE_DESC",
        "VENDOR_CODE",
    }
    missing = sorted(required - set(clean.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    amount_col = clean.columns[-1]
    asset_col = next((col for col in clean.columns if "Asset" in str(col)), None)
    if asset_col is None:
        raise ValueError("Asset column was not found")

    clean = clean.copy()
    clean["service_date"] = parse_mixed_datetime(clean["SERVICE_DATE"])
    clean["close_date"] = parse_mixed_datetime(clean["CLOSE_DATE"])
    clean["amount"] = pd.to_numeric(clean[amount_col], errors="coerce")
    clean["year"] = clean["service_date"].dt.year.astype("Int64")
    clean["month_number"] = clean["service_date"].dt.month.astype("Int64")
    clean["month"] = clean["service_date"].dt.to_period("M").astype("string")

    current_year = int(clean["year"].dropna().max())
    current_year_rows = clean[clean["year"] == current_year]
    comparison_month = int(current_year_rows["month_number"].dropna().max())
    baseline = clean[
        (clean["year"] == BASELINE_YEAR)
        & (clean["month_number"] <= comparison_month)
    ]
    current = clean[
        (clean["year"] == current_year)
        & (clean["month_number"] <= comparison_month)
    ]

    baseline_cost = float(baseline["amount"].sum())
    current_cost = float(current["amount"].sum())
    gross_apparent_reduction = baseline_cost - current_cost
    apparent_reduction_pct = (
        gross_apparent_reduction / baseline_cost if baseline_cost else None
    )
    target_saving = baseline_cost * 0.20
    target_cost = baseline_cost - target_saving
    target_headroom = target_cost - current_cost

    baseline_count = int(len(baseline))
    current_count = int(len(current))
    baseline_avg = baseline_cost / baseline_count
    current_avg = current_cost / current_count

    work_types = sorted(
        set(baseline["PMACTTYPES"].dropna())
        | set(current["PMACTTYPES"].dropna())
    )
    work_type_stats: dict[str, dict[str, float]] = {}
    for work_type in work_types:
        base_slice = baseline[baseline["PMACTTYPES"] == work_type]
        current_slice = current[current["PMACTTYPES"] == work_type]
        work_type_stats[str(work_type)] = {
            "base_n": float(len(base_slice)),
            "current_n": float(len(current_slice)),
            "base_rate": float(base_slice["amount"].mean()),
            "current_rate": float(current_slice["amount"].mean()),
        }

    volume_effect = (current_count - baseline_count) * baseline_avg
    mix_effect = current_count * sum(
        (
            stats["current_n"] / current_count
            - stats["base_n"] / baseline_count
        )
        * stats["base_rate"]
        for stats in work_type_stats.values()
    )
    rate_scope_effect = sum(
        stats["current_n"]
        * (stats["current_rate"] - stats["base_rate"])
        for stats in work_type_stats.values()
    )

    annual = (
        clean.groupby("year", dropna=False)
        .agg(rows=("SERVICE_ID", "size"), cost=("amount", "sum"))
        .reset_index()
        .dropna(subset=["year"])
    )
    annual["year"] = annual["year"].astype(int)

    monthly = (
        clean.groupby(["month", "year", "month_number", "PMACTTYPES"], dropna=False)
        .agg(rows=("SERVICE_ID", "size"), cost=("amount", "sum"))
        .reset_index()
        .dropna(subset=["year", "month_number"])
    )
    monthly["year"] = monthly["year"].astype(int)
    monthly["month_number"] = monthly["month_number"].astype(int)

    comparable_months = (
        clean[
            clean["year"].isin([BASELINE_YEAR, current_year])
            & (clean["month_number"] <= comparison_month)
        ]
        .groupby(["year", "month_number"], dropna=False)
        .agg(rows=("SERVICE_ID", "size"), cost=("amount", "sum"))
        .reset_index()
    )
    comparable_months["year"] = comparable_months["year"].astype(int)
    comparable_months["month_number"] = comparable_months["month_number"].astype(int)

    work_type_comparison_rows: list[dict[str, Any]] = []
    for work_type in work_types:
        for period, frame in (("baseline", baseline), ("current", current)):
            selected = frame[frame["PMACTTYPES"] == work_type]
            work_type_comparison_rows.append(
                {
                    "work_type": str(work_type),
                    "period": period,
                    "rows": int(len(selected)),
                    "cost": float(selected["amount"].sum()),
                    "average_cost": float(selected["amount"].mean()),
                }
            )

    problem_type = (
        clean.assign(
            category=clean["PROBLEM_TYPE_DESC"].fillna("ไม่ระบุ").astype(str).str.strip()
        )
        .groupby("category", dropna=False)
        .agg(rows=("SERVICE_ID", "size"), cost=("amount", "sum"))
        .reset_index()
        .sort_values("cost", ascending=False)
    )
    problem_type["share"] = problem_type["cost"] / clean["amount"].sum()

    resolution = (
        clean.assign(
            category=clean["PROB_RESOLVE_DESC"].fillna("ไม่ระบุ").astype(str).str.strip()
        )
        .groupby("category", dropna=False)
        .agg(rows=("SERVICE_ID", "size"), cost=("amount", "sum"))
        .reset_index()
        .sort_values("cost", ascending=False)
    )
    resolution["share"] = resolution["cost"] / clean["amount"].sum()
    resolution["cumulative_share"] = resolution["share"].cumsum()

    symptom_text = clean["PROB_DETAIL_DESC"].astype("string").str.strip()
    meaningful_symptom = (
        symptom_text.notna()
        & symptom_text.ne("")
        & ~symptom_text.str.lower().isin({"อื่น ๆ", "อื่นๆ", "other"})
    )
    unknown_symptom = ~meaningful_symptom
    unknown_symptom_cost = float(clean.loc[unknown_symptom, "amount"].sum())

    asset_count, asset_coverage = coverage(clean[asset_col])
    vendor_count, vendor_coverage = coverage(clean["VENDOR_CODE"])
    work_type_valid = clean["PMACTTYPES"].isin(["PM", "CM"])

    date_columns = [
        "SERVICE_DATE",
        "ASSIGNED_DATE",
        "WORKINPROGRESS",
        "RESOLVED_DATE",
        "CLOSE_DATE",
    ]
    parsed_dates = {col: parse_mixed_datetime(clean[col]) for col in date_columns}
    sequence_pairs = [
        ("SERVICE_DATE", "ASSIGNED_DATE"),
        ("ASSIGNED_DATE", "WORKINPROGRESS"),
        ("WORKINPROGRESS", "RESOLVED_DATE"),
        ("RESOLVED_DATE", "CLOSE_DATE"),
        ("SERVICE_DATE", "CLOSE_DATE"),
    ]
    date_sequence_violations = 0
    date_sequence_comparisons = 0
    for earlier, later in sequence_pairs:
        comparable = parsed_dates[earlier].notna() & parsed_dates[later].notna()
        date_sequence_comparisons += int(comparable.sum())
        date_sequence_violations += int(
            (parsed_dates[earlier][comparable] > parsed_dates[later][comparable]).sum()
        )
    date_sequence_validity = 1 - (
        date_sequence_violations / date_sequence_comparisons
    )

    latest_service_date = clean["service_date"].max()
    latest_close_date = clean["close_date"].max()
    freshness_days = (pd.Timestamp(REVIEW_DATE) - latest_close_date.normalize()).days

    sla_assessed = clean["SLA_STATUS"].isin(["Met", "Missed"])
    sla_met = clean["SLA_STATUS"].eq("Met")
    current_sla_assessed = current["SLA_STATUS"].isin(["Met", "Missed"])
    current_sla_met = current["SLA_STATUS"].eq("Met")

    exact_duplicate_rows = int(clean.duplicated().sum())
    service_id_duplicate_rows = int(
        clean.duplicated("SERVICE_ID", keep=False).sum()
    )
    service_id_unique_pct = 1 - service_id_duplicate_rows / len(clean)

    gates = [
        gate(
            "service_id_unique",
            "Service ID ไม่ซ้ำ",
            service_id_unique_pct,
            1.0,
            "ratio",
            "eq",
            "Grain ต้องเป็น 1 แถวต่อ Service ID",
        ),
        gate(
            "work_type_coverage",
            "PM/CM coverage",
            float(work_type_valid.mean()),
            0.98,
            "ratio",
            "gte",
            "ใช้เฉพาะค่า PM และ CM ที่ผ่าน mapping",
        ),
        gate(
            "meaningful_symptom_coverage",
            "Meaningful symptom coverage",
            float(meaningful_symptom.mean()),
            0.95,
            "ratio",
            "gte",
            "ไม่นับค่าว่างและ 'อื่น ๆ' เป็นอาการที่วิเคราะห์ได้",
        ),
        gate(
            "asset_coverage",
            "Asset match coverage",
            asset_coverage,
            0.98,
            "ratio",
            "gte",
            "จำเป็นต่อ Repeat Repair, MTBF และ Repair-vs-Replace",
        ),
        gate(
            "vendor_code_coverage",
            "Vendor code coverage",
            vendor_coverage,
            0.98,
            "ratio",
            "gte",
            "ต้องใช้รหัสมาตรฐานแทนชื่ออิสระ",
        ),
        gate(
            "date_sequence_validity",
            "Date sequence validity",
            date_sequence_validity,
            1.0,
            "ratio",
            "eq",
            f"พบลำดับเวลาผิด {date_sequence_violations} จุดจาก {date_sequence_comparisons} comparisons",
        ),
        gate(
            "source_freshness_days",
            "Source freshness",
            float(freshness_days),
            7.0,
            "days",
            "lte",
            "ใช้วันที่ปิดงานล่าสุดเทียบวัน review; เกณฑ์ชั่วคราวไม่เกิน 7 วัน",
        ),
        gate(
            "finance_reconciliation",
            "Finance reconciliation variance",
            None,
            0.01,
            "ratio",
            "lte",
            "ไม่มี Actual + Commitment + Accrual และ Finance control total ใน workbook นี้",
        ),
    ]

    cost = clean["amount"]
    concentration = []
    for fraction in (0.01, 0.05, 0.10, 0.20):
        count = max(1, int(math.ceil(len(cost) * fraction)))
        concentration.append(
            {
                "top_row_fraction": fraction,
                "row_count": count,
                "cost_share": float(cost.nlargest(count).sum() / cost.sum()),
            }
        )

    annual_2025 = float(clean.loc[clean["year"] == BASELINE_YEAR, "amount"].sum())
    pass_count = sum(item["status"] == "pass" for item in gates)
    fail_count = sum(item["status"] == "fail" for item in gates)
    blocked_count = sum(item["status"] == "blocked" for item in gates)

    profile: dict[str, Any] = {
        "source": {
            "workbook": SOURCE.name,
            "sheet": "Clean_Data",
            "review_date": REVIEW_DATE.isoformat(),
            "rows": int(len(clean)),
            "columns": int(source_column_count),
            "latest_service_date": to_builtin(latest_service_date),
            "latest_close_date": to_builtin(latest_close_date),
            "comparison": {
                "baseline_year": BASELINE_YEAR,
                "current_year": current_year,
                "through_month": comparison_month,
                "label": f"Jan-{comparison_month:02d} {BASELINE_YEAR} vs Jan-{comparison_month:02d} {current_year}",
            },
            "text_date_locale": "month-first en-US observed; upstream ISO 8601 required",
            "privacy": "Sanitized aggregates only; no raw identifiers, people, sites, vendors, or free text exported.",
        },
        "headline": {
            "total_rows": int(len(clean)),
            "total_cost": float(clean["amount"].sum()),
            "annual_2025_cost": annual_2025,
            "documented_2025_baseline": DOCUMENTED_BASELINE,
            "baseline_difference": DOCUMENTED_BASELINE - annual_2025,
            "documented_pm_cm_baseline": DOCUMENTED_PM_CM_BASELINE,
            "pm_cm_baseline_difference": annual_2025 - DOCUMENTED_PM_CM_BASELINE,
            "baseline_comparable_cost": baseline_cost,
            "current_comparable_cost": current_cost,
            "gross_apparent_reduction": gross_apparent_reduction,
            "apparent_reduction_pct": apparent_reduction_pct,
            "target_saving": target_saving,
            "target_cost": target_cost,
            "target_headroom": target_headroom,
            "finance_validated_saving": None,
            "status": "provisional_actual_only",
        },
        "engineering_decomposition": {
            "baseline": baseline_cost,
            "volume_effect": volume_effect,
            "work_type_mix_effect": mix_effect,
            "rate_scope_and_exposure_effect": rate_scope_effect,
            "current": current_cost,
            "reconciliation_check": baseline_cost
            + volume_effect
            + mix_effect
            + rate_scope_effect
            - current_cost,
            "warning": "Rate/scope effect also includes severity mix, job scope, pricing and missing commitment/accrual exposure; it is not proven saving.",
        },
        "operations": {
            "sla_assessed_rows": int(sla_assessed.sum()),
            "sla_coverage": float(sla_assessed.mean()),
            "sla_met_rate": float(sla_met.sum() / sla_assessed.sum()),
            "current_sla_assessed_rows": int(current_sla_assessed.sum()),
            "current_sla_met_rate": float(
                current_sla_met.sum() / current_sla_assessed.sum()
            ),
            "meaningful_symptom_rows": int(meaningful_symptom.sum()),
            "meaningful_symptom_coverage": float(meaningful_symptom.mean()),
            "unknown_symptom_cost": unknown_symptom_cost,
            "unknown_symptom_cost_share": float(
                unknown_symptom_cost / clean["amount"].sum()
            ),
            "asset_rows": asset_count,
            "asset_coverage": asset_coverage,
            "vendor_code_rows": vendor_count,
            "vendor_code_coverage": vendor_coverage,
        },
        "quality": {
            "exact_duplicate_rows": exact_duplicate_rows,
            "service_id_duplicate_rows": service_id_duplicate_rows,
            "date_sequence_violations": date_sequence_violations,
            "date_sequence_comparisons": date_sequence_comparisons,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "blocked_count": blocked_count,
            "gates": gates,
        },
        "annual": records(annual),
        "monthly": records(monthly),
        "comparable_months": records(comparable_months),
        "work_type_comparison": work_type_comparison_rows,
        "problem_type": records(problem_type),
        "resolution_pareto": records(resolution.head(12)),
        "cost_concentration": concentration,
        "sensitive_field_inventory": {
            "raw_fields_excluded_from_public_assets": [
                "SERVICE_ID",
                "SERVICE_NO",
                "SITE_ID",
                "SITE_NAME",
                "PMORDER",
                "VENDOR_CODE",
                "VENDOR_NAME",
                "TECHNICIAN_NAME",
                "USER_UPDATED_*",
                "CALL_DETAIL",
                "Asset number",
            ]
        },
    }

    dashboard = {
        "meta": profile["source"],
        "headline": profile["headline"],
        "engineeringDecomposition": profile["engineering_decomposition"],
        "operations": profile["operations"],
        "quality": profile["quality"],
        "comparableMonths": profile["comparable_months"],
        "monthly": profile["monthly"],
        "workTypeComparison": profile["work_type_comparison"],
        "problemType": profile["problem_type"],
        "resolutionPareto": profile["resolution_pareto"],
        "costConcentration": profile["cost_concentration"],
    }

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    profile_path = ANALYSIS_DIR / "data-profile.json"
    dashboard_path = DATA_DIR / "dashboard-data.json"
    profile_path.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    dashboard_path.write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Wrote {profile_path.relative_to(ROOT)}")
    print(f"Wrote {dashboard_path.relative_to(ROOT)}")
    print(
        f"Rows={len(clean):,}; total={clean['amount'].sum():,.2f}; "
        f"comparable reduction={apparent_reduction_pct:.2%}; "
        f"quality pass/fail/blocked={pass_count}/{fail_count}/{blocked_count}"
    )


if __name__ == "__main__":
    main()
