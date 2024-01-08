% A test script for ecg_gridest_margdist and ecg_gridest_spectral - ECG grid
% size estimation using marginal distributions and spectra of the ECG images
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
dataset_description_fname = '../../sample-data/ecg-images/ecg-samples-metadata.csv';

dataset_description = readtable(dataset_description_fname);
img_fnames = dataset_description.fname;

for k = 1 : length(img_fnames) % Sweep over all or specific records
    RecordName = img_fnames{k};
    image_fname = fullfile(data_path, filesep, RecordName);
    try
        img = imread(image_fname);
    catch
        error(['image file ', image_fname, ' not found or readable by imread']);
    end
    
    %% Marginal distribution-based method
    % Setting all the parameters for ecg_gridest_margdist function
    params_margdist = struct;
    params_margdist.blur_sigma_in_inch = 1.0; % Blurring filter sigma in inches, used for shadow removal
    params_margdist.paper_size_in_inch = [11.0, 8.5]; % Paper size in inches, used for scaling the blurring filter
    params_margdist.remove_shadows = true; % Flag to remove shadows due to photography/scanning
    params_margdist.apply_edge_detection = false; % Flag to enable or disable edge detection prior to grid detection
    params_margdist.post_edge_det_gauss_filt_std = 0.01; % Standard deviation for Gaussian filter post edge detection in inch
    params_margdist.sat_densities = true; % Saturate densities or not
    params_margdist.sat_level_upper_prctile = 99.0; % Upper percentile for saturation level post blurring
    params_margdist.sat_level_lower_prctile = 1.0; % Lower percentile for saturation level post blurring
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
    params_spectral.paper_size_in_inch = [11.0, 8.5]; % Paper size in inches, used for scaling the blurring filter
    params_spectral.remove_shadows = true; % Flag to remove shadows due to photography/scanning
    params_spectral.apply_edge_detection = false; % Flag to enable or disable edge detection prior to grid detection
    params_spectral.post_edge_det_gauss_filt_std = 0.01; % Standard deviation for Gaussian filter post edge detection in inch
    params_spectral.sat_densities = true; % Saturate densities or not
    params_spectral.sat_level_upper_prctile = 99.0; % Upper percentile for saturation level post blurring
    params_spectral.sat_level_lower_prctile = 1.0; % Lower percentile for saturation level post blurring
    params_spectral.num_seg_hor = 4; % Number of horizontal segments for grid detection
    params_spectral.num_seg_ver = 4; % Number of vertical segments for grid detection
    params_spectral.spectral_tiling_method = 'RANDOM_TILING'; % Spectral tiling method ('REGULAR_TILING', 'RANDOM_TILING' or 'RANDOM_VAR_SIZE_TILING')
    params_spectral.total_segments = 100; % Total number of segments in 'RANDOM_TILING' method
    params_spectral.min_grid_resolution = 1; % Minimum grid resolution in pixels
    params_spectral.min_grid_peak_prominence = 1.0; % minimum grid peak prominence in the spectral domain in dB
    params_spectral.detailed_plots = 1; % Flag to enable or disable detailed plotting (0 for none, 1 for end results, 2 for all figures)
    [gridsize_hor_spectral, gridsize_ver_spectral] = ecg_gridest_spectral(img, params_spectral);
    
    disp(['Horizontal grid resolution estimate (margdist): ', num2str(gridsize_hor_margdist) ' pixels'])
    disp(['Vertical grid resolution estimate (margdist): ', num2str(gridsize_ver_margdist) ' pixels'])
    disp(['Horizontal grid resolution estimate (spectral): [', num2str(gridsize_hor_spectral) '] pixels'])
    disp(['Vertical grid resolution estimate (spectral): [', num2str(gridsize_ver_spectral) '] pixels'])
    disp('---');
    close all
end
