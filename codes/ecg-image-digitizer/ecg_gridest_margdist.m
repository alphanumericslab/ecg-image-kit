function [grid_size_hor, grid_size_ver, grid_spacing_hor_all_seg, grid_spacing_ver_all_seg] = ecg_gridest_margdist(img, varargin)
% ecg_gridest_margdist Estimates grid size in ECG images.
%
% This function analyzes an ECG image to estimate the grid size in both
% horizontal and vertical directions.
%
% Syntax:
%   [grid_size_hor, grid_size_ver, grid_spacing_hor_all_seg, grid_spacing_ver_all_seg] = ecg_gridest_margdist(img)
%   [grid_size_hor, grid_size_ver, grid_spacing_hor_all_seg, grid_spacing_ver_all_seg] = ecg_gridest_margdist(img, params)
%
% Inputs:
%   img - A 2D matrix representing the ECG image in grayscale or RGB formats.
%   params - (Optional) A struct containing various parameters to control
%            the image processing and grid detection algorithm. Default
%            values are used if this argument is not provided. See function
%            for details
%
% Outputs:
%   grid_size_hor - Estimated grid size in the horizontal direction (in pixels).
%   grid_size_ver - Estimated grid size in the vertical direction (in pixels).
%   grid_spacing_hor_all_seg - Grid spacing for all segments in the
%                                     horizontal direction (in pixels).
%   grid_spacing_ver_all_seg - Grid spacing for all segments in the
%                                   vertical direction (in pixels).
%
% Example:
%   % Load an ECG image
%   img = imread('path/to/ecg_image.jpg');
%
%   % Estimate grid size with default parameters
%   [gh, gv, gsh, gsv] = ecg_gridest_margdist(img);
%
%   % Estimate grid size with custom parameters
%   params = struct('blur_sigma_in_inch', 0.8, 'remove_shadows', false);
%   [gh, gv, gsh, gsv] = ecg_gridest_margdist(img, params);
%
% Notes:
%   - The function requires Image Processing Toolbox for some operations.
%   - Edge detection is optional and can be controlled via the 'apply_edge_detection'
%     parameter in the params struct.
%   - The function uses histogram-based analysis for grid detection which
%     can be sensitive to image quality and resolution.
%
% Reference:
%   Reza Sameni, 2023, ECG-Image-Kit: A toolkit for ECG image analysis.
%   Available at: https://github.com/alphanumericslab/ecg-image-kit
%
% Revision History:
%   2023: First release
%

if nargin > 1
    params = varargin{1};
else
    params = [];
end

%% algorithm parameters
if ~isfield(params, 'blur_sigma_in_inch') || isempty(params.blur_sigma_in_inch)
    params.blur_sigma_in_inch = 1.0; % bluring filter sigma in inches
end
if ~isfield(params, 'paper_size_in_inch') || isempty(params.paper_size_in_inch)
    params.paper_size_in_inch = [11, 8.5]; % default paper size in inch (letter size)
end

if ~isfield(params, 'remove_shadows') || isempty(params.remove_shadows)
    params.remove_shadows = true; % remove shadows due to photography/scanning by default
end

if ~isfield(params, 'apply_edge_detection') || isempty(params.apply_edge_detection)
    params.apply_edge_detection = false; % detect grid on edge detection outputs
end

if params.apply_edge_detection
    if ~isfield(params, 'post_edge_det_gauss_filt_std') || isempty(params.post_edge_det_gauss_filt_std)
        params.post_edge_det_gauss_filt_std = 0.01; % post edge detection line smoothing
    end

    if ~isfield(params, 'sat_level_upper_prctile') || isempty(params.sat_level_upper_prctile)
        params.sat_level_upper_prctile = 99.0; % upper saturation threshold after bluring
    end
    if ~isfield(params, 'sat_level_lower_prctile') || isempty(params.sat_level_lower_prctile)
        params.sat_level_lower_prctile = 1.0; % lower saturation threshold after bluring
    end
end

if ~isfield(params, 'num_seg_hor') || isempty(params.num_seg_hor)
    params.num_seg_hor = 4;
end

if ~isfield(params, 'num_seg_ver') || isempty(params.num_seg_ver)
    params.num_seg_ver = 4;
end

if ~isfield(params, 'hist_grid_det_method') || isempty(params.hist_grid_det_method)
    params.hist_grid_det_method = 'RANDOM_TILING'; %'REGULAR_TILING', 'RANDOM_TILING';
    if ~isfield(params, 'total_segments') || isempty(params.total_segments)
        params.total_segments = 100;
    end
end

if ~isfield(params, 'min_grid_resolution') || isempty(params.min_grid_resolution)
    params.min_grid_resolution = 3; % in pixels
end

