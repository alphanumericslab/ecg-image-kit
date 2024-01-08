function [coarse_grid_res, fine_grid_res] = ecg_grid_size_from_paper(img, paper_width, unit)
% ecg_grid_size_from_paper - Estimates the size of the standard ECG coarse
% grid on a given image, based on a given ECG with
%
% This function calculates the grid size of an ECG image based on the physical 
% dimensions (width) of the paper. The function assumes a standard ECG grid size
% of 5mm x 5mm, representing 0.5mV in amplitude and 0.2s in time. The output is 
% the estimated grid size in pixels for both horizontal and vertical
% directions.
%
% Syntax:
%   [coarse_grid_res, fine_grid_res] = ecg_grid_size_from_paper(img, paper_width, unit)
%
% Inputs:
%   img - A 2D matrix representing the ECG image.
%   paper_width - The paper width, corresponding to the second dimension of
%   the input image
%   unit - A string specifying the unit of paper_width ('cm' or 'in').
%
% Outputs:
%   coarse_grid_res - Estimated coarse grid size (in pixels), representing 0.2s in time and 0.5mV in amplitude.
%   fine_grid_res - Estimated coarse grid size (in pixels), representing 40ms in time and 0.1mV in amplitude.
%
% Example:
%   % Load an ECG image
%   img = imread('path/to/ecg_image.jpg');
%
%   % Define the paper size in inches
%   paper_width = [11, 8.5];
%   unit = 'in';
%
%   % Estimate grid size
%   coarse_grid_res = ecg_grid_size_from_paper(img, paper_width(1), unit);
%
% Notes:
%   - The function issues a warning if the paper and image orientations do not match.
%   - The grid size estimation assumes standard ECG settings fitting the
%   entire ECG paper. The function will not report correct values if the
%   image is cropped or padded around the ECG paper
%
% Reference:
%   Reza Sameni, 2023, ECG-Image-Kit: A toolkit for ECG image analysis.
%   Available at: https://github.com/alphanumericslab/ecg-image-kit
%
% Revision History:
%   2023: First release

% Function implementation
width = size(img, 2);

% Convert paper size to inches if it's in centimeters
if strcmpi(unit, 'cm')
    paper_width_in_inch = paper_width / 2.54; % 1 inch = 2.54 cm
else
    paper_width_in_inch = paper_width; % Already in inches
end

% Calculating pixels per inch
pxls_per_inch = width / paper_width_in_inch;

% Standard coarse ECG grid 5mm x 5mm (0.5mV x 0.2s)
% Converting from mm to inches (1 inch = 25.4 mm)
coarse_grid_res = pxls_per_inch * 5 / 25.4; % coarse grid size in pixels

% Standard fine ECG grid 5mm x 5mm (0.1mV x 40ms)
fine_grid_res = coarse_grid_res / 5; % fine grid size in pixels
