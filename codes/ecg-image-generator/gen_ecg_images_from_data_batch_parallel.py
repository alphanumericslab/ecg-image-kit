import os, sys, argparse
import random
import csv
from helper_functions import find_records
from gen_ecg_image_from_data import run_single_file
import warnings
from multiprocessing import Pool
import time
from tqdm import tqdm

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
warnings.filterwarnings("ignore")

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_directory', type=str, required=True)
    parser.add_argument('-o', '--output_directory', type=str, required=True)
    parser.add_argument('-se', '--seed', type=int, required=False, default = -1)
    parser.add_argument('--num_leads',type=str,default='twelve')
    parser.add_argument('--max_num_images',type=int,default = -1)
    parser.add_argument('--config_file', type=str, default='config.yaml')
    
    parser.add_argument('-r','--resolution',type=int,required=False,default = 200)
    parser.add_argument('--pad_inches',type=int,required=False,default=0)
    parser.add_argument('-ph','--print_header', action="store_true",default=False)
    parser.add_argument('--num_columns',type=int,default = -1)
    parser.add_argument('--full_mode', type=str,default='II')
    parser.add_argument('--mask_unplotted_samples', action="store_true", default=False)
    parser.add_argument('--add_qr_code', action="store_true", default=False)

    parser.add_argument('-l', '--link', type=str, required=False,default='')
    parser.add_argument('-n','--num_words',type=int,required=False,default=5)
    parser.add_argument('--x_offset',dest='x_offset',type=int,default = 30)
    parser.add_argument('--y_offset',dest='y_offset',type=int,default = 30)
    parser.add_argument('--hws',dest='handwriting_size_factor',type=float,default = 0.2)
    
    parser.add_argument('-ca','--crease_angle',type=int,default=90)
    parser.add_argument('-nv','--num_creases_vertically',type=int,default=10)
    parser.add_argument('-nh','--num_creases_horizontally',type=int,default=10)

    parser.add_argument('-rot','--rotate',type=int,default=0)
    parser.add_argument('-noise','--noise',type=int,default=50)
    parser.add_argument('-c','--crop',type=float,default=0.01)
    parser.add_argument('-t','--temperature',type=int,default=40000)

    parser.add_argument('--random_resolution',action="store_true",default=False)
    parser.add_argument('--random_padding',action="store_true",default=False)
    parser.add_argument('--random_grid_color',action="store_true",default=False)
    parser.add_argument('--standard_grid_color', type=int, default=5)
    parser.add_argument('--calibration_pulse',type=float,default=1)
    parser.add_argument('--random_grid_present',type=float,default=1)
    parser.add_argument('--random_print_header',type=float,default=0)
    parser.add_argument('--random_bw',type=float,default=0)
    parser.add_argument('--remove_lead_names',action="store_false",default=True)
    parser.add_argument('--lead_name_bbox',action="store_true",default=False)
    parser.add_argument('--store_config', type=int, nargs='?', const=1, default=0)

    parser.add_argument('--deterministic_offset',action="store_true",default=False)
    parser.add_argument('--deterministic_num_words',action="store_true",default=False)
    parser.add_argument('--deterministic_hw_size',action="store_true",default=False)

    parser.add_argument('--deterministic_angle',action="store_true",default=False)
    parser.add_argument('--deterministic_vertical',action="store_true",default=False)
    parser.add_argument('--deterministic_horizontal',action="store_true",default=False)

    parser.add_argument('--deterministic_rot',action="store_true",default=False)
    parser.add_argument('--deterministic_noise',action="store_true",default=False)
    parser.add_argument('--deterministic_crop',action="store_true",default=False)
    parser.add_argument('--deterministic_temp',action="store_true",default=False)

    parser.add_argument('--fully_random',action='store_true',default=False)
    parser.add_argument('--hw_text',action='store_true',default=False)
    parser.add_argument('--wrinkles',action='store_true',default=False)
    parser.add_argument('--augment',action='store_true',default=False)
    parser.add_argument('--lead_bbox',action='store_true',default=False)
    parser.add_argument('--store_mask',action='store_true',default=False)
    parser.add_argument('--cpu_count', type=int, default=os.cpu_count())

    return parser

def run_single_file_wrapper(args_tuple):
    # Unpack the arguments
    args, full_header_file, full_recording_file = args_tuple

    # Obtain the filename, header, and other arguments
    filename = full_recording_file
    header = full_header_file
    args.input_file = os.path.join(args.input_directory, filename)
    args.header_file = os.path.join(args.input_directory, header)
    args.start_index = -1
    folder_struct_list = full_header_file.split('/')[:-1]
    args.output_directory = os.path.join(args.original_output_dir, '/'.join(folder_struct_list))
    args.encoding = os.path.split(os.path.splitext(filename)[0])[1]

    # Run a single file and return the value outputted
    return run_single_file(args)

def run(args):
    random.seed(args.seed)
    if os.path.isabs(args.input_directory) == False:
        args.input_directory = os.path.normpath(os.path.join(os.getcwd(), args.input_directory))
    if os.path.isabs(args.output_directory) == False:
        args.original_output_dir = os.path.normpath(os.path.join(os.getcwd(), args.output_directory))
    else:
        args.original_output_dir = args.output_directory

    if not os.path.exists(args.input_directory) or not os.path.isdir(args.input_directory):
        raise Exception("The input directory does not exist, Please re-check the input arguments!")

    if not os.path.exists(args.original_output_dir):
        os.makedirs(args.original_output_dir)

    full_header_files, full_recording_files = find_records(args.input_directory, args.original_output_dir)
    
    # Ensure this argument is always False for this script otherwise it will crash
    args.hw_text = False

    # Create a list of tuples containing the arguments for each file
    args_list = [(args, full_header_files[i], full_recording_files[i]) for i in range(len(full_header_files))]
    
    # Create a pool of workers equal to the number of CPU cores
    with Pool(processes=args.cpu_count) as pool:
        # Use tqdm to create a progress bar for the map function
        for _ in tqdm(pool.imap_unordered(run_single_file_wrapper, args_list), total=len(args_list)):
            pass

if __name__=='__main__':
    start_time = time.time()
    path = os.path.join(os.getcwd(), sys.argv[0])
    parentPath = os.path.dirname(path)
    os.chdir(parentPath)
    run(get_parser().parse_args(sys.argv[1:]))

    end_time = time.time()

    # Calculate the execution time
    execution_time = end_time - start_time

    # Get the current working directory
    cwd = os.getcwd()

    # Create the output file path
    output_file = os.path.join(cwd, "execution_time.txt")

    # Write the execution time to the file
    with open(output_file, "a") as f:
        f.write(f"Execution time for {sys.argv[2]} to  {sys.argv[4]}: {execution_time} seconds")
        f.write("\n")

    print(f"Execution time: {execution_time} seconds")
    print(f"Execution time written to {output_file}")
