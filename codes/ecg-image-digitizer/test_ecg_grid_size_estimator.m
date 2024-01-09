% A test script for multiple ECG grid size estimation algorithms
%
% Reference:
%   Reza Sameni, 2023, ECG-Image-Kit: A toolkit for ECG image analysis.
%   Available at: https://github.com/alphanumericslab/ecg-image-kit
%
% Revision History:
%   2023: First release

clear
close all FORCE
clc

data_path = '../../sample-data/ecg-images/';

% Get a list of all files in the image folder.
all_files = dir(fullfile(data_path, '*.*'));

% Loop over all files, reading them in
for k = 1 : length(all_files)
    file_name = all_files(k).name;
    image_fname = fullfile(data_path, filesep, file_name);
    try
        img = imread(image_fname);

        %% estimate grid resolution based on paper-size
        paper_size = [11.0, 8.5];
        [coarse_grid_size_paper_based, fine_grid_size_paper_based] = ecg_grid_size_from_paper(img, paper_size(1), 'in');

        %% Marginal distribution-based method
        % Setting all the parameters for ecg_gridest_margdist function
        params_margdist = struct;
        params_margdist.blur_sigma_in_inch = 1.0; % Blurring filter sigma in inches, used for shadow removal
        params_margdist.paper_size_in_inch = paper_size; % Paper size in inches, used for scaling the blurring filter
        params_margdist.remove_shadows = true; % Flag to remove shadows due to photography/scanning
        params_margdist.apply_edge_detection = false; % Flag to enable or disable edge detection prior to grid detection
        params_margdist.post_edge_det_gauss_filt_std = 0.01; % Standard deviation for Gaussian filter post edge detection in inch
        params_margdist.post_edge_det_sat = true; % Saturate densities or not post edge detection
        params_margdist.sat_level_upper_prctile = 99.0; % Upper percentile for saturation level post blurring
        params_margdist.sat_level_lower_prctile = 1.0; % Lower percentile for saturation level post blurring
        params_margdist.sat_pre_grid_det = false; % Pre grid detection saturation
        params_margdist.sat_level_pre_grid_det = 0.7; % Saturation k-sigma before grid detection
        params_margdist.num_seg_hor = 4; % Number of horizontal segments for grid detection
        params_margdist.num_seg_ver = 4; % Number of vertical segments for grid detection
        params_margdist.hist_grid_det_method = 'RANDOM_TILING'; % Method for histogram grid detection ('RANDOM_TILING' or 'REGULAR_TILING')
        params_margdist.total_segments = 100; % Total number of segments in 'RANDOM_TILING' method
        params_margdist.min_grid_resolution = 1; % Minimum grid resolution in pixels
        params_margdist.min_grid_peak_prom_prctile = 2.0; % Percentile for minimum grid peak prominence
        params_margdist.cluster_peaks = true; % Flag to enable clustering of peaks in histograms
        params_margdist.max_clusters = 3; % Maximum number of clusters to consider in k-means clustering
        params_margdist.cluster_selection_method = 'GAP_MIN_VAR'; % Method for selecting clusters ('GAP_MIN_VAR' or 'MAX_AMP_PEAKS')
        params_margdist.avg_quartile = 50.0; % The middle quartile used for averaging the estimated grid gaps
        params_margdist.detailed_plots = 1; % Flag to enable or disable detailed plotting (0 for none, 1 for end results, 2 for all figures)
        [gridsize_hor_margdist, gridsize_ver_margdist, grid_spacings_hor, grid_spacing_ver] = ecg_gridest_margdist(img, params_margdist);

        %% Spectral-based method
        % Setting all the parameters for ecg_gridest_margdist function
        params_spectral = struct;
        params_spectral.blur_sigma_in_inch = 1.0; % Blurring filter sigma in inches, used for shadow removal
        params_spectral.paper_size_in_inch = paper_size; % Paper size in inches, used for scaling the blurring filter
        params_spectral.remove_shadows = true; % Flag to remove shadows due to photography/scanning
        params_spectral.apply_edge_detection = false; % Flag to enable or disable edge detection prior to grid detection
        params_spectral.post_edge_det_gauss_filt_std = 0.01; % Standard deviation for Gaussian filter post edge detection in inch
        params_spectral.post_edge_det_sat = false; % Saturate densities or not
        params_spectral.sat_level_upper_prctile = 99.0; % Upper percentile for saturation level post blurring
        params_spectral.sat_level_lower_prctile = 1.0; % Lower percentile for saturation level post blurring
        params_spectral.sat_pre_grid_det = false; % Pre grid detection saturation
        params_spectral.sat_level_pre_grid_det = 0.7; % Saturation k-sigma before grid detection
        params_spectral.num_seg_hor = 4; % Number of horizontal segments for grid detection
        params_spectral.num_seg_ver = 4; % Number of vertical segments for grid detection
        params_spectral.spectral_tiling_method = 'RANDOM_TILING'; % Spectral tiling method ('REGULAR_TILING', 'RANDOM_TILING' or 'RANDOM_VAR_SIZE_TILING')
        params_spectral.total_segments = 100; % Total number of segments in 'RANDOM_TILING' method
        params_spectral.min_grid_resolution = 1; % Minimum grid resolution in pixels
        params_spectral.min_grid_peak_prominence = 1.0; % minimum grid peak prominence in the spectral domain in dB
        params_spectral.detailed_plots = 1; % Flag to enable or disable detailed plotting (0 for none, 1 for end results, 2 for all figures)
        [gridsize_hor_spectral, gridsize_ver_spectral] = ecg_gridest_spectral(img, params_spectral);

        [~, closest_ind_hor] = min(abs(gridsize_hor_spectral - fine_grid_size_paper_based));
        [~, closest_ind_ver] = min(abs(gridsize_ver_spectral - fine_grid_size_paper_based));

        params_matchfilt = params_margdist;
        params_matchfilt.sat_pre_grid_det = true; % Pre grid detection saturation
        params_matchfilt.sat_level_pre_grid_det = 0.7; % Saturation k-sigma before grid detection
        params_matchfilt.total_segments = 10; % Total number of segments in 'RANDOM_TILING' method
        params_matchfilt.tiling_method = 'RANDOM_TILING'; % Segmentation and tiling method ('REGULAR_TILING' or 'RANDOM_TILING')
        [grid_sizes_matchedfilt, grid_size_prom_matchedfilt, mask_size_matchedfilt, matchedfilt_powers_avg, I_peaks_matchedfilt] = ecg_gridest_matchedfilt(img, params_matchfilt);

        disp(['Grid resolution estimate per 0.1mV x 40ms (paper size-based): ', num2str(fine_grid_size_paper_based) ' pixels'])
        disp(['Grid resolution estimates per 0.1mV x 40ms (matched filter-based): [', num2str(grid_sizes_matchedfilt) '] pixels'])

        disp(['Horizontal grid resolution estimate (margdist): ', num2str(gridsize_hor_margdist) ' pixels'])
        disp(['Vertical grid resolution estimate (margdist): ', num2str(gridsize_ver_margdist) ' pixels'])

        disp(['Horizontal grid resolution estimate (spectral): [', num2str(gridsize_hor_spectral) '] pixels'])
        disp(['Vertical grid resolution estimate (spectral): [', num2str(gridsize_ver_spectral) '] pixels'])

        disp(['Closest spectral horizontal grid resolution estimate from paper-based resolution (per 0.1mV x 40ms): ', num2str(gridsize_hor_spectral(closest_ind_hor)) ' pixels'])
        disp(['Closest spectral vertical grid resolution estimate from paper-based resolution (per 0.1mV x 40ms): ', num2str(gridsize_ver_spectral(closest_ind_ver)) ' pixels'])

        disp('---');

        close all
    catch
        % error(['image file ', image_fname, ' not found or readable by imread']);
    end
end
