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

## Citation
Please include references to the following articles in any publications:

1. Kshama Kodthalu Shivashankara, Afagh Mehri Shervedani, Matthew A. Reyna, Gari D. Clifford, Reza Sameni (2024). A Synthetic Electrocardiogram (ECG) Image Generation Toolbox to Facilitate Deep Learning-Based Scanned ECG Digitization. doi: [10.48550/ARXIV.2307.01946](https://doi.org/10.48550/ARXIV.2307.01946)

2. ECG-Image-Kit: A Toolkit for Synthesis, Analysis, and Digitization of Electrocardiogram Images, (2024). URL: https://github.com/alphanumericslab/ecg-image-kit

## Contributors
- [Kshama Kodthalu Shivashankara](mailto:kshamashivashankar@gmail.com), School of Electrical and Computer Engineering, Georgia Institute of Technology, Atlanta, GA, US
- [Deepanshi](mailto:deepanshi.asr.21@gmail.com), Department of Biomedical Informatics, Emory University, GA, US
- [Matthew Reyna](mailto:matthew@dbmi.emory.edu), Department of Biomedical Informatics, Emory University, GA, US
- [Gari D Clifford](mailto:gari@dbmi.emory.edu), Department of Biomedical Informatics, Emory University, GA, US
- [Reza Sameni](mailto:rsameni@dbmi.emory.edu) (corresponding author), Department of Biomedical Informatics, Emory University, GA, US

![Static Badge](https://img.shields.io/badge/ecg_image-kit-blue)




