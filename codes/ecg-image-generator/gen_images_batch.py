import os, sys, argparse
import random
import csv
import subprocess
from itertools import cycle
from scipy.stats import bernoulli
from helper_functions import find_records
import warnings
import wfdb
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
warnings.filterwarnings("ignore")

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_directory', type=str, required=True)
    parser.add_argument('-o', '--output_directory', type=str, required=True)
    parser.add_argument('-se', '--seed', type=int, required=False, default = -1)
    parser.add_argument('-l', '--link', type=str, required=False,default='')

    return parser

def run(args):
        P1 = ['150', '300', '200', '250']  # E.g., resolutions
        P2 = ['0', '1', '2']  # E.g., padding inches
        P3 = ['0', '1']  # E.g., random DC offset options
        P4 = [1, 3, 2, 5, 4] # Grid color
        P5 = [1, 0] #add header
        P6 = [3, 4, 5] #number of handwritten words
        P7 = [30, 50, 100, 70, 80] #x offset for hw
        P8 = [50, 80, 90, 40] # y offser for hw
        P9 = [0.4 , 0.3, 0.2] #handwritten size factor
        P10 = [90, 60, 20, 50, 40] #crease angle
        P11 = [5, 7, 9, 8, 10] #num creases horizontally
        P12 = [4, 9, 8, 10, 5] #num creases vertically
        P13 = [5, 10, 8] #rotation
        P14 = [12, 29, 37] #noise
        P15 = [0.01, 0.0005, 0.02] #crop 
        P16 = [1, 0] #hw  text
        P17 = [1, 0] #wrinkles
        P18 = [0, 1] #augment 
        P19  = [1, 0, 1, 1, 0] #random black and white
        P20 =   [2, 4, 3] #num_columns
        P21 = [1, 2, 3, 4] #long leads

        # Creating iterators using cycle for round-robin
        iter_P1 = cycle(P1)
        iter_P2 = cycle(P2)
        iter_P3 = cycle(P3)
        iter_P4 = cycle(P4)
        iter_P5 = cycle(P5)
        iter_P6 = cycle(P6)
        iter_P7 = cycle(P7)
        iter_P8 = cycle(P8)
        iter_P9 = cycle(P9)
        iter_P10 = cycle(P10)
        iter_P11 = cycle(P11)
        iter_P12 = cycle(P12)
        iter_P13 = cycle(P13)
        iter_P14 = cycle(P14)
        iter_P15 = cycle(P15)
        iter_P16 = cycle(P16)
        iter_P17 = cycle(P17)
        iter_P18 = cycle(P18)
        iter_P19 = cycle(P19)
        iter_P20 = cycle(P20)
        iter_P21 = cycle(P21)

        random.seed(args.seed)

        output_dir = args.output_directory
        if os.path.isabs(args.input_directory) == False:
            args.input_directory = os.path.normpath(os.path.join(os.getcwd(), args.input_directory))
        if os.path.isabs(args.output_directory) == False:
            original_output_dir = os.path.normpath(os.path.join(os.getcwd(), args.output_directory))
        else:
            original_output_dir = args.output_directory
        
        if os.path.exists(args.input_directory) == False or os.path.isdir(args.input_directory) == False:
            raise Exception("The input directory does not exist, Please re-check the input arguments!")

        if os.path.exists(original_output_dir) == False:
            os.makedirs(original_output_dir)

        i = 0
        full_header_files, full_recording_files = find_records(args.input_directory, original_output_dir)
        
        all_commands = []
        
        for full_header_file, full_recording_file in zip(full_header_files, full_recording_files):
            filename = full_recording_file
            header = full_header_file
            args.input_file = os.path.join(args.input_directory, filename)
            args.header_file = os.path.join(args.input_directory, header)
            args.start_index = -1
            _, fields = wfdb.rdsamp(os.path.splitext(args.header_file)[0])
            currentLeads = random.sample(fields['sig_name'], next(iter_P21))

            folder_struct_list = full_header_file.split('/')[:-1]
            args.output_directory = os.path.join(original_output_dir, '/'.join(folder_struct_list))

            random_add_header = next(iter_P5)          
            
            hw_text = next(iter_P16)
            wrinkles = next(iter_P17)
            augment = next(iter_P18)

            #Handwritten text addition
            if(hw_text):
                num_words = next(iter_P6)
                x_offset = next(iter_P7)
                y_offset = next(iter_P8)

            if(wrinkles):
                crease_angle = next(iter_P10)
                num_creases_vertically = next(iter_P11)
                num_creases_horizontally = next(iter_P12)

            
            if(augment):
                noise = next(iter_P14) 
                crop = next(iter_P15)
                blue_temp = random.choice((True,False))

                if(blue_temp):
                    temp = random.choice(range(2000,4000))
                else:
                    temp = random.choice(range(10000,20000))

            args_dict = dict()
            config_args = []
            args_dict["input_file"] = args.input_file
            args_dict["header_file"] = args.header_file
            args_dict["output_directory"] = args.output_directory
            args_dict["start_index"] = args.start_index
            args_dict["resolution"] = next(iter_P1)
            args_dict["pad_inches"] = next(iter_P2)
            args_dict["standard_grid_color"] = next(iter_P4)
            args_dict["store_config"] = 1
            args_dict["calibration_pulse"] = next(iter_P3)
            args_dict["random_bw"] = next(iter_P19)
            args_dict["num_columns"] = next(iter_P20)
            args_dict["full_mode"] = currentLeads

            if random_add_header == 1:
                config_args.append("print_header")

            config_args.append("lead_bbox")
            config_args.append("lead_name_bbox")
            
            if hw_text:
                config_args.append("hw_text")
                config_args.append("deterministic_num_words")
                config_args.append("deterministic_offset")
                args_dict["num_words"] = num_words
                args_dict["x_offset"] = x_offset
                args_dict["y_offset"] = y_offset
                args_dict["link"] = args.link
                args_dict["hws"] = next(iter_P9)

            if wrinkles:
                config_args.append("wrinkles")
                config_args.append("deterministic_angle")
                config_args.append("deterministic_vertical")
                config_args.append("deterministic_horizontal")
                args_dict["crease_angle"] = crease_angle
                args_dict["num_creases_vertically"] = num_creases_vertically
                args_dict["num_creases_horizontally"] = num_creases_horizontally
                
            if augment:
                config_args.append("augment")
                config_args.append("deterministic_noise")
                args_dict["noise"] = noise
                args_dict["rotate"] = next(iter_P13)
                args_dict["crop"] = crop

            command = ["python", "gen_ecg_image_from_data.py"]
            for key, value in args_dict.items():
                command.extend([f"--{key}", str(value)])

            for key in config_args:
                command.extend([f"--{key}"])
            all_commands.append(command)

        with open(os.path.join(output_dir, 'textfile.pkl'), 'wb') as f:  
            pickle.dump(all_commands, f)
                #subprocess.call(command, shell=True)   
                  

if __name__=='__main__':
    run(get_parser().parse_args(sys.argv[1:]))