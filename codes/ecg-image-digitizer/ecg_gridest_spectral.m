function [grid_size_hor, grid_size_ver] = ecg_gridest_spectral(img, varargin)
% ecg_gridest_spectral Estimates grid size in ECG images.
%
% This function analyzes an ECG image to estimate the grid size in both
% horizontal and vertical directions using a spectral approach. The image
% is segmentized into smaller regular or random patches, the 2D spectrum of
% the patches are estimated and averaged. The local peaks of the average
% spectra are used to estimate the potential grid resolutions (both
% horizontally and vertically), and returned as vectors.
% 
% Note: This function only detects regular grids. The returned values should
%   be evaluated based on the image DPI and ECG image style to map the grid
%   resolutions to physical time and amplitude units.
%
% Syntax:
%   [grid_sizes_hor, grid_sizes_ver] = ecg_gridest_spectral(img)
%   [grid_sizes_hor, grid_sizes_ver] = ecg_gridest_spectral(img, params)
%
% Inputs:
%   img - A 2D matrix representing the ECG image in grayscale or RGB formats.
%   params - (optional) A struct containing various parameters to control
%            the image processing and grid detection algorithm. Default
%            values are used if this argument is not provided. See function
%            for details
%
% Outputs:
%   grid_sizes_hor - A vector of estimated grid sizes in the horizontal
%       direction (in pixels), sorted in order of priminence
%   grid_sizes_ver - A vector of estimated grid sizes in the vertical
%       direction (in pixels), sorted in order of priminence
%
% Example:
%   % Load an ECG image
%   img = imread('path/to/ecg_image.jpg');
%
%   % Estimate grid size with default parameters
%   [gh, gv] = ecg_gridest_spectral(img);
%
%   % Estimate grid size with custom parameters
%   params = struct('spectral_tiling_method', 'RANDOM_TILING', 'remove_shadows', false);
%   [gh, gv] = ecg_gridest_spectral(img, params);
%
% Notes:
%   - The function requires Image Processing Toolbox for some operations.
%   - Edge detection is optional and can be controlled via the 'apply_edge_detection'
%     parameter in the params struct.
%   - The function uses spectral estimation for grid detection which is
%     more robust than marginal histogram-based methods. The reported
%     values may however be susceptible to image rotation.
%
% Reference:
%   Reza Sameni, 2023, ECG-Image-Kit: A toolkit for ECG image analysis.
%   Available at: https://github.com/alphanumericslab/ecg-image-kit
%
% Revision History:
%   2023: First release
%

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

if ~isfield(params, 'apply_edge_detection') || isempty(params.apply_edge_detection)
    params.apply_edge_detection = false; % detect grid on edge detection outputs
end

if params.apply_edge_detection
    if ~isfield(params, 'post_edge_det_gauss_filt_std') || isempty(params.post_edge_det_gauss_filt_std)
        params.post_edge_det_gauss_filt_std = 0.01; % post edge detection line smoothing
    end

    if ~isfield(params, 'sat_densities') || isempty(params.sat_densities)
        params.sat_densities = true; % saturate densities or not
    end
    if params.sat_densities
        if ~isfield(params, 'sat_level_upper_prctile') || isempty(params.sat_level_upper_prctile)
            params.sat_level_upper_prctile = 99.0; % upper saturation threshold after bluring
        end
        if ~isfield(params, 'sat_level_lower_prctile') || isempty(params.sat_level_lower_prctile)
            params.sat_level_lower_prctile = 1.0; % lower saturation threshold after bluring
        end
    end
end

if ~isfield(params, 'num_seg_hor') || isempty(params.num_seg_hor)
    params.num_seg_hor = 4;
end

if ~isfield(params, 'num_seg_ver') || isempty(params.num_seg_ver)
    params.num_seg_ver = 4;
end

if ~isfield(params, 'spectral_tiling_method') || isempty(params.spectral_tiling_method)
    params.spectral_tiling_method = 'RANDOM_TILING'; %'REGULAR_TILING', 'RANDOM_TILING', 'RANDOM_VAR_SIZE_TILING'
    if ~isfield(params, 'total_segments') || isempty(params.total_segments)
        params.total_segments = 100;
    end
end

if isequal(params.spectral_tiling_method, 'RANDOM_VAR_SIZE_TILING')
    if ~isfield(params, 'seg_width_rand_dev') || isempty(params.seg_width_rand_dev)
        params.seg_width_rand_dev = 0.1;
    end
    if ~isfield(params, 'seg_height_rand_dev') || isempty(params.seg_height_rand_dev)
        params.seg_height_rand_dev = 0.1;
    end
end

if ~isfield(params, 'min_grid_resolution') || isempty(params.min_grid_resolution)
    params.min_grid_resolution = 1; % in pixels
end

if ~isfield(params, 'min_grid_peak_prominence') || isempty(params.min_grid_peak_prominence)
    params.min_grid_peak_prominence = 1.0; % in dB
