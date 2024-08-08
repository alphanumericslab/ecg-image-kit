# This script generates a text file with a list of commands to process a list of ECG data files in WFDB format (.hea format)
# found in a specified input directory. These commands are designed for running the `ecg-image-gen` tool in the `ecg-image-kit`,
# which converts ECG time-series data into ECG images. Each command generated uses the `gen_ecg_images_from_data_batch.py`
# function within the `ecg-image-kit` and includes parameters for input and output file paths, as well as additional options
# selected in a round-robin fashion from predefined lists. The output of each command will be an image file (.png) name,
# representing the generated ECG image, stored in a corresponding structure in the output directory.
#
# This automation facilitates batch processing of multiple ECG data files, ensuring efficient and consistent image generation
# for large datasets. The round-robin selection of parameters allows for varied configurations across the dataset, useful
# for testing or data augmentation purposes.
#
# Author: Reza Sameni
# Date: Feb 2024
# Project: ECG-Image-Kit
# URL: https://github.com/alphanumericslab/ecg-image-kit

import os
from itertools import cycle

# Paths for the input and output root folders
root_input_path = '../../DataFiles/physionet.org/files/ptb-xl/'
root_output_path = '../../OutputFiles/physionet.org/files/ptb-xl/'

# The output file for commands
commands_file = './batch_commands.txt'

# Replace these lists with your actual lists (they don't need to be of the same length or unique. they may include repeated values for more prevalent options)
P1 = ['150', '200', '300', '200', '200', '200']  # E.g., resolutions
P2 = ['0', '0.1', '0.5']  # E.g., padding inches
P3 = ['0', '1', '1', '0', '1', '1']  # E.g., random DC offset options

# Creating iterators using cycle for round-robin
iter_P1 = cycle(P1)
iter_P2 = cycle(P2)
iter_P3 = cycle(P3)

with open(commands_file, 'w') as f_out:
    for root, dirs, files in os.walk(root_input_path):
        for file in files:
            if file.endswith('.hea'):
                full_input_path = os.path.join(root, file)
                
                # Constructing the relative output path
                relative_dir = os.path.relpath(root, root_input_path)
                output_dir = os.path.join(root_output_path, relative_dir)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # Constructing the output file name
                base_file_name = os.path.splitext(file)[0] + '.png'
                full_output_path = os.path.join(output_dir, base_file_name)

                # Constructing the command
                command = f"python gen_ecg_images_from_data_batch.py -i \"{full_input_path}\" -o \"{full_output_path}\" --print_header -r {next(iter_P1)} --pad_inches {next(iter_P2)} --random_dc {next(iter_P3)}"
                f_out.write(command + '\n')

print(f"Commands written to {commands_file}")
