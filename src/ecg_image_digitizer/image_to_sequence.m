function data = image_to_sequence(img, mode, method, varargin)
% IMAGE_TO_SEQUENCE Extracts a sequence/time-series from an image.
%
% This function processes an image to extract a time-series representation,
% for example an ECG images. The method to extract the sequence depends on
% the image's characteristics (e.g., whether the foreground is darker or
% brighter than the background) and the filtering approach. The function
% returns a vector that has the same length as the width of the input image
% (the second dimension of the input image matrix). The method used
% for extracting the sequence can be justified using a maximum likelihood
% estimate of adjacent temporal samples when studied in a probabilistic
% framework.
%
% Syntax:
%   data = image_to_sequence(img, mode, method)
%   data = image_to_sequence(img, mode, method, windowlen)
%   data = image_to_sequence(img, mode, method, windowlen, plot_result)
%
% Inputs:
%   img - A 2D matrix representing the image.
%   mode - A string specifying the foreground type: 'dark-foreground' or
%          'bright-foreground'.
%   method - A string specifying the filtering method to use. Options are
%            'max_finder', 'moving_average', 'hor_smoothing', 
%            'all_left_right_neighbors', 'combined_all_neighbors'.
%   windowlen - (optional) Length of the moving average window. Default is 3.
%   plot_result - (optional) Boolean to plot the result. Default is false.
%
% Outputs:
%   data - Extracted sequence or time-series from the image.
%
% Example:
%   img = imread('path/to/ecg_image.jpg');
%   data = image_to_sequence(img, 'dark-foreground', 'moving_average', 5, true);
%
% Notes:
%   - The function assumes the image is either grayscale or RGB.
%   - The 'max_finder' method simply extracts the max value per column.
%   - Other methods apply different filters to smoothen or highlight features.
%
% Reference:
%   Reza Sameni, 2023, ECG-Image-Kit: A toolkit for ECG image analysis.
%   Available at: https://github.com/alphanumericslab/ecg-image-kit
%
% Revision History:
%   2022: First release

% Handle optional arguments
if nargin < 4 || isempty(varargin{1})
    windowlen = 3;
else
    windowlen = varargin{1};
end

if nargin < 5 || isempty(varargin{2})
    plot_result = false;
else
    plot_result = varargin{2};
end

% Convert image to grayscale if it's in RGB format
if ndims(img) == 3
    img_gray = rgb2gray(img);
else
    img_gray = img;
end

% Process image based on specified foreground mode
switch mode
    case 'dark-foreground'
        img_flipped = imcomplement(img_gray);
    case 'bright-foreground'
        img_flipped = img_gray;
end

% Apply different methods for sequence extraction
switch method
    case 'max_finder'
        img_filtered = img_flipped;

    case 'moving_average'
        h = ones(windowlen); h = h / sum(h(:));
        img_filtered = imfilter(img_flipped, h, 'replicate');

    case 'hor_smoothing'
        h = ones(1, windowlen); h = h / sum(h(:));
        img_filtered = imfilter(img_flipped, h, 'replicate');

    case 'all_left_right_neighbors'
        h = [1, 0, 1; 1, 1, 1; 1, 0, 1]; h = h / sum(h(:));
        img_filtered = imfilter(img_flipped, h, 'replicate');

    case 'combined_all_neighbors'
        h1 = [1, 1, 1]; h1 = h1 / sum(h1(:));
        z1 = imfilter(img_flipped, h1, 'replicate');
        h2 = [1, 0, 0; 0, 1, 0; 0, 0, 1]; h2 = h2 / sum(h2(:));
        z2 = imfilter(img_flipped, h2, 'replicate');
        h3 = [0, 0, 1; 0, 1, 0; 1, 0, 0]; h3 = h3 / sum(h3(:));
        z3 = imfilter(img_flipped, h3, 'replicate');

        img_filtered = min(min(z1, z2), z3);
end

% Find the maximum pixel value in each column to represent the ECG signal
[~, I] = max(img_filtered, [], 1);
img_height = size(img_filtered, 1);
data = img_height - I; % Convert to vertical position (ECG amplitude with offset)

% Plot the result if requested
if plot_result
    figure;
    imshow(img);
    hold on;
    plot(1:size(img, 2), size(img, 1) - data, 'g', 'linewidth', 3);
    hold off;
end