end

if ~isfield(params, 'detailed_plots') || isempty(params.detailed_plots)
    params.detailed_plots = 0;
end

if ~isfield(params, 'smooth_spectra') || isempty(params.smooth_spectra)
    params.smooth_spectra = true;
end

if params.smooth_spectra
    if ~isfield(params, 'gauss_win_sigma') || isempty(params.gauss_win_sigma)
        params.gauss_win_sigma = 0.3;
    end
end

if ~isfield(params, 'patch_avg_method') || isempty(params.patch_avg_method)
    params.patch_avg_method = 'MEDIAN'; % 'MEDIAN', 'MEAN'
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

    edges_blurred_sat = edges_blurred;
    % saturate extreme pixels
    if params.sat_densities
        % upper saturation level
        sat_level = prctile(edges_blurred(:), params.sat_level_upper_prctile);
        I_sat = edges_blurred > sat_level;
        edges_blurred_sat(I_sat) = sat_level;

        % lower saturation level
        sat_level = prctile(edges_blurred(:), params.sat_level_lower_prctile);
        I_sat = edges_blurred < sat_level;
        edges_blurred_sat(I_sat) = sat_level;
    end
    edges_blurred_sat = edges_blurred_sat / max(edges_blurred_sat(:));

    img_gray_normalized = imcomplement((edges_blurred_sat - min(edges_blurred_sat(:)))/(max(edges_blurred_sat(:)) - min(edges_blurred_sat(:))));
end

%% segmentize and estimate spectra
seg_width = floor(width / params.num_seg_hor);
seg_height = floor(height / params.num_seg_ver);
switch params.spectral_tiling_method
    case 'REGULAR_TILING' % regular tiling across the entire image
        if params.smooth_spectra % use a mask (2D window) to improve the spectra
            mask = fspecial('gaussian',[seg_height, seg_width], params.gauss_win_sigma * mean(seg_width, seg_height));
        else
            mask = ones(seg_height, seg_width);
        end
        spectra_stacked = zeros(seg_height, seg_width, params.num_seg_hor * params.num_seg_ver);
        k = 1;
        for i = 1 : params.num_seg_ver
            for j = 1 : params.num_seg_hor
                patch = img_gray_normalized((i -1)*seg_height + 1 : i*seg_height, (j -1)*seg_width + 1 : j*seg_width);
                spectra_stacked(:, :, k) = abs(fft2(mask .* patch)).^2 / (seg_width * seg_height); % estimate the spectrum
                k = k + 1;
            end
        end
    case 'RANDOM_TILING' % random segments across the entire image
        if params.smooth_spectra % use a mask (2D window) to improve the spectra
            mask = fspecial('gaussian',[seg_height, seg_width], params.gauss_win_sigma * mean(seg_width, seg_height));
        else
            mask = ones(seg_height, seg_width);
        end
        spectra_stacked = zeros(seg_height, seg_width, params.total_segments);
        for k = 1 : params.total_segments
            start_hor = randi(width - seg_width);
            start_ver = randi(height - seg_height);
            patch = img_gray_normalized(start_ver : start_ver + seg_height-1, start_hor : start_hor + seg_width-1);
            spectra_stacked(:, :, k) = abs(fft2(mask .* patch)).^2 / (seg_width * seg_height); % estimate the spectrum
        end
    case 'RANDOM_VAR_SIZE_TILING' % random and variable-size segments across the entire image
        spectra_stacked = zeros(seg_height, seg_width, params.total_segments);
        for k = 1 : params.total_segments
            seg_width_randomized = min(width - 1, seg_width + randi(ceil(params.seg_width_rand_dev*seg_width)));
            seg_height_randomized = min(height - 1, seg_height + randi(ceil(params.seg_height_rand_dev*seg_height)));
            if params.smooth_spectra % use a mask (2D window) to improve the spectra
                mask = fspecial('gaussian',[seg_height_randomized, seg_width_randomized], params.gauss_win_sigma * mean(seg_width_randomized, seg_height_randomized));
            else
                mask = ones(seg_height_randomized, seg_width_randomized);
            end
            start_hor = randi(width - seg_width_randomized);
            start_ver = randi(height - seg_height_randomized);
            patch = img_gray_normalized(start_ver : start_ver + seg_height_randomized-1, start_hor : start_hor + seg_width_randomized-1);
            spectra_stacked(:, :, k) = abs(fft2(mask .* patch, seg_height, seg_width)).^2 / (seg_height * seg_width); % estimate the spectrum
        end
end

%% Horizontal/vertical histogram approach
switch params.patch_avg_method
    case 'MEDIAN'
        spectral_avg = median(spectra_stacked, 3);
    case 'MEAN'
        spectral_avg = mean(spectra_stacked, 3);
end

spectral_avg_hor = 10*log10(mean(spectral_avg, 2));
spectral_avg_ver = 10*log10(mean(spectral_avg, 1))';

