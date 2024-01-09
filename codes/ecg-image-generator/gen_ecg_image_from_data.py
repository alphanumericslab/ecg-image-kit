import os, sys, argparse
import random
import csv
import numpy as np
from scipy.stats import bernoulli
from helper_functions import find_files
from extract_leads import get_paper_ecg
from HandwrittenText.generate import get_handwritten
from CreasesWrinkles.creases import get_creased
from ImageAugmentation.augment import get_augment

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, required=True)
    parser.add_argument('-hea', '--header_file', type=str, required=True)
    parser.add_argument('-o', '--output_directory', type=str, required=True)
    parser.add_argument('-se', '--seed', type=int, required=False, default = -1)
    parser.add_argument('-st', '--start_index', type=int, required=True)
    parser.add_argument('--num_leads',type=str,default='twelve')
    
    parser.add_argument('-r','--resolution',type=int,required=False,default = 200)
    parser.add_argument('--pad_inches',type=int,required=False,default=0)
    parser.add_argument('--num_columns',type=int,default = -1)
    parser.add_argument('--full_mode', type=str,default='random')

    parser.add_argument('-l', '--link', type=str, required=False,default='https://www.physionet.org/content/ptbdb/1.0.0/')
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
    parser.add_argument('--random_dc',type=float,default=0)
    parser.add_argument('--random_grid_present',type=float,default=1)
    parser.add_argument('--random_print',type=float,default=0)
    parser.add_argument('--random_bw',type=float,default=0)
    parser.add_argument('--deterministic_lead',action="store_true",default=True)
    parser.add_argument('--store_text_bounding_box',action="store_true",default=False)
    parser.add_argument('--store_config',action="store_true",default=False)

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

def writeCSV(args):
    csv_file_path = os.path.join(args.output_directory,'Coordinates.csv')
    if os.path.isfile(csv_file_path) == False:
        with open (csv_file_path,'a') as ground_truth_file:
                writer = csv.writer(ground_truth_file)
                if args.start_index != -1:
                    writer.writerow(["Filename","class","x_center","y_center","width","height"])

    grid_file_path = os.path.join(args.output_directory,'gridsizes.csv')
    if os.path.isfile(grid_file_path) == False:
        with open (grid_file_path,'a') as gridsize_file:
            writer = csv.writer(gridsize_file)
            if args.start_index != -1:
                writer.writerow(["filename","xgrid","ygrid","lead_name","start","end"])

def run_single_file(args):  
        if args.seed != -1:
            random.seed(args.seed)

        filename = args.input_file
        header = args.header_file
        resolution = random.choice(range(50,args.resolution+1)) if (args.random_resolution) else args.resolution
        padding = random.choice(range(0,args.pad_inches+1)) if (args.random_padding) else args.pad_inches
        
        papersize = ''
        lead = args.deterministic_lead

        bernoulli_dc = bernoulli(args.random_dc)
        bernoulli_bw = bernoulli(args.random_bw)
        bernoulli_grid = bernoulli(args.random_grid_present)
        bernoulli_add_print = bernoulli(args.random_print)
        
        font = os.path.join('Fonts',random.choice(os.listdir("Fonts")))
        
        if(args.random_bw == 0):
            standard_colours = random.choice((True,False))
        else:
            standard_colours = False

        out_array = get_paper_ecg(input_file=filename,header_file=header, start_index=args.start_index, store_configs=args.store_config, store_text_bbox=args.store_text_bounding_box, output_directory=args.output_directory,resolution=resolution,papersize=papersize,add_lead_names=lead,add_dc_pulse=bernoulli_dc,add_bw=bernoulli_bw,show_grid=bernoulli_grid,add_print=bernoulli_add_print,pad_inches=padding,font_type=font,standard_colours=standard_colours,full_mode=args.full_mode,bbox = args.bbox, columns = args.num_columns, seed=args.seed)
        
        for out in out_array:
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
                num_words = args.num_words if (args.deterministic_num_words) else random.choice(range(2,args.num_words+1))
                x_offset = args.x_offset if (args.deterministic_offset) else random.choice(range(1,args.x_offset+1))
                y_offset = args.y_offset if (args.deterministic_offset) else random.choice(range(1,args.y_offset+1))
            
                out = get_handwritten(link=args.link,num_words=num_words,input_file=out,output_dir=args.output_directory,x_offset=x_offset,y_offset=y_offset,handwriting_size_factor=args.handwriting_size_factor,bbox = args.bbox)

            if(wrinkles):
                ifWrinkles = True
                ifCreases = True
                crease_angle = args.crease_angle if (args.deterministic_angle) else random.choice(range(0,args.crease_angle+1))
                num_creases_vertically = args.num_creases_vertically if (args.deterministic_vertical) else random.choice(range(1,args.num_creases_vertically+1))
                num_creases_horizontally = args.num_creases_horizontally if (args.deterministic_horizontal) else random.choice(range(1,args.num_creases_horizontally+1))
                out = get_creased(out,output_directory=args.output_directory,ifWrinkles=ifWrinkles,ifCreases=ifCreases,crease_angle=crease_angle,num_creases_vertically=num_creases_vertically,num_creases_horizontally=num_creases_horizontally,bbox = args.bbox)

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
            
                out = get_augment(out,output_directory=args.output_directory,rotate=args.rotate,noise=noise,crop=crop,temperature=temp,bbox = args.bbox, store_text_bounding_box = args.store_text_bounding_box)
       
        return len(out_array)

if __name__=='__main__':
    run_single_file(get_parser().parse_args(sys.argv[1:]))
