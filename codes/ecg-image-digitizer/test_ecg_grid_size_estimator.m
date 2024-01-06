% A test script for ecg_gridest_margdist - ECG grid size estimation using
% marginal distributions of the ECG images
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

data_path = './sample-ecg-images/';
dataset_description_fname = './sample-ecg-images/ecg-samples-metadata.csv';

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
    
    % Setting all the parameters for ecg_gridest_margdist function
    params = struct;
    params.blur_sigma_in_inch = 1.0; % Blurring filter sigma in inches, used for shadow removal
    params.paper_size_in_inch = [11.0, 8.5]; % Paper size in inches, used for scaling the blurring filter
    params.remove_shadows = true; % Flag to remove shadows due to photography/scanning
    params.apply_edge_detection = false; % Flag to enable or disable edge detection prior to grid detection
    params.post_edge_det_gauss_filt_std = 0.01; % Standard deviation for Gaussian filter post edge detection in inch
    params.sat_level_upper_prctile = 99.0; % Upper percentile for saturation level post blurring
    params.sat_level_lower_prctile = 1.0; % Lower percentile for saturation level post blurring
    params.num_seg_hor = 4; % Number of horizontal segments for grid detection
    params.num_seg_ver = 4; % Number of vertical segments for grid detection
    params.hist_grid_det_method = 'RANDOM_TILING'; % Method for histogram grid detection ('RANDOM_TILING' or 'REGULAR_TILING')
    params.total_segments = 100; % Total number of segments in 'RANDOM_TILING' method
    params.min_grid_resolution = 1; % Minimum grid resolution in pixels
    params.min_grid_peak_prom_prctile = 2.0; % Percentile for minimum grid peak prominence
    params.detailed_plots = 0; % Flag to enable or disable detailed plotting (0 for none, 1 for end results, 2 for all figures)
    params.cluster_peaks = true; % Flag to enable clustering of peaks in histograms
    params.max_clusters = 3; % Maximum number of clusters to consider in k-means clustering
    params.cluster_selection_method = 'GAP_MIN_VAR'; % Method for selecting clusters ('GAP_MIN_VAR' or 'MAX_AMP_PEAKS')
    params.avg_quartile = 50.0; % The middle quartile used for averaging the estimated grid gaps

    [grid_size_horizontal, grid_size_vertical, grid_spacings_horizontal, grid_spacing_vertical] = ecg_gridest_margdist(img, params);
    
    disp(['Horizontal grid resolution estimate: ', num2str(grid_size_horizontal) ' pixels'])
    disp(['Vertical grid resolution estimate: ', num2str(grid_size_vertical) ' pixels'])
end