if 0
    % Remove the slow trend prior to peak detection using Tikhonov 
    % regularization. tikhonov_regularization() is availabe in the open-source
    % electrophysiological toolbox (OSET): https://github.com/alphanumericslab/OSET
    TikhonovOrder = 2;
    SmoothnessFactor = 1000;

    spectral_avg_hor_bl = tikhonov_regularization(spectral_avg_hor(:)', TikhonovOrder, SmoothnessFactor)';
    spectral_avg_hor_zm = spectral_avg_hor - spectral_avg_hor_bl;

    spectral_avg_ver_bl = tikhonov_regularization(spectral_avg_ver(:)', TikhonovOrder, SmoothnessFactor)';
    spectral_avg_ver_zm = spectral_avg_ver - spectral_avg_ver_bl;
else
    spectral_avg_hor_zm = spectral_avg_hor;
    spectral_avg_ver_zm = spectral_avg_ver;
end

%% estimate grid resolution
% find local spectral peaks
[~, I_pk_hor, ~, pk_prominence_hor] = findpeaks(spectral_avg_hor_zm, 'MinPeakDistance', params.min_grid_resolution, 'MinPeakProminence', params.min_grid_peak_prominence);
[~, I_pk_ver, ~, pk_prominence_ver] = findpeaks(spectral_avg_ver_zm, 'MinPeakDistance', params.min_grid_resolution, 'MinPeakProminence', params.min_grid_peak_prominence);

% limit range to Nyquist frequency
ff_hor = (0:length(spectral_avg_hor_zm) - 1) / length(spectral_avg_hor_zm);
ff_ver = (0:length(spectral_avg_ver_zm) - 1) / length(spectral_avg_ver_zm);

I_nyq = find(ff_hor(I_pk_hor) < 0.5, 1, 'last');
I_pk_hor = I_pk_hor(1 : I_nyq);
pk_prominence_hor = pk_prominence_hor(1 : I_nyq);

I_nyq = find(ff_ver(I_pk_ver) < 0.5, 1, 'last');
I_pk_ver = I_pk_ver(1 : I_nyq);
pk_prominence_ver = pk_prominence_ver(1 : I_nyq);

% sort spectral peaks in order of prominence in their neighborhood
[~, I_hor_sorted] = sort(pk_prominence_hor, 'descend');
grid_size_hor = 1./ff_hor(I_pk_hor(I_hor_sorted));

[~, I_ver_sorted] = sort(pk_prominence_ver, 'descend');
grid_size_ver = 1./ff_ver(I_pk_ver(I_ver_sorted));

%% Plot results
if params.detailed_plots > 0
    figure
    hold on
    plot(ff_hor, spectral_avg_hor_zm)
    if ~isempty(I_pk_hor)
        plot(ff_hor(I_pk_hor), spectral_avg_hor_zm(I_pk_hor), 'ro', 'markersize', 14)
        plot(ff_hor(I_pk_hor(I_hor_sorted(1))), spectral_avg_hor_zm(I_pk_hor(I_hor_sorted(1))), 'rx', 'markersize', 20)
    end
    plot(ff_ver, spectral_avg_ver_zm)
    if ~isempty(I_pk_ver)
        plot(ff_ver(I_pk_ver), spectral_avg_ver_zm(I_pk_ver), 'ko', 'markersize', 14)
        plot(ff_ver(I_pk_ver(I_ver_sorted(1))), spectral_avg_ver_zm(I_pk_ver(I_ver_sorted(1))), 'kx', 'markersize', 20)
    end
    grid
    title('Average spectral estimate across image patches')
    xlabel('Grid repetition frequency (inverse of grid period in pixels)')
    ylabel('Amplitude (dB)')

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

%% prominence calculation code (used during development):
% pk_hor = pk_hor(1 : I_nyq);
% pk_prominence_hor = zeros(1, length(I_pk_hor));
% for p = 1 : length(I_pk_hor)
%     if p == 1
%         start = 1;
%     else
%         start = I_pk_hor(p-1) + 1;
%     end
%
%     if p == length(I_pk_hor)
%         stop = round(length(spectral_avg_hor_zm)/2);
%     else
%         stop = I_pk_hor(p+1) - 1;
%     end
%
%     pk_prominence_hor(p) = pk_hor(p) - min(spectral_avg_hor_zm(start:stop));
% end
% pk_ver = pk_ver(1 : I_nyq);
% pk_prominence_ver = zeros(1, length(I_pk_ver));
% for p = 1 : length(I_pk_ver)
%     if p == 1
%         start = 1;
%     else
%         start = I_pk_ver(p-1) + 1;
%     end
%
%     if p == length(I_pk_ver)
%         stop = round(length(spectral_avg_ver_zm)/2);
%     else
%         stop = I_pk_ver(p+1) - 1;
%     end
%
%     pk_prominence_ver(p) = pk_ver(p) - min(spectral_avg_ver_zm(start:stop));
% end
