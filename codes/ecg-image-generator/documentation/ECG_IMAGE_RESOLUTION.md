# A note on electrocardiogram image vs time-series resolutions

[Reza Sameni](rsameni@dbmi.emory.edu)

Department of Biomedical Informatics, Emory University

## ECG as a time-series
The electrocardiogram (ECG), recorded by standard body surface leads, typically has an amplitude of several millivolts and its spectral content ranges from approximately 0.05Hz to around 150Hz. When transformed into a digital signal, it first passes through an anti-aliasing low-pass filter (in the analog domain) before being sampled at a sampling frequency ($f_s$). According to the Nyquist theorem, the cutoff frequency of the anti-aliasing filter should be lower than $f_s/2$. Systems with lower resolution, such as onl ECG machines, Holder monitors and wearable devices, may have sampling frequencies as low as 100Hz. Modern high-quality clinical monitors often sample at higher frequencies, such as 1000Hz or more. Non-uniform (irregular) sampling is a less common, yet viable, option employed in some low-power, microcontroller-based devices. These devices satisfy the Nyquist frequency only on average but do not adhere to precise sampling times. This flexibility allows for accommodation of other microcontroller processes that run concurrently in the background. For more in-depth information on Nyquist theory, uniform and non-uniform sampling theory <sup>[[Oppenheim 1998]](#ref-oppenheim-discrete), [[Marvasti 2001]](#ref-marvasti-nonuniform), [[Mitra 2001]](#ref-mitra-dsp)</sup>.

The amplitude resolution of the digital signal depends on the number of bits of the analog-to-digital converter (ADC), denoted by $N$. In older ECG devices, $N$ was as low as 8 bits, resulting in a maximum resolution of 256 quantization levels (assuming that the ECG was amplified to span the ADC's full dynamic range). In modern ECG devices, $N$ can be up to 24 bits, resulting in significantly better amplitude resolution. It is important to note that due to electronic and thermal noise, and depending on the quality of the analog front-end circuitry, the effective number of bits (ENOB) is, in practice, lower than the nominal ADC bit number $N$. For instance, a 16-bit ADC may yield between 12.5 to 14 ENOBs in practice. With an $N$-bit ADC digitizing the input voltage range of $V_{min}$ to $V_{max}$, the voltage resolution after digitization is:

$$\delta v = \frac{V_{max} - V_{min}}{2^N}$$
For example, if the input span of the ADC is $\Delta_v=V_{max} - V_{min} = 5mV$, an 8-bit ADC yeilds a voltage resolution of $\delta v=19.5\mu V$, while a 12-bit ADC yeilds $\delta v=1.22\mu V$, improving the voltage resolution by a factor of 16. Further details regarding the ENOB and its relationship with $N$ and $f_s$ can be found <sup>[[Sameni 2018]](#ref-sameni-digital)<sup>.


## Printed ECG
In clinical applications, the ECG is printed on standard ECG paper featuring fine grids and coarse grid. The fine grids are 1mm by 1mm, corresponding to 0.1mV in amplitude and 40ms in time. The coarse-grids are 5mm by 5mm, equating to 0.5mV in amplitude and 200ms in time, as shown in the image below.

![Standard printed ECG grid](./ecg_grid.png)

In modern ECG devices, despite the data being collected digitally and stored on computers or other digital platforms, the same convention is used. ECGs are visualized against the same background grids, whether displayed on a computer screen or printed as a PDF or image file. The number and format of the leads, along with the ECG grid color, vary depending on the ECG acquisition technology and the device manufacturer. The most common clinical ECGs are 12-lead, featuring approximately 2.5-second segments of the 12 leads arranged in a 3-row by 4-column grid. Additionally, one to three leads (typically leads II, V1, V2, or V5) are displayed as a longer 10-second strip at the bottom. Below is an example of a typical ECG image.

![10.7759/cureus.2523](./ST_elevation_myocardial_infarction_ECG.png)

## Scanned ECG images
Printing an analog or digital ECG on paper and then rescanning it as an image involves implicit or explicit interpolation and resampling of the original ECG. Once an ECG is printed, $f_s$, the original sampling frequency of the digital time series, and its number of quantization bits $N$, become irrelevant, as the signal has been transformed back into the continuous-time domain. When the ECG paper is scanned or photographed as an image, it is essentially being quantized and resampled again, this time as a two-dimensional image. Assuming the image is scanned at a resolution of $D$ dots per inch (DPI), each 1-inch by 1-inch square of the printed ECG is quantized into a $D \times D$ matrix, each pixel stored in $B$ bits. If scanned as a colored image, there will be three such matrices, corresponding to the colors red (R), green (G), and blue (B). Modern images typically use $B = 8$, resulting in 24 bits per pixel. Therefore, for example, scanning a Letter-size paper of 11 inches by 8.5 inches at 72 DPI would require 8.5 $\times$ 11 $\times$ (72 $\times$ 72) $\times$ 3 bytes = 1,454,112 bytes or 1.39MB as an uncompressed bitmap file (excluding metadata or other headers).

Therefore, when a standard ECG, printed on A4 or Letter-size paper, is scanned at full image size (without any cropping or excess borders), each 1 inch (25.4mm) horizontally and vertically maps to $D$ pixels. In other words, each coarse square of the ECG (0.5mV in amplitude and 200ms in time) corresponds to $\frac{5 \times D}{25.4}$ pixels. This means the amplitude resolution of the scanned ECG is: $$dV = \frac{2.54 mV}{D}$$ and the temporal resolution is $dT = \frac{1.016s}{D}$ seconds, or equivalently, a sampling frequency (in Hertz): $$f_s' = \frac{D}{1.016}$$

As we can see, the effective sampling frequency of the scanned ECG, $f_s'$, is independent of the original digital signal's sampling frequency $f_s$. However, since the original signal's frequency range was limited to $f_s/2$ by the analog front-end anti-aliasing filter, increasing $D$, and consequently $f'_s$, although it will yield smoother waveforms, will not add any information beyond $f_s/2$. Further details and examples can be followed from [[Shivashankara 2023]](#ref-ecg-image-kit-paper).

## Citation
Please include references [[Shivashankara 2023]](#ref-ecg-image-kit-paper) and [[ECG-Image-Kit]](#ref-ecg-image-kit) in publications related to this article.


## References

1. <a name="ref-oppenheim-discrete"></a> Oppenheim, A. V., Schafer, R. W., & Buck, J. R. (1998). Discrete-time signal processing (2nd ed.). Upper Saddle River, NJ: Pearson. ISBN: 9780137549207


1. <a name="ref-marvasti-nonuniform"></a> Marvasti, Farokh, ed. Nonuniform Sampling: Theory and Practice. (2001). Netherlands: Springer US.

1. <a name="ref-mitra-dsp"></a> Mitra, Sanjit K. Digital signal processing: a computer-based approach. McGraw-Hill Higher Education, 2001.

1. <a name="ref-sameni-digital"></a> Reza Sameni. Digital Systems Design. Engineering school. Iran. 2018. ⟨cel-01815308⟩. Online at: https://hal.science/cel-01815308v1

1. <a name="ref-ecg-image-kit-paper"></a> Kshama Kodthalu Shivashankara, Afagh Mehri Shervedani, Matthew A. Reyna, Gari D. Clifford, Reza Sameni (2023). A Synthetic Electrocardiogram (ECG) Image Generation Toolbox to Facilitate Deep Learning-Based Scanned ECG Digitization. arXiv. Online at: https://doi.org/10.48550/ARXIV.2307.01946

1. <a name="ref-ecg-image-kit"></a> ECG-Image-Kit: A Toolkit for Synthesis, Analysis, and Digitization of Electrocardiogram Images, January 2024, Online at: https://github.com/alphanumericslab/ecg-image-kit


![Static Badge](https://img.shields.io/badge/ecg_image-kit-blue)