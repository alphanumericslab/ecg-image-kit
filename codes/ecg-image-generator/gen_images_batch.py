import os, sys, argparse
import random
import csv
import subprocess
from itertools import cycle
from scipy.stats import bernoulli
from helper_functions import find_records
import warnings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
warnings.filterwarnings("ignore")

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_directory', type=str, required=True)
    parser.add_argument('-o', '--output_directory', type=str, required=True)
    parser.add_argument('-se', '--seed', type=int, required=False, default = -1)
    parser.add_argument('--num_leads',type=str,default='twelve')
    parser.add_argument('--num_images',type=int,default = -1)
    
    parser.add_argument('-r','--resolution',type=int,required=False,default = 200)
    parser.add_argument('--pad_inches',type=int,required=False,default=0)
    parser.add_argument('-ph','--print_header', action="store_true",default=False)
    parser.add_argument('--num_columns',type=int,default = -1)
    parser.add_argument('--full_mode', type=str,default='II')

    parser.add_argument('--random_resolution',action="store_true",default=False)
    parser.add_argument('--random_padding',action="store_true",default=False)
    parser.add_argument('--random_grid_color',action="store_true",default=False)
    parser.add_argument('--standard_grid_color', type=int, default=5)
    parser.add_argument('--random_dc',type=float,default=0)
    parser.add_argument('--random_grid_present',type=float,default=1)
    parser.add_argument('--random_add_header',type=float,default=0)
    parser.add_argument('--random_bw',type=float,default=0)
    parser.add_argument('--deterministic_lead',action="store_false",default=True)
    parser.add_argument('--store_text_bounding_box',action="store_true",default=False)
    parser.add_argument('--store_config',action="store_true",default=False)

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
    parser.add_argument('--bbox',action='store_true',default=False)

    return parser

def run(args):
        P1 = ['150', '200', '300', '200', '200', '200']  # E.g., resolutions
        P2 = ['0', '0.1', '0.5']  # E.g., padding inches
        P3 = ['0', '1', '1', '0', '1', '1']  # E.g., random DC offset options

        # Creating iterators using cycle for round-robin
        iter_P1 = cycle(P1)
        iter_P2 = cycle(P2)
        iter_P3 = cycle(P3)

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

                folder_struct_list = full_header_file.split('/')[:-1]
                args.output_directory = os.path.join(original_output_dir, '/'.join(folder_struct_list))
                
                resolution = random.choice(range(50,args.resolution+1)) if (args.random_resolution) else args.resolution
                pad_inches = random.choice(range(0,args.pad_inches+1)) if (args.random_padding) else args.pad_inches
                
                papersize = ''
                lead = args.deterministic_lead

                if args.print_header:
                    random_add_header = 1
                else:
                    random_add_header = args.random_add_header                
                
                
                if(args.fully_random):
                    hw_text = random.choice((True,False))
                    wrinkles = random.choice((True,False))
                    augment = random.choice((True,False))
                else:
                    hw_text = args.hw_text
                    wrinkles = args.wrinkles
                    augment = args.augment

                #Handwritten text addition
                if(hw_text):
                    num_words = args.num_words 
                    x_offset = args.x_offset 
                    y_offset = args.y_offset 

                if(wrinkles):
                    ifWrinkles = True
                    ifCreases = True
                    crease_angle = args.crease_angle if (args.deterministic_angle) else random.choice(range(0,args.crease_angle+1))
                    num_creases_vertically = args.num_creases_vertically if (args.deterministic_vertical) else random.choice(range(1,args.num_creases_vertically+1))
                    num_creases_horizontally = args.num_creases_horizontally if (args.deterministic_horizontal) else random.choice(range(1,args.num_creases_horizontally+1))

                
                if(augment):
                    noise = args.noise if (args.deterministic_noise) else random.choice(range(1,args.noise+1))
                
                    if(not args.bbox):
                        do_crop = random.choice((True,False))
                        if(do_crop):
                            crop = args.crop
                        else:
                            crop = args.crop
                    else:
                        crop = 0
                    blue_temp = random.choice((True,False))

                    if(blue_temp):
                        temp = random.choice(range(2000,4000))
                    else:
                        temp = random.choice(range(10000,20000))

                command = "python gen_ecg_image_from_data.py --input_file " + args.input_file + " --header_file " + args.header_file + " --output_directory " + args.output_directory + " --start_index " + str(args.start_index)
                command += " --resolution " + str(next(iter_P1)) + " --pad_inches " + str(next(iter_P2)) + " --random_add_header " + str(random_add_header) + " --num_columns " + str(args.num_columns) + " --full_mode " + args.full_mode + " --standard_grid_color " + str(args.standard_grid_color)
                if lead:
                    command += " --deterministic_lead "
                if args.store_text_bounding_box:
                    command += " --store_text_bounding_box "
                if args.store_config:
                    command += " --store_config "
                if args.random_grid_color:
                    command += " --random_grid_color "
                if args.bbox:
                    command += " --bbox "
                command += " --random_dc " + str(next(iter_P3)) + " --random_bw " + str(args.random_bw) + " --random_grid_present " + str(args.random_grid_present)
                if hw_text:
                    command += " --hw_text "
                if wrinkles:
                    command += " --wrinkles "
                if augment:
                    command += " --augment "
                
                #HW text
                if args.deterministic_num_words:
                    command += " --deterministic_num_words --num_words " + str(num_words)
                if args.deterministic_offset:
                    command += " --deterministic_offset --x_offset " + str(x_offset) + " --y_offset " + str(y_offset)
                command += " --link " + str(args.link) + " --handwriting_size_factor " + str(args.handwriting_size_factor)

                #Creases and wrinkles
                if args.deterministic_angle:
                    command += " --deterministic_angle --crease_angle " + str(args.crease_angle)
                if args.deterministic_vertical:
                    command += " --deterministic_vertical --num_creases_vertically " + str(args.num_creases_vertically)
                if args.deterministic_horizontal:
                    command += " --deterministic_horizontal --num_creases_horizontally " + str(args.num_creases_horizontally)

                #Augment
                if args.deterministic_noise:
                    command += " --deterministic_noise --noise " + str(args.noise) 
                command += " --crop " + str(args.crop) + " --rotate " + str(args.rotate)

                 
                command += '\n'
                f.write(command) 
                #subprocess.call(command, shell=True)   
                  

if __name__=='__main__':
    run(get_parser().parse_args(sys.argv[1:]))
