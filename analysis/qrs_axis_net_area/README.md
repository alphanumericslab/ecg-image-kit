# Non-paced QRS axis net-area check

This folder tests whether QRS net area from non-paced ECG screenshots can
approximate the report-header QRS axis.

## Method

1. Use PT7-PT45 from `/Users/yaweizhang/Downloads/No Pacemaker`.
2. Treat the second `PRT Axis` value in each ECG header as the standard QRS axis.
3. Extract each lead row from the fixed screenshot layout.
4. Detect QRS timing from combined limb/precordial waveform energy.
5. Integrate baseline-corrected QRS windows for the six limb leads.
6. Compare three net-area estimates:
   - `direct_i_avf`: `atan2(area_aVF, area_I)`
   - `lead_i_ii_reconstructed_avf`: reconstruct aVF from I and II, then `atan2`
   - `limb_lead_least_squares`: fit a frontal-plane vector to all six limb-lead areas

## Run

```bash
/Users/yaweizhang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  analysis/qrs_axis_net_area/analyze_non_paced_qrs_axis.py
```

Optional debug overlays:

```bash
/Users/yaweizhang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  analysis/qrs_axis_net_area/analyze_non_paced_qrs_axis.py --debug-overlays
```

## Current result

On PT7-PT45, the direct I/aVF net-area estimate is only a coarse approximation:

| method | N | MAE | median absolute error | within 15 deg | within 30 deg |
|---|---:|---:|---:|---:|---:|
| direct_i_avf | 39 | 31.7 deg | 24.9 deg | 38.5% | 53.8% |
| lead_i_ii_reconstructed_avf | 39 | 32.3 deg | 20.7 deg | 43.6% | 59.0% |
| limb_lead_least_squares | 39 | 28.1 deg | 16.6 deg | 46.2% | 59.0% |

Interpretation: QRS net area from screenshots carries useful directional signal,
but the simple `atan2(area_aVF, area_I)` method is not accurate enough to replace
the standard axis on this image-only dataset. The all-limb-lead least-squares
variant is somewhat more stable, especially when lead I or aVF has low amplitude
or a noisy extracted trace.

## Header extraction

`extract_header_and_compare.py` writes the fixed-layout left-header readout to:

```text
outputs/non_paced_header_extracted.csv
```

It then uses the extracted `qrs_axis_deg` column as the comparison target and
writes:

```text
outputs/non_paced_qrs_axis_results_from_extracted_header.csv
outputs/non_paced_qrs_axis_summary_from_extracted_header.csv
```

The default path uses a verified header readout table because the JPG header
font is very small and template-only OCR can misread values such as `76` as
`-8`. The experimental fixed-coordinate template OCR can still be run with:

```bash
/Users/yaweizhang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  analysis/qrs_axis_net_area/extract_header_and_compare.py --template-only
```

For the expanded `EKGE-NP-PT*.jpg` set, pass the image range and write to a
separate output directory:

```bash
/Users/yaweizhang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  analysis/qrs_axis_net_area/extract_header_and_compare.py \
  --image-dir "/Users/yaweizhang/Downloads/No Pacemaker" \
  --first 1 \
  --last 100 \
  --output-dir analysis/qrs_axis_net_area/outputs/pt1_100
```

PT7-PT45 use the verified header table. Other PT IDs use the template OCR
fallback; if QRS axis cannot be read, the script still writes waveform-based
axis estimates and leaves error fields as `nan`.

## Error analysis

Run:

```bash
/Users/yaweizhang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  analysis/qrs_axis_net_area/error_analysis.py
```

For the expanded output directory:

```bash
/Users/yaweizhang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  analysis/qrs_axis_net_area/error_analysis.py \
  --results-csv analysis/qrs_axis_net_area/outputs/pt1_100/non_paced_qrs_axis_results_from_extracted_header.csv \
  --header-csv analysis/qrs_axis_net_area/outputs/pt1_100/non_paced_header_extracted.csv \
  --output-dir analysis/qrs_axis_net_area/outputs/pt1_100/error_analysis
```

This writes:

```text
outputs/error_analysis/method_summary.csv
outputs/error_analysis/group_summary.csv
outputs/error_analysis/flag_summary.csv
outputs/error_analysis/worst_cases.csv
outputs/error_analysis/per_case_error_features.csv
outputs/error_analysis/error_analysis_report.md
```

The strongest failure signal in the current run is low I/aVF vector magnitude:
the flagged subset has much higher MAE than the unflagged subset across all
three methods. This means many large errors occur when the net-area vector is
small or unstable, so a confidence/rejection rule based on QRS area magnitude is
likely needed before using the estimated axis.
