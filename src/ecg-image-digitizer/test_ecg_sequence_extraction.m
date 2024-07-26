% Test script for image_to_sequence to convert ECG images into time-series
%
% This script reads ECG images and applies different methods provided by
% the image_to_sequence function to convert these images into time-series
% data. It processes each image using various sequence extraction methods
% and then visualizes the results for comparison.
% 
% Note: This method works on single-channel ECG or segments of ECG. For
% multichannel data, the leads should be separated before applying this
% function. To note, the function is only provided as proof-of-concept. A
% full ECG digitization pipeline requires additional elements.
%
% Reference:
%   Reza Sameni, 2023, ECG-Image-Kit: A toolkit for ECG image analysis.
%   Available at: https://github.com/alphanumericslab/ecg-image-kit
%
% Revision History:
%   2023: First release
%   2024: Added further comments and checks for files

clear
close all FORCE
clc

% Define the path to the folder containing ECG image segments
data_path = '../../sample-data/ecg-images/sample-segments/';

% Get a list of all files in the image folder
all_files = dir(fullfile(data_path, '*.*'));

% Loop over all files, reading and processing each image
for k = 1 : length(all_files)
    file_name = all_files(k).name;
    image_fname = fullfile(data_path, filesep, file_name);

    if isfile(image_fname)
        try
            % Read the image
            img = imread(image_fname);

            % Apply different sequence extraction methods to the image
            z0 = image_to_sequence(img, 'dark-foreground', 'max_finder', [], false);
            z1 = image_to_sequence(img, 'dark-foreground', 'hor_smoothing', 3);
            z2 = image_to_sequence(img, 'dark-foreground', 'all_left_right_neighbors');
            z3 = image_to_sequence(img, 'dark-foreground', 'combined_all_neighbors');
            z4 = image_to_sequence(img, 'dark-foreground', 'moving_average', 3);

            % Combine results from all methods. The median operator is used
            % to perform a type of voting between multiple algorithms.
            z_combined = median([z0 ; z1 ; z2 ; z3 ; z4], 1);

            % Prepare for plotting
            lgnd = {};
            nn = 1 : size(img, 2);
            img_height = size(img, 1);

            % Display the original image and overlay the extracted sequences
            figure
            imshow(img)
            hold on
            plot(nn, img_height - z0, 'linewidth', 3); lgnd = cat(2, lgnd, {'max_finder'});
            plot(nn, img_height - z1, 'linewidth', 3); lgnd = cat(2, lgnd, {'hor_smoothing'});
            plot(nn, img_height - z2, 'linewidth', 3); lgnd = cat(2, lgnd, {'all_left_right_neighbors'});
            plot(nn, img_height - z3, 'linewidth', 3); lgnd = cat(2, lgnd, {'combined_all_neighbors'});
            plot(nn, img_height - z4, 'linewidth', 3); lgnd = cat(2, lgnd, {'moving_average'});
            plot(nn, img_height - z_combined, 'linewidth', 3); lgnd = cat(2, lgnd, {'combined methods'});

            % Add legend and title
            legend(lgnd, 'interpreter', 'none');
            title(['Paper ECG vs recovered signal for: ', file_name]);
            set(gca, 'fontsize', 14)

            % Uncomment the following line to save the superposed image, if needed
            % saveas(gcf, [fname(1:end-4), '-rec.png']);

            close all FORCE

        catch
            warning(['File ', file_name, ' not an image, or processing failed'])
        end
    end
end
