function [grid_sizes, grid_size_prominences, mask_size, matched_filter_powers_avg, I_peaks] = ecg_gridest_matchedfilt(img, varargin)
% ECG_GRIDEST_MATCHEDFILT Estimates grid size in ECG images using matched filtering.
%
% This function analyzes an ECG image to estimate the grid size using a
% matched filter-based approach. The image is segmented into smaller
% regular or random patches, which are processed with an edge-only
% square-haped matched filter of variable size. The matched filter output
% powers are calculated and averaged across all patches. The matched filter
% sizes yielding the maximum average power are returned as potential grid
% sizes.
%
% Note: This function only detects regular grids without rotation. The
% returned values should be evaluated based on the image DPI and ECG image
% style to map the grid resolutions to physical time and amplitude units.
%
% Syntax:
%   [grid_sizes, grid_size_prominences, mask_size, matched_filter_powers_avg, I_peaks] = ecg_gridest_matchedfilt(img)
%   [grid_sizes, grid_size_prominences, mask_size, matched_filter_powers_avg, I_peaks] = ecg_gridest_matchedfilt(img, params)
%
% Inputs:
%   img - A 2D matrix representing the ECG image in grayscale or RGB formats.
%   params - (optional) A struct containing various parameters to control
%            the image processing and grid detection algorithm. Default
%            values are used if this argument is not provided. See below for details.
%
% Outputs:
%   grid_sizes - Vector of estimated grid sizes.
%   grid_size_prominences - Vector of prominences for each grid size.
%   mask_size - Array of all studied grid sizes.
%   matched_filter_powers_avg - Average matched filter output powers for each mask size.
%   I_peaks - The selected local peaks of matched_filter_powers_avg
%
% Parameters:
%   blur_sigma_in_inch - Blurring filter sigma in inches for shadow removal.
%   paper_size_in_inch - Default paper size in inches (width, height).
%   remove_shadows - Boolean to indicate if shadows due to scanning should be removed.
%   sat_pre_grid_det - Boolean to indicate if pre-grid detection saturation should be applied.
%   sat_level_pre_grid_det - Saturation k-sigma level before grid detection.
%   num_seg_hor - Number of horizontal segments for segmentation.
%   num_seg_ver - Number of vertical segments for segmentation.
%   tiling_method - Tiling method for segmentation ('REGULAR_TILING' or 'RANDOM_TILING').
%   total_segments - Total number of segments for 'RANDOM_TILING' method.
%   max_grid_size - Maximum size of the grid to be analyzed.
%   min_grid_size - Minimum size of the grid to be analyzed.
%   power_avg_prctile_th - Percentile threshold for averaging matched filter powers.
%   detailed_plots - Boolean to control the generation of detailed plots.
%
% Example:
%   img = imread('path/to/ecg_image.jpg');
%   [grid_sizes, proms, mask_size, mf_powers] = ecg_gridest_matchedfilt(img);
%
%   params = struct('tiling_method', 'RANDOM_TILING', 'remove_shadows', false);
%   [grid_sizes, proms, mask_size, mf_powers] = ecg_gridest_matchedfilt(img, params);
%
% Notes:
%   Requires Image Processing Toolbox for some operations.
%   Limited to integer-valued grid sizes and susceptible to image rotation.
%
% Reference:
%   Reza Sameni, 2023, ECG-Image-Kit: A toolkit for ECG image analysis.
%   Available at: https://github.com/alphanumericslab/ecg-image-kit
%
% Revision History:
%   2023: First release

%% parse algorithm parameters
if nargin > 1
    params = varargin{1};
else
    params = [];
end

if ~isfield(params, 'blur_sigma_in_inch') || isempty(params.blur_sigma_in_inch)
    params.blur_sigma_in_inch = 1.0; % bluring filter sigma in inches
end
if ~isfield(params, 'paper_size_in_inch') || isempty(params.paper_size_in_inch)
    params.paper_size_in_inch = [11, 8.5]; % default paper size in inch (letter size)
end

if ~isfield(params, 'remove_shadows') || isempty(params.remove_shadows)
    params.remove_shadows = true; % remove shadows due to photography/scanning by default
end

if ~isfield(params, 'sat_pre_grid_det') || isempty(params.sat_pre_grid_det)
    params.sat_pre_grid_det = true; % saturate densities or not (before spectral estimation)
end
if params.sat_pre_grid_det
    if ~isfield(params, 'sat_level_pre_grid_det') || isempty(params.sat_level_pre_grid_det)
        params.sat_level_pre_grid_det = 0.7; % saturation k-sigma before grid detection
    end
end

if ~isfield(params, 'num_seg_hor') || isempty(params.num_seg_hor)
    params.num_seg_hor = 4;
end

if ~isfield(params, 'num_seg_ver') || isempty(params.num_seg_ver)
    params.num_seg_ver = 4;
end

if ~isfield(params, 'tiling_method') || isempty(params.tiling_method)
    params.tiling_method = 'RANDOM_TILING'; %'REGULAR_TILING' or 'RANDOM_TILING'
    if ~isfield(params, 'total_segments') || isempty(params.total_segments)
        params.total_segments = 16;
    end
end

if ~isfield(params, 'max_grid_size') || isempty(params.max_grid_size)
    params.max_grid_size = 30;
end

if ~isfield(params, 'min_grid_size') || isempty(params.min_grid_size)
    params.min_grid_size = 2;
end

if ~isfield(params, 'power_avg_prctile_th') || isempty(params.power_avg_prctile_th)
    params.power_avg_prctile_th = 95.0;
