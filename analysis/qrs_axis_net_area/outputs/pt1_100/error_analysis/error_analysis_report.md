# QRS Axis Error Analysis

## Overall

| method | N | MAE | median | RMSE | P90 | within 30 deg | worst PT |
|---|---:|---:|---:|---:|---:|---:|---:|
| direct_i_avf | 79 | 33.0 | 22.5 | 47.1 | 62.5 | 57.0% | PT94 |
| lead_i_ii_reconstructed_avf | 79 | 33.0 | 20.6 | 49.0 | 74.8 | 60.8% | PT94 |
| limb_lead_least_squares | 79 | 31.2 | 20.5 | 46.5 | 57.5 | 59.5% | PT94 |

## Main Takeaway

The lowest MAE is from `limb_lead_least_squares` (31.2 deg), but the P90 error is still 57.5 deg. This supports using the net-area approach as a rough directional signal, not as a replacement for the header QRS axis.

## Failure Flags

| flag | method | flagged N | flagged MAE | unflagged MAE | delta |
|---|---|---:|---:|---:|---:|
| low_abs_area_i | direct_i_avf | 12 | 56.5 | 28.8 | 27.7 |
| low_abs_area_i | lead_i_ii_reconstructed_avf | 12 | 55.0 | 29.0 | 26.0 |
| low_abs_area_i | limb_lead_least_squares | 12 | 53.0 | 27.3 | 25.6 |
| low_abs_area_avf | direct_i_avf | 26 | 38.4 | 30.3 | 8.2 |
| low_abs_area_avf | lead_i_ii_reconstructed_avf | 26 | 37.5 | 30.7 | 6.8 |
| low_abs_area_avf | limb_lead_least_squares | 26 | 35.6 | 29.1 | 6.5 |
| low_i_avf_vector_mag | direct_i_avf | 20 | 65.8 | 21.8 | 44.0 |
| low_i_avf_vector_mag | lead_i_ii_reconstructed_avf | 20 | 64.9 | 22.1 | 42.8 |
| low_i_avf_vector_mag | limb_lead_least_squares | 20 | 64.8 | 19.8 | 44.9 |
| direct_limb_ls_disagree_gt30 | direct_i_avf | 1 | 61.7 | 32.6 | 29.1 |
| direct_limb_ls_disagree_gt30 | lead_i_ii_reconstructed_avf | 1 | 48.6 | 32.8 | 15.8 |
| direct_limb_ls_disagree_gt30 | limb_lead_least_squares | 1 | 4.1 | 31.6 | -27.5 |

## Worst Cases

| method | rank | PT | standard | estimate | abs error | low I | low aVF | low vector |
|---|---:|---:|---:|---:|---:|---|---|---|
| direct_i_avf | 1 | PT94 | 58.0 | -129.92901517845038 | 172.0709848215496 | False | False | True |
| direct_i_avf | 2 | PT22 | 39.0 | -124.15969454566944 | 163.15969454566942 | False | False | True |
| direct_i_avf | 3 | PT14 | 50.0 | -159.24592868120058 | 150.75407131879945 | True | True | True |
| direct_i_avf | 4 | PT66 | 48.0 | -53.746162262555195 | 101.7461622625552 | True | True | True |
| direct_i_avf | 5 | PT52 | 88.0 | 3.928920488866697e-15 | 88.0 | False | True | True |
| direct_i_avf | 6 | PT50 | 28.0 | -53.3658861240326 | 81.3658861240326 | True | False | True |
| direct_i_avf | 7 | PT93 | 88.0 | 14.729024450709911 | 73.27097554929009 | False | True | True |
| direct_i_avf | 8 | PT89 | 6.0 | 71.7228903907799 | 65.7228903907799 | True | True | True |
| lead_i_ii_reconstructed_avf | 1 | PT94 | 58.0 | -122.46116148691448 | 179.53883851308552 | False | False | True |
| lead_i_ii_reconstructed_avf | 2 | PT14 | 50.0 | -144.89472679013826 | 165.1052732098617 | True | True | True |
| lead_i_ii_reconstructed_avf | 3 | PT22 | 39.0 | -125.93711959124073 | 164.93711959124073 | False | False | True |
| lead_i_ii_reconstructed_avf | 4 | PT66 | 48.0 | -60.4937151489069 | 108.4937151489069 | True | True | True |
| lead_i_ii_reconstructed_avf | 5 | PT37 | 84.0 | 172.36538797125718 | 88.36538797125718 | False | False | False |
| lead_i_ii_reconstructed_avf | 6 | PT82 | 88.0 | 174.3938004866563 | 86.39380048665629 | False | False | False |
| lead_i_ii_reconstructed_avf | 7 | PT50 | 28.0 | -55.469112668663264 | 83.46911266866326 | True | False | True |
| lead_i_ii_reconstructed_avf | 8 | PT52 | 88.0 | 6.458725184661899 | 81.5412748153381 | False | True | True |
| limb_lead_least_squares | 1 | PT94 | 58.0 | -122.2035539790874 | 179.79644602091258 | False | False | True |
| limb_lead_least_squares | 2 | PT14 | 50.0 | -143.9000270953232 | 166.0999729046768 | True | True | True |
| limb_lead_least_squares | 3 | PT22 | 39.0 | -120.76651217659992 | 159.76651217659992 | False | False | True |
| limb_lead_least_squares | 4 | PT66 | 48.0 | -60.683071533362195 | 108.6830715333622 | True | True | True |
| limb_lead_least_squares | 5 | PT52 | 88.0 | 1.647771050624324 | 86.35222894937567 | False | True | True |
| limb_lead_least_squares | 6 | PT50 | 28.0 | -54.03986884014323 | 82.03986884014323 | True | False | True |
| limb_lead_least_squares | 7 | PT93 | 88.0 | 17.143069055945748 | 70.85693094405426 | False | True | True |
| limb_lead_least_squares | 8 | PT89 | 6.0 | 68.675507118962 | 62.675507118962 | True | True | True |
