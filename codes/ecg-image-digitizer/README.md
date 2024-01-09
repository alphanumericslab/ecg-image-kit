# `ecg-image-digitizer`

Tools for ECG image digitization.

## MATLAB

### Functions

| File | Description |
|---|---|
[ecg_grid_size_from_paper.m](ecg_grid_size_from_paper.m)| ECG grid size estimate from paper size and image width |
[ecg_gridest_margdist.m](ecg_gridest_margdist.m)| ECG grid size estimation - marginal image intensity approach |
[ecg_gridest_spectral.m](ecg_gridest_spectral.m)| ECG grid size estimation - spectral approach |
[ecg_gridest_matchedfilt.m](ecg_gridest_matchedfilt.m)| ECG grid size estimation - matched filter-based approach |
[image_to_sequence.m](image_to_sequence.m)| Extract time-series from an ECG segment |
[tanh_sat.m](tanh_sat.m)| Saturate signal/image intensity with a tanh function |


### Test scripts

| File | Description |
|---|---|
[test_ecg_grid_size_estimator.m](test_ecg_grid_size_estimator.m)| A test script for running and comparing the grid size estimation methods |
[test_ecg_sequence_extraction.m](test_ecg_sequence_extraction.m)| A test script for time-series extraction from an image segment |




