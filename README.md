# `ECG-Image-Kit`
**A Toolkit for Synthesis, Analysis, and Digitization of Electrocardiogram Images**

The ECG (Electrocardiogram) is a widely-used and accurate diagnostic tool for cardiovascular diseases. Traditionally recorded in printed formats, the digitization of ECGs holds immense potential for training machine learning (ML) models in algorithmic ECG diagnosis. However, physical ECG archives are at risk of deterioration. Simply scanning printed ECGs is insufficient, as ML models require time-series data from ECGs. This necessitates the digitization and conversion of paper ECG archives into time-series data.

To address these challenges, we have developed methods and tools for generating synthetic ECG images on standard paper-like ECG backgrounds, faithfully replicating realistic artifacts. Our approach includes plotting ECG time-series data on ECG paper-like backgrounds, followed by applying various distortions such as handwritten text artifacts, wrinkles, creases, and perspective transforms to the generated images, while ensuring the absence of personally identifiable information. These synthetic ECG images provide a valuable resource for developing and evaluating ML and deep learning models for ECG digitization and analysis.

In this repository, you will find tools and utilities for analyzing scanned ECG images, generating realistic synthetic ECG images, and digitizing them into time-series data. Our aim is to facilitate the digitization and analysis of ECG archives, ultimately enabling the advancement of computerized ECG diagnosis.

Contributions and feedback are welcome and encouraged from our user community, as we strive to revolutionize the digitization and analysis of ECG data using state-of-the-art deep learning and image processing techniques.

## Toolsets
* [Synthetic ECG image generation tools](codes/ecg-image-generator/)
* [ECG image digitization tools](codes/ecg-image-digitizer/)

## Reference
[![arXiv](https://img.shields.io/badge/arXiv-ECGgen-b31b1b.svg)](https://doi.org/10.48550/ARXIV.2307.01946)

Shivashankara, K. K., Shervedani, A. M., and Sameni, R. (2023). A Synthetic Electrocardiogram (ECG) Image Generation Toolbox to Facilitate Deep Learning-Based Scanned ECG Digitization. doi: [10.48550/ARXIV.2307.01946](https://doi.org/10.48550/ARXIV.2307.01946)

## Contributors
- [Reza Sameni](mailto:rsameni@dbmi.emory.edu) (corresponding author), Department of Biomedical Informatics, Emory University, GA, US
- [Kshama Kodthalu Shivashankara](mailto:kshamashivashankar@gmail.com), School of Electrical and Computer Engineering, Georgia Institute of Technology, Atlanta, GA, US
- [Deepanshi](mailto:deepanshi.asr.21@gmail.com), Department of Biomedical Informatics, Emory University, GA, US
- [Matthew Reyna](mailto:matthew@dbmi.emory.edu), Department of Biomedical Informatics, Emory University, GA, US
- [Gari D Clifford](mailto:gari@dbmi.emory.edu), Department of Biomedical Informatics, Emory University, GA, US

