#!/usr/bin/env python3
"""Estimate frontal QRS axis from non-paced ECG screenshots.

This script digitizes the limb-lead waveforms from the fixed-format JPG ECG
screenshots, integrates baseline-corrected QRS windows, and compares net-area
axis estimates against the machine-reported QRS axis in the report header.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


LEADS = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
LIMB_LEAD_ANGLES_DEG = np.array([0.0, 60.0, 120.0, -150.0, -30.0, 90.0])

# QRS axis from the report header "PRT Axis"; the second value is QRS axis.
# These are the PT7-PT45 non-paced ECGs named in the request.
STANDARD_QRS_AXIS_DEG = {
    7: 8,
    8: 76,
    9: 33,
    10: 20,
    11: 23,
    12: 7,
    13: -5,
    14: 50,
    15: 66,
    16: 26,
    17: -24,
    18: 43,
    19: 47,
    20: 3,
    21: 73,
    22: 39,
    23: 46,
    24: -2,
    25: -3,
    26: 23,
    27: 52,
    28: 18,
    29: 53,
    30: 31,
    31: 28,
    32: 19,
    33: 47,
    34: 68,
    35: 59,
    36: 69,
    37: 84,
    38: 29,
    39: 1,
    40: 35,
    41: 49,
    42: 67,
    43: 15,
    44: 68,
    45: 50,
}


@dataclass(frozen=True)
class AxisResult:
    patient_id: int
    image: str
    standard_axis_deg: float
    direct_axis_deg: float
    direct_abs_error_deg: float
    lead_i_ii_axis_deg: float
    lead_i_ii_abs_error_deg: float
    limb_ls_axis_deg: float
    limb_ls_abs_error_deg: float
    beats_used: int
    peaks_detected: int
    area_i: float
    area_ii: float
    area_iii: float
    area_avr: float
    area_avl: float
    area_avf: float


def angle180(deg: float) -> float:
    """Wrap an angle to (-180, 180]."""
    while deg > 180:
        deg -= 360
    while deg <= -180:
        deg += 360
    return deg


def angular_error(estimated: float, standard: float) -> float:
    return abs(angle180(estimated - standard))


def load_dark_mask(image_path: Path) -> tuple[Image.Image, np.ndarray, np.ndarray]:
    image = Image.open(image_path).convert("RGB")
    arr = np.asarray(image)
    # The waveform and labels are black/gray; the grid is pink/red and remains
    # above this RGB threshold.
    dark_mask = (arr[:, :, 0] < 120) & (arr[:, :, 1] < 120) & (arr[:, :, 2] < 120)
    return image, arr, dark_mask


def lead_centers(height: int) -> list[float]:
    # These ECG screenshots are 880 px high with the ECG panel starting near
    # y=164 and row centers every 60 px. Keep a proportional fallback for any
    # nearby export size.
    if abs(height - 880) <= 5:
        return [194 + 60 * i for i in range(12)]
    pitch = (height - 164) / 12
    return [164 + pitch * (i + 0.5) for i in range(12)]


def extract_trace(mask: np.ndarray, row: int, x0: int, x1: int, centers: list[float]) -> np.ndarray:
    height = mask.shape[0]
    cy = centers[row]
    y0 = max(0, int(cy - 27))
    y1 = min(height, int(cy + 28))
    sub = mask[y0:y1, x0:x1]

    y_trace = np.full(x1 - x0, np.nan, dtype=float)
    for xi in range(sub.shape[1]):
        ys = np.flatnonzero(sub[:, xi])
        if len(ys):
            y_trace[xi] = float(np.median(ys) + y0)

    good = np.isfinite(y_trace)
    if good.sum() < 100:
        raise RuntimeError(f"Too few waveform pixels found for lead {LEADS[row]}")

    idx = np.arange(len(y_trace))
    y_trace = np.interp(idx, idx[good], y_trace[good])
    signal = np.median(y_trace) - y_trace
    return np.convolve(signal, np.ones(3) / 3, mode="same")


def detect_qrs_peaks(signal_energy: np.ndarray) -> list[int]:
    energy = np.abs(signal_energy - np.median(signal_energy))
    energy = np.convolve(energy, np.ones(5) / 5, mode="same")
    threshold = max(np.percentile(energy, 94), np.median(energy) + 1.2 * np.std(energy))

    peaks: list[int] = []
    min_distance_px = 45
    for i in range(12, len(energy) - 12):
        if energy[i] <= threshold or energy[i] < energy[i - 1] or energy[i] < energy[i + 1]:
            continue
        if peaks and i - peaks[-1] < min_distance_px:
            if energy[i] > energy[peaks[-1]]:
                peaks[-1] = i
        else:
            peaks.append(i)
    return peaks


def qrs_net_areas(signals: list[np.ndarray], peaks: list[int]) -> np.ndarray:
    beat_areas: list[list[float]] = []
    strip_len = len(signals[0])

    for peak in peaks:
        if peak < 55 or peak > strip_len - 60:
            continue

        areas_for_beat = []
        for signal in signals[:6]:
            baseline = np.median(
                np.r_[
                    signal[peak - 48 : peak - 22],
                    signal[peak + 25 : peak + 52],
                ]
            )
            # 26 px is about 208 ms at 25 mm/s and this export scale; it captures
            # QRS for these non-paced examples without including much ST/T area.
            areas_for_beat.append(float(np.sum(signal[peak - 10 : peak + 16] - baseline)))

        beat_areas.append(areas_for_beat)

    if not beat_areas:
        raise RuntimeError("No usable QRS windows after edge trimming")

    return np.asarray(beat_areas, dtype=float)


def axis_from_i_avf(area_i: float, area_avf: float) -> float:
    return angle180(math.degrees(math.atan2(area_avf, area_i)))


def axis_from_i_ii(area_i: float, area_ii: float) -> float:
    area_avf = (area_ii - 0.5 * area_i) / math.sin(math.radians(60))
    return axis_from_i_avf(area_i, area_avf)


def axis_from_limb_least_squares(limb_areas: np.ndarray) -> float:
    lead_angles = np.deg2rad(LIMB_LEAD_ANGLES_DEG)
    matrix = np.column_stack([np.cos(lead_angles), np.sin(lead_angles)])
    x_component, y_component = np.linalg.lstsq(matrix, limb_areas, rcond=None)[0]
    return angle180(math.degrees(math.atan2(y_component, x_component)))


def estimate_image(
    image_path: Path,
    patient_id: int,
    standard_axis_deg: float | None = None,
) -> tuple[AxisResult, list[int], list[float], int, int]:
    image, arr, dark_mask = load_dark_mask(image_path)
    height, width = arr.shape[:2]
    x0, x1 = 66, width - 8
    centers = lead_centers(height)

    signals = [extract_trace(dark_mask, row, x0, x1, centers) for row in range(12)]
    timing_candidates = [signals[i] for i in (1, 0, 10, 11)]
    energy = np.median(
        np.vstack([np.abs(candidate - np.median(candidate)) for candidate in timing_candidates]),
        axis=0,
    )
    peaks = detect_qrs_peaks(energy)
    beat_areas = qrs_net_areas(signals, peaks)
    limb_areas = np.median(beat_areas, axis=0)

    if standard_axis_deg is None:
        standard_axis_deg = STANDARD_QRS_AXIS_DEG[patient_id]
    standard = float(standard_axis_deg)
    direct = axis_from_i_avf(limb_areas[0], limb_areas[5])
    lead_i_ii = axis_from_i_ii(limb_areas[0], limb_areas[1])
    limb_ls = axis_from_limb_least_squares(limb_areas)

    return (
        AxisResult(
            patient_id=patient_id,
            image=image_path.name,
            standard_axis_deg=standard,
            direct_axis_deg=direct,
            direct_abs_error_deg=angular_error(direct, standard),
            lead_i_ii_axis_deg=lead_i_ii,
            lead_i_ii_abs_error_deg=angular_error(lead_i_ii, standard),
            limb_ls_axis_deg=limb_ls,
            limb_ls_abs_error_deg=angular_error(limb_ls, standard),
            beats_used=len(beat_areas),
            peaks_detected=len(peaks),
            area_i=limb_areas[0],
            area_ii=limb_areas[1],
            area_iii=limb_areas[2],
            area_avr=limb_areas[3],
            area_avl=limb_areas[4],
            area_avf=limb_areas[5],
        ),
        peaks,
        centers,
        x0,
        x1,
    )


def write_debug_overlay(image_path: Path, output_path: Path, peaks: list[int], centers: list[float], x0: int, x1: int) -> None:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    for center in centers:
        draw.line([(x0, center), (x1, center)], fill=(0, 128, 255), width=1)
    for peak in peaks:
        draw.line([(x0 + peak, 160), (x0 + peak, image.height - 5)], fill=(0, 180, 0), width=1)
    image.save(output_path)


def summarize(results: list[AxisResult], field: str) -> dict[str, float]:
    errors = np.asarray([getattr(result, field) for result in results], dtype=float)
    errors = errors[np.isfinite(errors)]
    if len(errors) == 0:
        return {
            "n": 0.0,
            "mae_deg": math.nan,
            "median_abs_error_deg": math.nan,
            "within_15_deg_fraction": math.nan,
            "within_30_deg_fraction": math.nan,
        }
    return {
        "n": float(len(errors)),
        "mae_deg": float(np.mean(errors)),
        "median_abs_error_deg": float(np.median(errors)),
        "within_15_deg_fraction": float(np.mean(errors <= 15)),
        "within_30_deg_fraction": float(np.mean(errors <= 30)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path("/Users/yaweizhang/Downloads/No Pacemaker"),
        help="Directory containing EKGE-NP-PT*.jpg files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs",
        help="Directory for CSV outputs and optional debug overlays.",
    )
    parser.add_argument("--debug-overlays", action="store_true", help="Save row-center and QRS-peak overlay images.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = args.output_dir / "debug_overlays"
    if args.debug_overlays:
        debug_dir.mkdir(parents=True, exist_ok=True)

    results: list[AxisResult] = []
    for patient_id in sorted(STANDARD_QRS_AXIS_DEG):
        image_path = args.image_dir / f"EKGE-NP-PT{patient_id}.jpg"
        result, peaks, centers, x0, x1 = estimate_image(image_path, patient_id)
        results.append(result)

        if args.debug_overlays:
            write_debug_overlay(
                image_path,
                debug_dir / f"EKGE-NP-PT{patient_id}-overlay.jpg",
                peaks,
                centers,
                x0,
                x1,
            )

    rows = [result.__dict__ for result in results]
    results_path = args.output_dir / "non_paced_qrs_axis_results.csv"
    with results_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summaries = [
        {"method": "direct_i_avf", **summarize(results, "direct_abs_error_deg")},
        {"method": "lead_i_ii_reconstructed_avf", **summarize(results, "lead_i_ii_abs_error_deg")},
        {"method": "limb_lead_least_squares", **summarize(results, "limb_ls_abs_error_deg")},
    ]
    summary_path = args.output_dir / "non_paced_qrs_axis_summary.csv"
    with summary_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        writer.writeheader()
        writer.writerows(summaries)

    for summary in summaries:
        print(
            "{method}: N={n:.0f}, MAE={mae_deg:.1f} deg, median={median_abs_error_deg:.1f} deg, "
            "<=15 deg={within_15_deg_fraction:.1%}, <=30 deg={within_30_deg_fraction:.1%}".format(
                **summary
            )
        )
    print(f"Wrote {results_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
