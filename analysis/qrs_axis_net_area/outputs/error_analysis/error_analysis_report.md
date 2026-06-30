# QRS Axis Error Analysis

## Overall

| method | N | MAE | median | RMSE | P90 | within 30 deg | worst PT |
|---|---:|---:|---:|---:|---:|---:|---:|
| direct_i_avf | 39 | 31.7 | 24.9 | 46.3 | 56.6 | 53.8% | PT22 |
| lead_i_ii_reconstructed_avf | 39 | 32.3 | 20.7 | 49.0 | 56.1 | 59.0% | PT14 |
| limb_lead_least_squares | 39 | 28.1 | 16.6 | 44.4 | 43.7 | 59.0% | PT14 |

## Main Takeaway

The lowest MAE is from `limb_lead_least_squares` (28.1 deg), but the P90 error is still 43.7 deg. This supports using the net-area approach as a rough directional signal, not as a replacement for the header QRS axis.

## Failure Flags

| flag | method | flagged N | flagged MAE | unflagged MAE | delta |
|---|---|---:|---:|---:|---:|
| low_abs_area_i | direct_i_avf | 6 | 65.0 | 25.6 | 39.4 |
| low_abs_area_i | lead_i_ii_reconstructed_avf | 6 | 60.4 | 27.1 | 33.3 |
| low_abs_area_i | limb_lead_least_squares | 6 | 54.8 | 23.3 | 31.5 |
| low_abs_area_avf | direct_i_avf | 16 | 36.5 | 28.4 | 8.1 |
| low_abs_area_avf | lead_i_ii_reconstructed_avf | 16 | 34.5 | 30.7 | 3.7 |
| low_abs_area_avf | limb_lead_least_squares | 16 | 31.4 | 25.9 | 5.6 |
| low_i_avf_vector_mag | direct_i_avf | 10 | 65.7 | 20.0 | 45.7 |
| low_i_avf_vector_mag | lead_i_ii_reconstructed_avf | 10 | 63.7 | 21.4 | 42.2 |
| low_i_avf_vector_mag | limb_lead_least_squares | 10 | 60.9 | 16.8 | 44.0 |
| direct_limb_ls_disagree_gt30 | direct_i_avf | 1 | 61.7 | 30.9 | 30.8 |
| direct_limb_ls_disagree_gt30 | lead_i_ii_reconstructed_avf | 1 | 48.6 | 31.8 | 16.7 |
| direct_limb_ls_disagree_gt30 | limb_lead_least_squares | 1 | 4.1 | 28.8 | -24.7 |

## Worst Cases

| method | rank | PT | standard | estimate | abs error | low I | low aVF | low vector |
|---|---:|---:|---:|---:|---:|---|---|---|
| direct_i_avf | 1 | PT22 | 39.0 | -124.15969454566944 | 163.15969454566942 | False | False | True |
| direct_i_avf | 2 | PT14 | 50.0 | -159.24592868120058 | 150.75407131879945 | True | True | True |
| direct_i_avf | 3 | PT35 | 59.0 | 120.72073069599229 | 61.7207306959923 | False | False | False |
| direct_i_avf | 4 | PT23 | 46.0 | 105.2551187030578 | 59.2551187030578 | True | True | True |
| direct_i_avf | 5 | PT8 | 76.0 | 131.92347466647257 | 55.92347466647257 | True | True | True |
| direct_i_avf | 6 | PT31 | 28.0 | -24.837396009213958 | 52.83739600921396 | True | True | True |
| direct_i_avf | 7 | PT37 | 84.0 | 131.36157906631564 | 47.36157906631564 | False | False | False |
| direct_i_avf | 8 | PT42 | 67.0 | 22.319440392975086 | 44.68055960702492 | False | True | True |
| lead_i_ii_reconstructed_avf | 1 | PT14 | 50.0 | -144.89472679013826 | 165.1052732098617 | True | True | True |
| lead_i_ii_reconstructed_avf | 2 | PT22 | 39.0 | -125.93711959124073 | 164.93711959124073 | False | False | True |
| lead_i_ii_reconstructed_avf | 3 | PT37 | 84.0 | 172.36538797125718 | 88.36538797125718 | False | False | False |
| lead_i_ii_reconstructed_avf | 4 | PT23 | 46.0 | 119.10602569480884 | 73.10602569480884 | True | True | True |
| lead_i_ii_reconstructed_avf | 5 | PT39 | 1.0 | 52.78975669207915 | 51.78975669207915 | False | False | True |
| lead_i_ii_reconstructed_avf | 6 | PT35 | 59.0 | 107.56779083123786 | 48.56779083123786 | False | False | False |
| lead_i_ii_reconstructed_avf | 7 | PT8 | 76.0 | 122.23055389042544 | 46.230553890425426 | True | True | True |
| lead_i_ii_reconstructed_avf | 8 | PT17 | -24.0 | -70.01696368966076 | 46.01696368966077 | False | False | False |
| limb_lead_least_squares | 1 | PT14 | 50.0 | -143.9000270953232 | 166.0999729046768 | True | True | True |
| limb_lead_least_squares | 2 | PT22 | 39.0 | -120.76651217659992 | 159.76651217659992 | False | False | True |
| limb_lead_least_squares | 3 | PT17 | -24.0 | -68.25508030842215 | 44.25508030842215 | False | False | False |
| limb_lead_least_squares | 4 | PT40 | 35.0 | 78.77430648634304 | 43.77430648634305 | True | False | True |
| limb_lead_least_squares | 5 | PT19 | 47.0 | 3.273804459995991 | 43.726195540004 | False | True | False |
| limb_lead_least_squares | 6 | PT39 | 1.0 | 43.275801654182274 | 42.27580165418226 | False | False | True |
| limb_lead_least_squares | 7 | PT9 | 33.0 | -7.608962770256919 | 40.60896277025691 | False | True | True |
| limb_lead_least_squares | 8 | PT8 | 76.0 | 115.20543476194143 | 39.20543476194143 | True | True | True |
