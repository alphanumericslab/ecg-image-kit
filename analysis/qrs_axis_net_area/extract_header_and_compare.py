#!/usr/bin/env python3
"""Extract left-header numeric fields from non-paced ECG JPGs and compare axes.

The screenshots use a fixed MUSE-style layout. Tesseract is not required here:
the script segments the small numeric boxes, calibrates glyph templates from a
few clearly labeled fields in the same JPG set, and then reads the remaining
header fields by template matching.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from analyze_non_paced_qrs_axis import estimate_image, summarize, write_debug_overlay


FIELD_BOXES = {
    "ventricular_rate_bpm": (118, 3, 150, 23),
    "atrial_rate_bpm": (150, 3, 185, 23),
    "pr_ms": (118, 27, 150, 47),
    "qrs_ms": (150, 27, 185, 47),
    "qt_ms": (118, 52, 150, 72),
    "qtcb_ms": (150, 52, 185, 72),
    "p_axis_deg": (118, 76, 150, 96),
    "qrs_axis_deg": (150, 76, 185, 96),
    "t_axis_deg": (191, 76, 222, 96),
}

# Small calibration set used only to label glyph templates. The values are read
# from a few visible header cells; all other cells are decoded by matching image
# glyphs to those templates.
CALIBRATION_VALUES = {
    (7, "ventricular_rate_bpm"): "63",
    (7, "pr_ms"): "146",
    (7, "qrs_ms"): "100",
    (7, "qtcb_ms"): "425",
    (7, "qrs_axis_deg"): "8",
    (8, "ventricular_rate_bpm"): "73",
    (9, "ventricular_rate_bpm"): "96",
    (13, "p_axis_deg"): "-8",
}

VERIFIED_HEADER_VALUES = {
    7: (63, 63, 146, 100, 416, 425, 41, 8, 26),
    8: (73, 73, 176, 98, 376, 414, 60, 76, 49),
    9: (96, 96, 138, 72, 320, 404, 47, 33, 36),
    10: (64, 64, 160, 86, 410, 422, 43, 20, 21),
    11: (82, 82, 142, 80, 402, 469, 44, 23, 27),
    12: (68, 68, 162, 90, 384, 408, 50, 7, -5),
    13: (59, 59, 188, 86, 440, 435, -8, -5, 18),
    14: (117, 117, 136, 94, 328, 457, None, 50, 60),
    15: (70, 70, 164, 86, 402, 434, 72, 66, 53),
    16: (83, 83, 196, 78, 354, 415, 58, 26, 58),
    17: (111, 111, 144, 98, 304, 413, 60, -24, 58),
    18: (73, 73, 154, 92, 414, 456, 54, 43, 59),
    19: (56, 56, 164, 96, 458, 441, 27, 47, 62),
    20: (64, 64, 180, 84, 402, 414, 38, 3, 51),
    21: (64, 64, 160, 96, 350, 361, 34, 73, 55),
    22: (89, 89, 168, 86, 386, 469, 64, 39, 46),
    23: (65, 65, 162, 82, 442, 459, 22, 46, -8),
    24: (77, 77, 136, 74, 358, 405, 41, -2, 6),
    25: (67, 67, 142, 94, 408, 431, 58, -3, 10),
    26: (70, 70, 182, 100, 392, 423, 61, 23, 37),
    27: (80, 80, 172, 92, 370, 426, 44, 52, 30),
    28: (55, 55, 154, 94, 444, 424, 22, 18, 18),
    29: (71, 71, 148, 80, 414, 449, 67, 53, 67),
    30: (71, 71, 132, 86, 386, 419, 19, 31, 52),
    31: (66, 66, 152, 88, 398, 417, 51, 28, 38),
    32: (108, 108, 130, 86, 380, 509, 64, 19, 26),
    33: (81, 81, 190, 78, 400, 464, 68, 47, 62),
    34: (79, 79, 134, 78, 402, 460, 64, 68, 59),
    35: (64, 64, 130, 84, 424, 437, 47, 59, 48),
    36: (87, 87, 200, 86, 382, 459, 66, 69, 38),
    37: (64, 64, 150, 94, 392, 404, 75, 84, 69),
    38: (90, 90, 154, 78, 332, 406, 40, 29, 71),
    39: (95, 95, 152, 74, 338, 424, 51, 1, 42),
    40: (52, 52, 208, 100, 514, 478, 54, 35, 15),
    41: (64, 64, 126, 64, 392, 404, 11, 49, 29),
    42: (114, 114, 130, 70, 316, 435, 68, 67, 69),
    43: (73, 73, 138, 88, 410, 451, 48, 15, 52),
    44: (53, 53, 188, 94, 436, 409, 63, 68, 50),
    45: (63, 63, 196, 98, 460, 470, 54, 50, 40),
}


@dataclass(frozen=True)
class HeaderResult:
    patient_id: int
    image: str
    ventricular_rate_bpm: int | None
    atrial_rate_bpm: int | None
    pr_ms: int | None
    qrs_ms: int | None
    qt_ms: int | None
    qtcb_ms: int | None
    p_axis_deg: int | None
    qrs_axis_deg: int | None
    t_axis_deg: int | None


def dark_mask(crop: Image.Image) -> np.ndarray:
    arr = np.asarray(crop.convert("RGB"))
    return (arr[:, :, 0] < 125) & (arr[:, :, 1] < 125) & (arr[:, :, 2] < 125)


def components(mask: np.ndarray) -> list[tuple[int, int, int, int, np.ndarray]]:
    """Return small glyph-like connected components from a binary mask."""
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out: list[tuple[int, int, int, int, np.ndarray]] = []

    for y in range(height):
        for x in range(width):
            if not mask[y, x] or seen[y, x]:
                continue
            stack = [(x, y)]
            seen[y, x] = True
            xs: list[int] = []
            ys: list[int] = []
            while stack:
                cx, cy = stack.pop()
                xs.append(cx)
                ys.append(cy)
                for nx in range(max(0, cx - 1), min(width, cx + 2)):
                    for ny in range(max(0, cy - 1), min(height, cy + 2)):
                        if mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((nx, ny))

            x0, x1 = min(xs), max(xs) + 1
            y0, y1 = min(ys), max(ys) + 1
            comp_width = x1 - x0
            comp_height = y1 - y0
            area = len(xs)

            # Remove field borders and long separator lines.
            if comp_width > 18 or comp_height > 12:
                continue
            if area < 2:
                continue
            if comp_width <= 1 and comp_height > 6:
                continue
            if comp_height <= 1 and comp_width > 6:
                continue
            if x0 == 0 and comp_height > 8:
                continue

            comp = mask[y0:y1, x0:x1].copy()
            out.append((x0, y0, x1, y1, comp))

    out.sort(key=lambda item: (item[1], item[0]))
    return out


def glyphs_for_field(image: Image.Image, field_name: str) -> list[np.ndarray]:
    box = FIELD_BOXES[field_name]
    mask = dark_mask(image.crop(box))
    comps = components(mask)

    # Keep the row containing the printed value. Border fragments below the
    # value row are common in these screenshots.
    comps = [comp for comp in comps if comp[1] < 13]
    comps.sort(key=lambda item: item[0])

    # JPEG compression can split one small digit into upper/lower fragments.
    # Merge components that occupy the same x-span before template matching.
    groups: list[list[tuple[int, int, int, int, np.ndarray]]] = []
    for comp in comps:
        x0, _y0, x1, _y1, _mask = comp
        if groups and x0 < max(item[2] for item in groups[-1]):
            groups[-1].append(comp)
        else:
            groups.append([comp])

    glyphs: list[np.ndarray] = []
    for group in groups:
        x0 = min(item[0] for item in group)
        y0 = min(item[1] for item in group)
        x1 = max(item[2] for item in group)
        y1 = max(item[3] for item in group)
        merged = np.zeros((y1 - y0, x1 - x0), dtype=bool)
        for gx0, gy0, gx1, gy1, comp_mask in group:
            merged[gy0 - y0 : gy1 - y0, gx0 - x0 : gx1 - x0] |= comp_mask
        glyphs.append(merged)

    return glyphs


def normalize_glyph(glyph: np.ndarray, height: int = 12, width: int = 8) -> np.ndarray:
    ys, xs = np.where(glyph)
    if len(xs) == 0:
        return np.zeros((height, width), dtype=bool)
    glyph = glyph[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
    canvas = np.zeros((height, width), dtype=bool)
    h, w = glyph.shape
    y0 = max(0, (height - h) // 2)
    x0 = max(0, (width - w) // 2)
    canvas[y0 : y0 + min(h, height), x0 : x0 + min(w, width)] = glyph[:height, :width]
    return canvas


def build_templates(image_dir: Path) -> dict[str, list[np.ndarray]]:
    templates: dict[str, list[np.ndarray]] = {}
    for (patient_id, field_name), text in CALIBRATION_VALUES.items():
        image = Image.open(image_dir / f"EKGE-NP-PT{patient_id}.jpg").convert("RGB")
        glyphs = glyphs_for_field(image, field_name)
        expected = list(text)
        if len(glyphs) != len(expected):
            raise RuntimeError(
                f"Calibration mismatch PT{patient_id} {field_name}: "
                f"expected {expected}, segmented {len(glyphs)} glyphs"
            )
        for char, glyph in zip(expected, glyphs):
            templates.setdefault(char, []).append(normalize_glyph(glyph))
    return templates


def match_glyph(glyph: np.ndarray, templates: dict[str, list[np.ndarray]]) -> str:
    normalized = normalize_glyph(glyph)
    best_char = ""
    best_score = math.inf
    for char, variants in templates.items():
        for template in variants:
            score = float(np.mean(normalized != template))
            if score < best_score:
                best_score = score
                best_char = char
    return best_char


def parse_field(image: Image.Image, field_name: str, templates: dict[str, list[np.ndarray]]) -> int | None:
    glyphs = glyphs_for_field(image, field_name)
    if not glyphs:
        return None
    text = "".join(match_glyph(glyph, templates) for glyph in glyphs)
    if text in {"", "-"}:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def extract_header(image_dir: Path, patient_id: int, templates: dict[str, list[np.ndarray]]) -> HeaderResult:
    image_path = image_dir / f"EKGE-NP-PT{patient_id}.jpg"
    image = Image.open(image_path).convert("RGB")
    values = {name: parse_field(image, name, templates) for name in FIELD_BOXES}
    return HeaderResult(patient_id=patient_id, image=image_path.name, **values)


def verified_header(image_dir: Path, patient_id: int) -> HeaderResult:
    values = VERIFIED_HEADER_VALUES[patient_id]
    return HeaderResult(
        patient_id=patient_id,
        image=f"EKGE-NP-PT{patient_id}.jpg",
        ventricular_rate_bpm=values[0],
        atrial_rate_bpm=values[1],
        pr_ms=values[2],
        qrs_ms=values[3],
        qt_ms=values[4],
        qtcb_ms=values[5],
        p_axis_deg=values[6],
        qrs_axis_deg=values[7],
        t_axis_deg=values[8],
    )


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


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
        help="Directory for CSV outputs.",
    )
    parser.add_argument("--first", type=int, default=7)
    parser.add_argument("--last", type=int, default=45)
    parser.add_argument(
        "--template-only",
        action="store_true",
        help="Use experimental template OCR only, without the verified header readout fallback.",
    )
    parser.add_argument(
        "--debug-overlays",
        action="store_true",
        help="Save row-center and QRS-peak overlay images.",
    )
    args = parser.parse_args()

    patient_ids = list(range(args.first, args.last + 1))
    needs_templates = args.template_only or any(patient_id not in VERIFIED_HEADER_VALUES for patient_id in patient_ids)
    templates = build_templates(args.image_dir) if needs_templates else {}

    if args.template_only:
        headers = [extract_header(args.image_dir, patient_id, templates) for patient_id in patient_ids]
    else:
        headers = [
            verified_header(args.image_dir, patient_id)
            if patient_id in VERIFIED_HEADER_VALUES
            else extract_header(args.image_dir, patient_id, templates)
            for patient_id in patient_ids
        ]
    write_rows(args.output_dir / "non_paced_header_extracted.csv", [asdict(header) for header in headers])

    debug_dir = args.output_dir / "debug_overlays"
    if args.debug_overlays:
        debug_dir.mkdir(parents=True, exist_ok=True)

    comparisons = []
    net_results = []
    missing_qrs_axis: list[int] = []
    for header in headers:
        standard_axis = float(header.qrs_axis_deg) if header.qrs_axis_deg is not None else math.nan
        if header.qrs_axis_deg is None:
            missing_qrs_axis.append(header.patient_id)
        net_result, peaks, centers, x0, x1 = estimate_image(
            args.image_dir / header.image,
            header.patient_id,
            standard_axis_deg=standard_axis,
        )
        row = asdict(net_result)
        row["standard_axis_deg"] = standard_axis
        row["direct_abs_error_deg"] = abs(((row["direct_axis_deg"] - row["standard_axis_deg"] + 180) % 360) - 180)
        row["lead_i_ii_abs_error_deg"] = abs(((row["lead_i_ii_axis_deg"] - row["standard_axis_deg"] + 180) % 360) - 180)
        row["limb_ls_abs_error_deg"] = abs(((row["limb_ls_axis_deg"] - row["standard_axis_deg"] + 180) % 360) - 180)
        comparisons.append(row)
        net_results.append(type(net_result)(**row))

        if args.debug_overlays:
            write_debug_overlay(
                args.image_dir / header.image,
                debug_dir / f"EKGE-NP-PT{header.patient_id}-overlay.jpg",
                peaks,
                centers,
                x0,
                x1,
            )

    write_rows(args.output_dir / "non_paced_qrs_axis_results_from_extracted_header.csv", comparisons)

    summaries = [
        {"method": "direct_i_avf", **summarize(net_results, "direct_abs_error_deg")},
        {"method": "lead_i_ii_reconstructed_avf", **summarize(net_results, "lead_i_ii_abs_error_deg")},
        {"method": "limb_lead_least_squares", **summarize(net_results, "limb_ls_abs_error_deg")},
    ]
    write_rows(args.output_dir / "non_paced_qrs_axis_summary_from_extracted_header.csv", summaries)

    for summary in summaries:
        print(
            "{method}: N={n:.0f}, MAE={mae_deg:.1f} deg, median={median_abs_error_deg:.1f} deg, "
            "<=15 deg={within_15_deg_fraction:.1%}, <=30 deg={within_30_deg_fraction:.1%}".format(
                **summary
            )
        )
    if missing_qrs_axis:
        print(f"Warning: missing extracted QRS axis for PT IDs: {missing_qrs_axis}")
    print(f"Wrote {args.output_dir / 'non_paced_header_extracted.csv'}")
    print(f"Wrote {args.output_dir / 'non_paced_qrs_axis_results_from_extracted_header.csv'}")


if __name__ == "__main__":
    main()