end

if ~isfield(params, 'detailed_plots') || isempty(params.detailed_plots)
    params.detailed_plots = 0;
end

width = size(img, 2);
height = size(img, 1);

%% convert image to gray scale
if ndims(img) == 3
    img_gray = double(rgb2gray(img));
    img_gray = img_gray / max(img_gray(:));
else
    img_gray = double(img);
    img_gray = imcomplement(img_gray / max(img_gray(:)));
end

%% shaddow removal and intensity normalization
switch params.remove_shadows
    case true
        blurrring_sigma = mean([width * params.blur_sigma_in_inch / params.paper_size_in_inch(1), height * params.blur_sigma_in_inch / params.paper_size_in_inch(2)]);
        img_gray_blurred = imgaussfilt(img_gray, blurrring_sigma, 'Padding', 'symmetric');

        img_gray_normalized = img_gray ./ img_gray_blurred;
        img_gray_normalized = (img_gray_normalized - min(img_gray_normalized(:)))/(max(img_gray_normalized(:)) - min(img_gray_normalized(:)));

    case false
        img_gray_blurred = img_gray;
        img_gray_normalized = img_gray;

end

%% image density saturation
if params.sat_pre_grid_det
    img_sat = tanh_sat(1.0 - img_gray_normalized(:)', params.sat_level_pre_grid_det, 'ksigma')';%imbinarize(img_gray_normalized, 'adaptive','ForegroundPolarity','dark','Sensitivity',0.4);
    img_gray_normalized = reshape(img_sat, size(img_gray_normalized));
    figure
    imshowpair(img_gray, img_gray_normalized, 'montage')
end

%% segmentation
seg_width = floor(width / params.num_seg_hor);
seg_height = floor(height / params.num_seg_ver);
mask_size = params.min_grid_size : params.max_grid_size;
switch params.tiling_method
    case 'REGULAR_TILING' % regular tiling across the entire image
        matched_filter_powers = zeros(params.num_seg_hor * params.num_seg_ver, length(mask_size));
        k = 1;
        for i = 1 : params.num_seg_ver
            for j = 1 : params.num_seg_hor
                segment = img_gray_normalized((i -1)*seg_height + 1 : i*seg_height, (j -1)*seg_width + 1 : j*seg_width);
                segment = (segment - mean(segment(:)))/std(segment(:));
                for g = 1 : length(mask_size)
                    B = boundary_mask(mask_size(g));
                    B = B - mean(B(:));
                    matched_filtered = filter2(B, segment);
                    % pm = (matched_filtered(:) - mean(matched_filtered(:))).^2;
                    % pm = sqrt(mask_size(g))*(matched_filtered(:) - mean(matched_filtered(:))).^2;
                    pm = matched_filtered(:).^2;
                    pm_th = prctile(pm, params.power_avg_prctile_th);
                    matched_filter_powers(k, g) = 10*log10(mean(pm(pm > pm_th)));
                end
                k = k + 1;
            end
        end
    case 'RANDOM_TILING' % random segments across the entire image
        matched_filter_powers = zeros(params.total_segments, length(mask_size));
        for k = 1 : params.total_segments
            start_hor = randi(width - seg_width);
            start_ver = randi(height - seg_height);
            segment = img_gray_normalized(start_ver : start_ver + seg_height-1, start_hor : start_hor + seg_width-1);
            segment = (segment - mean(segment(:)))/std(segment(:));
            for g = 1 : length(mask_size)
                B = boundary_mask(mask_size(g));
                B = B - mean(B(:));
                matched_filtered = filter2(B, segment);
                % pm = (matched_filtered(:) - mean(matched_filtered(:))).^2;
                % pm = sqrt(mask_size(g))*(matched_filtered(:) - mean(matched_filtered(:))).^2;
                pm = matched_filtered(:).^2;
                pm_th = prctile(pm, params.power_avg_prctile_th);
                matched_filter_powers(k, g) = 10*log10(mean(pm(pm > pm_th)));
            end
        end
end

matched_filter_powers_avg = mean(matched_filter_powers, 1);
[~, I_peaks, ~, grid_size_prominences] = findpeaks(matched_filter_powers_avg);
grid_sizes = mask_size(I_peaks) - 1; % -1 is to convert mask size to period

%% Plot results
if params.detailed_plots > 0
    figure
    hold on
    plot(mask_size - 1, matched_filter_powers')  % -1 is to convert mask size to period
    plot(mask_size - 1, matched_filter_powers_avg, 'k', 'linewidth', 3)  % -1 is to convert mask size to period
    plot(mask_size(I_peaks) - 1, matched_filter_powers_avg(I_peaks), 'ro', 'markersize', 18)
    grid
    xlabel('Grid size');
    ylabel('Average power (dB)');
    title('Average matched-filter output power vs grid size');

    figure
    subplot(2,2,1)
    imshow(img)
    title('img', 'interpreter', 'none')
    subplot(2,2,2)
    imshow(img_gray)
    title('img_gray', 'interpreter', 'none')
    subplot(2,2,3)
    imshow(img_gray_blurred)
    title('img_gray_blurred', 'interpreter', 'none')
    subplot(2,2,4)
    imshow(img_gray_normalized)
    title('img_gray_normalized', 'interpreter', 'none')
    sgtitle('Preprocessing stages (shaddow removal and intensity normalization)');
end
end

function B = boundary_mask(sz)
B = zeros(sz);
B(1, :) = 1;
B(end, :) = 1;
B(:, 1) = 1;
B(:, end) = 1;
B = B / sum(B(:));
end