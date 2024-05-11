# `ecg-image-digitizer`
***Software tools for ECG image processing and digitization***

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

1. Kshama Kodthalu Shivashankara, Deepanshi, Afagh Mehri Shervedani, Matthew A. Reyna, Gari D. Clifford, Reza Sameni (2024). ECG-image-kit: a synthetic image generation toolbox to facilitate deep learning-based electrocardiogram digitization. In Physiological Measurement. IOP Publishing. doi: [10.1088/1361-6579/ad4954](https://doi.org/10.1088/1361-6579/ad4954)


2. ECG-Image-Kit: A Toolkit for Synthesis, Analysis, and Digitization of Electrocardiogram Images, (2024). URL: https://github.com/alphanumericslab/ecg-image-kit

## Contributors
- Deepanshi, Department of Biomedical Informatics, Emory University, GA, US
- Kshama Kodthalu Shivashankara, School of Electrical and Computer Engineering, Georgia Institute of Technology, Atlanta, GA, US
- Matthew A Reyna, Department of Biomedical Informatics, Emory University, GA, US
- Gari D Clifford, Department of Biomedical Informatics and Biomedical Engineering, Emory University and Georgia Tech, GA, US
- Reza Sameni (contact person), Department of Biomedical Informatics and Biomedical Engineering, Emory University and Georgia Tech, GA, US

## Contact
Please direct any inquiries, bug reports or requests for joining the team to: [ecg-image-kit@dbmi.emory.edu](ecg-image-kit@dbmi.emory.edu).


![Static Badge](https://img.shields.io/badge/ecg_image-kit-blue)




