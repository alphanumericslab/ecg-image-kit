#!/usr/bin/env python
# Load libraries.
import os, sys, argparse
import json
import numpy as np
from scipy.io import savemat, loadmat
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from TemplateFiles.generate_template import generate_template
from math import ceil 
from helper_functions import get_adc_gains,get_frequency,get_leads,load_recording,load_header,find_files, truncate_signal, create_signal_dictionary, samples_to_volts, standardize_leads
from ecg_plot import ecg_plot
import wfdb
from PIL import Image, ImageDraw, ImageFont
from random import randint
import random


# Run script.
def get_paper_ecg(input_file,header_file,output_directory, seed, start_index = -1, store_configs=False, store_text_bbox=True,key='val',resolution=100,units='inches',papersize='',add_lead_names=True,add_dc_pulse=True,add_bw=True,show_grid=True,add_print=True,pad_inches=1,template_file=os.path.join('TemplateFiles','TextFile1.txt'),font_type=os.path.join('Fonts','Arial.ttf'),standard_colours=True,full_mode='II',bbox = False,columns=-1):

    # Extract a reduced-lead set from each pair of full-lead header and recording files.
    full_header_file = header_file
    full_recording_file = input_file
    full_header = load_header(full_header_file)
    full_leads = get_leads(full_header)
    num_full_leads = len(full_leads)

    # Update the header file
    full_lines = full_header.split('\n')

    # For the first line, update the number of leads.
    entries = full_lines[0].split()

    head, tail = os.path.split(full_header_file)

    output_header_file = os.path.join(output_directory, tail)
    with open(output_header_file, 'w') as f:
            f.write('\n'.join(full_lines))

    #Load the full-lead recording file, extract the lead data, and save the reduced-lead recording file.
    recording = load_recording(full_recording_file, full_header,key)
           
    # Get values from header
    rate = get_frequency(full_header)
    adc = get_adc_gains(full_header,full_leads)
    full_leads = standardize_leads(full_leads)

    if(len(full_leads)==2):
        full_mode = 'None'
        gen_m = 2
        if(columns==-1):
            columns = 1
    elif(len(full_leads)==12):
        gen_m = 12
        if full_mode not in full_leads:
            full_mode = random.choice(full_leads)
        else:
            full_mode = full_mode
        if(columns==-1):
            columns = 4
    else:
        gen_m = len(full_leads)
        columns = 4
        full_mode = 'None'

    template_name = 'custom_template.png'
    generate_template(full_header_file, font_type=font_type, mode=gen_m,template_file=template_name)

    if(recording.shape[0]>recording.shape[1]):
       recording = np.transpose(recording)

    if recording.shape[1]/rate < 10:
        return []

    record_dict = create_signal_dictionary(recording,full_leads)
   
    gain_index = 0
    center_function = lambda x: x - x.mean()

    ecg_frame = []
    end_flag = False
    start = 0
    lead_length_in_seconds = 10.0/columns
    next_lead_step = 10.0

    if start_index != -1:
        start = start_index
        #do something
        frame = {}
        gain_index = 0
        for key in record_dict:
                if(len(record_dict[key][start:])<int(rate*lead_length_in_seconds)):
                    end_flag = True
                else:
                    end = start + int(rate*lead_length_in_seconds)

                    if(key!='full'+full_mode):
                        frame[key] = samples_to_volts(record_dict[key][start:end],adc[gain_index])
                        frame[key] = center_function(frame[key])
                    if(full_mode!='None' and key==full_mode):
                        if(len(record_dict[key][start:])>int(rate*10)):
                            frame['full'+full_mode] = samples_to_volts(record_dict[key][start:(start+int(rate)*10)],adc[gain_index])
                            frame['full'+full_mode] = center_function(frame['full'+full_mode])
                        else:
                            frame['full'+full_mode] = samples_to_volts(record_dict[key][start:],adc[gain_index])
                            frame['full'+full_mode] = center_function(frame['full'+full_mode])
                    gain_index += 1
        ecg_frame.append(frame)

    else:
        while(end_flag==False):
            # To do : Incorporate column and ful_mode info
            frame = {}
            gain_index = 0
            for key in record_dict:
                if(len(record_dict[key][start:])<int(rate*lead_length_in_seconds)):
                    end_flag = True
                else:
                    end = start + int(rate*lead_length_in_seconds)

                    if(key!='full'+full_mode):
                        frame[key] = samples_to_volts(record_dict[key][start:end],adc[gain_index])
                        frame[key] = center_function(frame[key])
                    if(full_mode!='None' and key==full_mode):
                        if(len(record_dict[key][start:])>int(rate*10)):
                            frame['full'+full_mode] = samples_to_volts(record_dict[key][start:(start+int(rate)*10)],adc[gain_index])
                            frame['full'+full_mode] = center_function(frame['full'+full_mode])
                        else:
                            frame['full'+full_mode] = samples_to_volts(record_dict[key][start:],adc[gain_index])
                            frame['full'+full_mode] = center_function(frame['full'+full_mode])
                    gain_index += 1
            if(end_flag==False):
                ecg_frame.append(frame)
                start += int(rate*next_lead_step)

    outfile_array = []
        
    for i in range(len(ecg_frame)):
        dc = add_dc_pulse.rvs()
        bw = add_bw.rvs()
        grid = show_grid.rvs()
        print_txt = add_print.rvs()

        json_dict = {}
        grid_colour = 'colour'
        if(bw):
            grid_colour = 'bw'

        name, ext = os.path.splitext(full_header_file)
        rec_file = name + '-' + str(i)
        
        x_grid,y_grid = ecg_plot(ecg_frame[i], style=grid_colour, sample_rate = rate,columns=columns,rec_file_name = rec_file, output_dir = output_directory, resolution = resolution, pad_inches = pad_inches, lead_index=full_leads, full_mode = full_mode, store_text_bbox = store_text_bbox, show_lead_name=add_lead_names,show_dc_pulse=dc,papersize=papersize,show_grid=(grid),standard_colours=standard_colours,bbox=bbox)

        rec_head, rec_tail = os.path.split(rec_file)

        json_dict["x_grid"] = x_grid
        json_dict["y_grid"] = y_grid
        if store_text_bbox:
            json_dict["text_bounding_box_file"] = os.path.join(output_directory, 'text_bounding_box', rec_tail + '.txt')
        else:
            json_dict["text_bounding_box_file"] = ""
        if bbox:
            json_dict["lead_bounding_box_file"] = os.path.join(output_directory, 'lead_bounding_box', rec_tail + '.txt')
        else:
            json_dict["lead_bounding_box_file"] = ""

        if(print_txt):
            img_ecg = Image.open(os.path.join(output_directory,rec_tail+'.png'))
            
            img = Image.open(template_name)
            img = img.resize((int(img_ecg.size[0]/3),int(img_ecg.size[0]*img.size[1]/(3*img.size[0]))))
            img = np.asarray(img).copy()
            img[img!=255] = 0
            img[img==255] = 1
            img =  np.asarray(img)
            img_ecg = np.asarray(img_ecg).copy()
            

            im1 = img_ecg[:img.shape[0],:img.shape[1],:img.shape[2]] * img
            img_ecg[:img.shape[0],:img.shape[1],:img.shape[2]] = im1
            im = Image.fromarray(img_ecg)
            im.save(os.path.join(output_directory,rec_tail+'.png'))

        outfile = os.path.join(output_directory,rec_tail+'.png')
        
        json_object = json.dumps(json_dict, indent=4)
 
        # Writing to sample.json
        if store_configs:
            with open(os.path.join(output_directory,rec_tail+'.json'), "w") as f:
                f.write(json_object)

        outfile_array.append(outfile)

    os.remove(template_name)
    return outfile_array