if ~isfield(params, 'min_grid_peak_prom_prctile') || isempty(params.min_grid_peak_prom_prctile)
    params.min_grid_peak_prom_prctile = 25;
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
%% edge detection
if params.apply_edge_detection
    % Canny edge detection
    edges = edge(img_gray_normalized, 'Canny');

    % make the edges sharper
    % edges = bwmorph(edges, 'thin', Inf);
    edges = bwmorph(edges, 'skel', Inf);

    % smooth the lines
    blurrring_sigma = mean([width * params.post_edge_det_gauss_filt_std / params.paper_size_in_inch(1), height * params.post_edge_det_gauss_filt_std / params.paper_size_in_inch(2)]);
    edges_blurred = imgaussfilt(double(edges), blurrring_sigma);
    % edges_blurred = edges_blurred / max(edges_blurred(:));
    % edges_blurred = double(edges) / max(double(edges(:)));

    % saturate extreme pixels
    edges_blurred_sat = edges_blurred;

    % upper saturation level
    sat_level = prctile(edges_blurred(:), params.sat_level_upper_prctile);
    I_sat = edges_blurred > sat_level;
    edges_blurred_sat(I_sat) = sat_level;

    % lower saturation level
    sat_level = prctile(edges_blurred(:), params.sat_level_lower_prctile);
    I_sat = edges_blurred < sat_level;
    edges_blurred_sat(I_sat) = sat_level;

    edges_blurred_sat = edges_blurred_sat / max(edges_blurred_sat(:));

    img_gray_normalized = imcomplement((edges_blurred_sat - min(edges_blurred_sat(:)))/(max(edges_blurred_sat(:)) - min(edges_blurred_sat(:))));
end

%% Horizontal/vertical histogram approach
% estimate spectra
seg_width = floor(width / params.num_seg_hor); % 150
seg_height = floor(height / params.num_seg_ver); % 100
switch params.hist_grid_det_method
    case 'REGULAR_TILING'
        segments_stacked = zeros(seg_height, seg_width, params.num_seg_hor * params.num_seg_ver);
        k = 1;
        for i = 1 : params.num_seg_ver
            for j = 1 : params.num_seg_hor
                segments_stacked(:, :, k) = img_gray_normalized((i -1)*seg_height + 1 : i*seg_height, (j -1)*seg_width + 1 : j*seg_width);
                k = k + 1;
            end
        end
    case 'RANDOM_TILING'
        segments_stacked = zeros(seg_height, seg_width, params.total_segments);
        for k = 1 : params.total_segments
            start_hor = randi(width - seg_width);
            start_ver = randi(height - seg_height);
            segments_stacked(:, :, k) = img_gray_normalized(start_ver : start_ver + seg_height-1, start_hor : start_hor + seg_width-1);
        end
end

grid_spacing_hor_all_seg = zeros(1, size(segments_stacked, 3));
grid_spacing_ver_all_seg = zeros(1, size(segments_stacked, 3));
for k = 1 : size(segments_stacked, 3)
    hist_hor = 1.0 - mean(segments_stacked(:, :, k), 2);
    min_grid_peak_prominence = prctile(hist_hor, params.min_grid_peak_prom_prctile) - min(hist_hor);
    [~, I_peaks_hor] = findpeaks(hist_hor, 'MinPeakDistance', params.min_grid_resolution, 'MinPeakProminence', min_grid_peak_prominence);
    grid_spacing_hor_all_seg(k) = mean(diff(I_peaks_hor));

    hist_ver = 1.0 - mean(segments_stacked(:, :, k), 1);
    min_grid_peak_prominence = prctile(hist_ver, params.min_grid_peak_prom_prctile) - min(hist_ver);
    [~, I_peaks_ver] = findpeaks(hist_ver, 'MinPeakDistance', params.min_grid_resolution, 'MinPeakProminence', min_grid_peak_prominence);
    grid_spacing_ver_all_seg(k) = mean(diff(I_peaks_ver));

    if params.detailed_plots > 1
        figure
        hold on
        nn = 1 : length(hist_hor);
        plot(nn, hist_hor)
        plot(nn(I_peaks_hor), peaks_hor, 'ro')
        grid

        figure
        hold on
        nn = 1 : length(hist_ver);
        plot(nn, hist_ver)
        plot(nn(I_peaks_ver), peaks_ver, 'ro')
        grid
    end
end
grid_size_hor = median(grid_spacing_hor_all_seg);
grid_size_ver = median(grid_spacing_ver_all_seg);


%% Plot results
if params.detailed_plots > 0
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

    figure
    subplot(121)
    histogram(grid_spacing_hor_all_seg)
    title('Histogram of horizontal grid spacing estimate of all segments')

    subplot(122)
    histogram(grid_spacing_ver_all_seg)
    title('Histogram of vertical grid spacing estimate of all segments')
end