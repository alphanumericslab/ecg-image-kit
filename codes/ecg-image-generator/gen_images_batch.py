import os, sys, argparse
import random
import csv
import subprocess
from itertools import cycle
from scipy.stats import bernoulli
from helper_functions import find_records
import warnings
import wfdb

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
warnings.filterwarnings("ignore")

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_directory', type=str, required=True)
    parser.add_argument('-o', '--output_directory', type=str, required=True)
    parser.add_argument('-se', '--seed', type=int, required=False, default = -1)
    parser.add_argument('--num_leads',type=str,default='twelve')
    parser.add_argument('--num_images',type=int,default = -1)
    
    #parser.add_argument('-r','--resolution',type=int,required=False,default = 200)
    #parser.add_argument('--pad_inches',type=int,required=False,default=0)
    #parser.add_argument('-ph','--print_header', action="store_true",default=False)
    #parser.add_argument('--full_mode', type=str,default='II')

    #parser.add_argument('--random_grid_color',action="store_true",default=False)
    #parser.add_argument('--standard_grid_color', type=int, default=5)
    #parser.add_argument('--random_bw',type=float,default=0)

    parser.add_argument('-l', '--link', type=str, required=False,default='')
    #parser.add_argument('-n','--num_words',type=int,required=False,default=5)
    #parser.add_argument('--x_offset',dest='x_offset',type=int,default = 30)
    #parser.add_argument('--y_offset',dest='y_offset',type=int,default = 30)
    #parser.add_argument('--hws',dest='handwriting_size_factor',type=float,default = 0.2)
    
    #parser.add_argument('-ca','--crease_angle',type=int,default=90)
    #parser.add_argument('-nv','--num_creases_vertically',type=int,default=10)
    #parser.add_argument('-nh','--num_creases_horizontally',type=int,default=10)

    #parser.add_argument('-rot','--rotate',type=int,default=0)
    #parser.add_argument('-noise','--noise',type=int,default=50)
    #parser.add_argument('-c','--crop',type=float,default=0.01)

    #parser.add_argument('--deterministic_offset',action="store_true",default=False)
    #parser.add_argument('--deterministic_num_words',action="store_true",default=False)
    #parser.add_argument('--deterministic_hw_size',action="store_true",default=False)

    #parser.add_argument('--deterministic_angle',action="store_true",default=False)
    #parser.add_argument('--deterministic_vertical',action="store_true",default=False)
    #parser.add_argument('--deterministic_horizontal',action="store_true",default=False)

    #parser.add_argument('--deterministic_rot',action="store_true",default=False)
    #parser.add_argument('--deterministic_noise',action="store_true",default=False)
    #parser.add_argument('--deterministic_crop',action="store_true",default=False)
    #parser.add_argument('--deterministic_temp',action="store_true",default=False)

    #parser.add_argument('--fully_random',action='store_true',default=False)
    #parser.add_argument('--hw_text',action='store_true',default=False)
    #parser.add_argument('--wrinkles',action='store_true',default=False)
    #parser.add_argument('--augment',action='store_true',default=False)
    #parser.add_argument('--bbox',action='store_true',default=False)

    return parser

def run(args):
        P1 = ['150', '300', '200', '250']  # E.g., resolutions
        P2 = ['0', '0.1', '0.5']  # E.g., padding inches
        P3 = ['0', '1']  # E.g., random DC offset options
        P4 = [1, 3, 2, 5, 4] # Grid color
        P5 = [1, 0] #add header
        P6 = [3, 4, 5] #number of handwritten words
        P7 = [30, 50, 100, 20, 70] #x offset for hw
        P8 = [50, 30, 70] # y offser for hw
        P9 = [0.1 , 0.3, 0.2] #handwritten size factor
        P10 = [90, 60, 20, 50, 40] #crease angle
        P11 = [5, 7, 9, 8, 10] #num creases horizontally
        P12 = [4, 9, 8, 10, 5] #num creases vertically
        P13 = [5, 10, 8] #rotation
        P14 = [12, 29, 37] #noise
        P15 = [0.01, 0.0005, 0.02] #crop 
        P16 = [1, 0] #hw  text
        P17 = [1, 0] #wrinkles
        P18 = [0, 1] #augment 
        P19  = [1, 0] #random black and white
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
        
        with open(os.path.join(args.output_directory, 'textfile.txt'), 'w') as f:
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

                command = "python gen_ecg_image_from_data.py --input_file " + args.input_file + " --header_file " + args.header_file + " --output_directory " + args.output_directory + " --start_index " + str(args.start_index)
                command += " --resolution " + str(next(iter_P1)) + " --pad_inches " + str(next(iter_P2)) + " --random_add_header " + str(random_add_header) + " --standard_grid_color " + str(next(iter_P4))
                command += " --lead_bbox "
                command += " --store_config " + str(1)
                command += " --lead_name_bbox "
                command += " --random_dc " + str(next(iter_P3)) + " --random_bw " + str(next(iter_P19)) 
                command += " --num_columns " + str(next(iter_P20)) 
                command += " --full_mode " 
                for lead in currentLeads:
                    command += lead + " "
                if hw_text:
                    command += " --hw_text "
                    command += " --deterministic_num_words --num_words " + str(num_words)
                    command += " --deterministic_offset --x_offset " + str(x_offset) + " --y_offset " + str(y_offset)
                    command += " --link " + str(args.link) + " --handwriting_size_factor " + str(next(iter_P9))
                if wrinkles:
                    command += " --wrinkles "
                    command += " --deterministic_angle --crease_angle " + str(crease_angle)
                    command += " --deterministic_vertical --num_creases_vertically " + str(num_creases_vertically)
                    command += " --deterministic_horizontal --num_creases_horizontally " + str(num_creases_horizontally)
                if augment:
                    command += " --augment "               
                    command += " --deterministic_noise --noise " + str(noise) 
                    command += " --crop " + str(crop) + " --rotate " + str(next(iter_P13))

                 
                command += '\n'
                f.write(command) 
                #subprocess.call(command, shell=True)   
                  

if __name__=='__main__':
    run(get_parser().parse_args(sys.argv[1:]))