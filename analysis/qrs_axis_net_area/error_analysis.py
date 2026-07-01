#!/usr/bin/env python3
"""Analyze error patterns for JPG-derived QRS-axis estimates."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


METHODS = [
    ("direct_i_avf", "direct_axis_deg", "direct_abs_error_deg"),
    ("lead_i_ii_reconstructed_avf", "lead_i_ii_axis_deg", "lead_i_ii_abs_error_deg"),
    ("limb_lead_least_squares", "limb_ls_axis_deg", "limb_ls_abs_error_deg"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def to_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value == "":
        return math.nan
    return float(value)


def angle_diff(estimated: float, standard: float) -> float:
    """Return signed angular difference in [-180, 180)."""
    return (estimated - standard + 180) % 360 - 180


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return math.nan
    values = sorted(values)
    idx = (len(values) - 1) * pct / 100
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return values[int(idx)]
    return values[lo] * (hi - idx) + values[hi] * (idx - lo)


def rmse(values: list[float]) -> float:
    return math.sqrt(mean([value * value for value in values])) if values else math.nan


def axis_bin(axis: float) -> str:
    if axis < 0:
        return "negative"
    if axis < 30:
        return "0_to_30"
    if axis < 60:
        return "30_to_60"
    if axis <= 90:
        return "60_to_90"
    return "greater_than_90"


def clinical_axis_group(axis: float) -> str:
    if axis < -30:
        return "left_axis_deviation"
    if axis <= 90:
        return "normal_or_borderline"
    return "right_axis_deviation"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def enrich_rows(result_rows: list[dict[str, str]], header_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    header_by_patient = {int(row["patient_id"]): row for row in header_rows}
    enriched: list[dict[str, object]] = []

    for row in result_rows:
        patient_id = int(row["patient_id"])
        standard = to_float(row, "standard_axis_deg")
        if not math.isfinite(standard):
            continue
        area_i = to_float(row, "area_i")
        area_avf = to_float(row, "area_avf")
        area_ii = to_float(row, "area_ii")
        limb_vector_mag = math.sqrt(area_i * area_i + area_avf * area_avf)
        frontal_area_sum = sum(abs(to_float(row, key)) for key in ["area_i", "area_ii", "area_iii", "area_avr", "area_avl", "area_avf"])
        header = header_by_patient.get(patient_id, {})

        enriched.append(
            {
                **row,
                "patient_id": patient_id,
                "standard_axis_deg": standard,
                "area_i": area_i,
                "area_ii": area_ii,
                "area_avf": area_avf,
                "qrs_ms": header.get("qrs_ms", ""),
                "axis_bin": axis_bin(standard),
                "clinical_axis_group": clinical_axis_group(standard),
                "limb_vector_mag_i_avf": limb_vector_mag,
                "frontal_area_sum": frontal_area_sum,
                "low_abs_area_i": abs(area_i) < 15,
                "low_abs_area_avf": abs(area_avf) < 10,
                "direct_limb_ls_disagreement_deg": abs(
                    angle_diff(to_float(row, "direct_axis_deg"), to_float(row, "limb_ls_axis_deg"))
                ),
            }
        )

    vector_cutoff = percentile([float(row["limb_vector_mag_i_avf"]) for row in enriched], 25)
    for row in enriched:
        row["low_i_avf_vector_mag"] = float(row["limb_vector_mag_i_avf"]) <= vector_cutoff
        row["direct_limb_ls_disagree_gt30"] = float(row["direct_limb_ls_disagreement_deg"]) > 30

    return enriched


def method_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for method_name, estimate_col, error_col in METHODS:
        errors = [float(row[error_col]) for row in rows]
        signed = [angle_diff(float(row[estimate_col]), float(row["standard_axis_deg"])) for row in rows]
        worst = max(rows, key=lambda row: float(row[error_col]))
        best = min(rows, key=lambda row: float(row[error_col]))
        summaries.append(
            {
                "method": method_name,
                "n": len(errors),
                "mae_deg": mean(errors),
                "median_abs_error_deg": median(errors),
                "rmse_deg": rmse(errors),
                "p90_abs_error_deg": percentile(errors, 90),
                "max_abs_error_deg": max(errors),
                "mean_signed_error_deg": mean(signed),
                "within_15_deg_fraction": mean([err <= 15 for err in errors]),
                "within_30_deg_fraction": mean([err <= 30 for err in errors]),
                "best_patient_id": best["patient_id"],
                "best_abs_error_deg": float(best[error_col]),
                "worst_patient_id": worst["patient_id"],
                "worst_abs_error_deg": float(worst[error_col]),
            }
        )
    return summaries


def group_summary(rows: list[dict[str, object]], group_col: str) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        for method_name, _estimate_col, error_col in METHODS:
            grouped[(method_name, str(row[group_col]))].append({**row, "_error": float(row[error_col])})

    out: list[dict[str, object]] = []
    for (method_name, group), items in sorted(grouped.items()):
        errors = [float(item["_error"]) for item in items]
        out.append(
            {
                "group_type": group_col,
                "group": group,
                "method": method_name,
                "n": len(errors),
                "mae_deg": mean(errors),
                "median_abs_error_deg": median(errors),
                "within_30_deg_fraction": mean([err <= 30 for err in errors]),
            }
        )
    return out


def flag_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    flags = [
        "low_abs_area_i",
        "low_abs_area_avf",
        "low_i_avf_vector_mag",
        "direct_limb_ls_disagree_gt30",
    ]
    out: list[dict[str, object]] = []
    for flag in flags:
        flagged = [row for row in rows if row[flag]]
        unflagged = [row for row in rows if not row[flag]]
        for method_name, _estimate_col, error_col in METHODS:
            flagged_errors = [float(row[error_col]) for row in flagged]
            unflagged_errors = [float(row[error_col]) for row in unflagged]
            out.append(
                {
                    "flag": flag,
                    "method": method_name,
                    "flagged_n": len(flagged_errors),
                    "flagged_mae_deg": mean(flagged_errors) if flagged_errors else math.nan,
                    "unflagged_n": len(unflagged_errors),
                    "unflagged_mae_deg": mean(unflagged_errors) if unflagged_errors else math.nan,
                    "mae_delta_flagged_minus_unflagged": (
                        mean(flagged_errors) - mean(unflagged_errors)
                        if flagged_errors and unflagged_errors
                        else math.nan
                    ),
                }
            )
    return out


def worst_cases(rows: list[dict[str, object]], top_n: int) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for method_name, estimate_col, error_col in METHODS:
        ordered = sorted(rows, key=lambda row: float(row[error_col]), reverse=True)[:top_n]
        for rank, row in enumerate(ordered, start=1):
            out.append(
                {
                    "method": method_name,
                    "rank": rank,
                    "patient_id": row["patient_id"],
                    "image": row["image"],
                    "standard_axis_deg": row["standard_axis_deg"],
                    "estimated_axis_deg": row[estimate_col],
                    "abs_error_deg": row[error_col],
                    "qrs_ms": row["qrs_ms"],
                    "axis_bin": row["axis_bin"],
                    "clinical_axis_group": row["clinical_axis_group"],
                    "area_i": row["area_i"],
                    "area_avf": row["area_avf"],
                    "limb_vector_mag_i_avf": row["limb_vector_mag_i_avf"],
                    "low_abs_area_i": row["low_abs_area_i"],
                    "low_abs_area_avf": row["low_abs_area_avf"],
                    "low_i_avf_vector_mag": row["low_i_avf_vector_mag"],
                    "direct_limb_ls_disagreement_deg": row["direct_limb_ls_disagreement_deg"],
                }
            )
    return out


def write_markdown_report(
    path: Path,
    summaries: list[dict[str, object]],
    flag_rows: list[dict[str, object]],
    worst_rows: list[dict[str, object]],
) -> None:
    best_method = min(summaries, key=lambda row: float(row["mae_deg"]))
    lines = [
        "# QRS Axis Error Analysis",
        "",
        "## Overall",
        "",
        "| method | N | MAE | median | RMSE | P90 | within 30 deg | worst PT |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            "| {method} | {n} | {mae_deg:.1f} | {median_abs_error_deg:.1f} | {rmse_deg:.1f} | "
            "{p90_abs_error_deg:.1f} | {within_30_deg_fraction:.1%} | PT{worst_patient_id} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Main Takeaway",
            "",
            f"The lowest MAE is from `{best_method['method']}` "
            f"({float(best_method['mae_deg']):.1f} deg), but the P90 error is still "
            f"{float(best_method['p90_abs_error_deg']):.1f} deg. This supports using the "
            "net-area approach as a rough directional signal, not as a replacement for the header QRS axis.",
            "",
            "## Failure Flags",
            "",
            "| flag | method | flagged N | flagged MAE | unflagged MAE | delta |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in flag_rows:
        lines.append(
            "| {flag} | {method} | {flagged_n} | {flagged_mae_deg:.1f} | "
            "{unflagged_mae_deg:.1f} | {mae_delta_flagged_minus_unflagged:.1f} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Worst Cases",
            "",
            "| method | rank | PT | standard | estimate | abs error | low I | low aVF | low vector |",
            "|---|---:|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for row in worst_rows:
        lines.append(
            "| {method} | {rank} | PT{patient_id} | {standard_axis_deg:.1f} | {estimated_axis_deg} | "
            "{abs_error_deg} | {low_abs_area_i} | {low_abs_area_avf} | {low_i_avf_vector_mag} |".format(
                **row
            )
        )

    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-csv",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs" / "non_paced_qrs_axis_results_from_extracted_header.csv",
    )
    parser.add_argument(
        "--header-csv",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs" / "non_paced_header_extracted.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs" / "error_analysis",
    )
    parser.add_argument("--top-n", type=int, default=8)
    args = parser.parse_args()

    result_rows = read_csv(args.results_csv)
    header_rows = read_csv(args.header_csv)
    rows = enrich_rows(result_rows, header_rows)

    summaries = method_summary(rows)
    group_rows = group_summary(rows, "axis_bin") + group_summary(rows, "clinical_axis_group")
    flag_rows = flag_summary(rows)
    worst_rows = worst_cases(rows, args.top_n)

    write_csv(args.output_dir / "method_summary.csv", summaries)
    write_csv(args.output_dir / "group_summary.csv", group_rows)
    write_csv(args.output_dir / "flag_summary.csv", flag_rows)
    write_csv(args.output_dir / "worst_cases.csv", worst_rows)
    write_csv(args.output_dir / "per_case_error_features.csv", rows)
    write_markdown_report(args.output_dir / "error_analysis_report.md", summaries, flag_rows, worst_rows)

    for row in summaries:
        print(
            "{method}: MAE={mae_deg:.1f} deg, median={median_abs_error_deg:.1f} deg, "
            "P90={p90_abs_error_deg:.1f} deg, worst=PT{worst_patient_id}".format(**row)
        )
    print(f"Wrote {args.output_dir}")


if __name__ == "__main__":
    main()
