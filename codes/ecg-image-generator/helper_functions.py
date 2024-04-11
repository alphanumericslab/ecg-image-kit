import os, sys, argparse
import numpy as np
from scipy.io import savemat, loadmat
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from math import ceil 
import wfdb
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

BIT_NAN_16 = -(2.**15)

def find_records(folder, output_dir):
    header_files = list()
    recording_files = list()

    for root, directories, files in os.walk(folder):
        files = sorted(files)
        for file in files:
            extension = os.path.splitext(file)[1]
            if extension == '.mat':
                record = os.path.relpath(os.path.join(root, file.split('.')[0] + '.mat'), folder)
                hd = os.path.relpath(os.path.join(root, file.split('.')[0] + '.hea'), folder)
                recording_files.append(record)
                header_files.append(hd)
            if extension == '.dat':
                record = os.path.relpath(os.path.join(root, file.split('.')[0] + '.dat'), folder)
                hd = os.path.relpath(os.path.join(root, file.split('.')[0] + '.hea'), folder)
                header_files.append(hd)
                recording_files.append(record)
    
    if recording_files == []:
        raise Exception("The input directory does not have any WFDB compatible ECG files, please re-check the folder!")


    for file in recording_files:
        f, ext = os.path.splitext(file)
        f1 = f.split('/')[:-1]
        f1 = '/'.join(f1)

        if os.path.exists(os.path.join(output_dir, f1)) == False:
            os.makedirs(os.path.join(output_dir, f1))

    return header_files, recording_files


def find_files(data_directory):
    header_files = list()
    recording_files = list()

    for f in sorted(os.listdir(data_directory)):

        if(os.path.isdir(os.path.join(data_directory, f))):
            
            for file in sorted(os.listdir(os.path.join(data_directory,f))):
                root, extension = os.path.splitext(file)
                
                if not root.startswith('.'):

                    if extension=='.mat':
                        header_file = os.path.join(os.path.join(data_directory,f), root + '.hea')
                        recording_file = os.path.join(os.path.join(data_directory,f), root + '.mat')

                        if os.path.isfile(header_file) and os.path.isfile(recording_file):
                            header_files.append(header_file)
                            recording_files.append(recording_file)

                    if extension=='.dat':
                        header_file = os.path.join(os.path.join(data_directory,f), root + '.hea')
                        recording_file = os.path.join(os.path.join(data_directory,f), root + '.dat')

                        if os.path.isfile(header_file) and os.path.isfile(recording_file):
                            header_files.append(header_file)
                            recording_files.append(recording_file)
                            
        else:

            root, extension = os.path.splitext(f)

            if not root.startswith('.'):
                #Based on the recording format, we save the file names differently
                if extension=='.mat':
                    header_file = os.path.join(data_directory, root + '.hea')
                    recording_file = os.path.join(data_directory, root + '.mat')
                    if os.path.isfile(header_file) and os.path.isfile(recording_file):
                        header_files.append(header_file)
                        recording_files.append(recording_file)

                if extension=='.dat':
                    header_file = os.path.join(data_directory, root + '.hea')
                    recording_file = os.path.join(data_directory, root + '.dat')
                    if os.path.isfile(header_file) and os.path.isfile(recording_file):
                        header_files.append(header_file)
                        recording_files.append(recording_file)

    return header_files, recording_files

def load_header(header_file):
    with open(header_file, 'r') as f:
        header = f.read()
    return header

# Load recording file as an array.
def load_recording(recording_file, header=None,key='val'):
    rootname,extension = os.path.splitext(recording_file)
    #Load files differently based on file format
    if extension=='.dat':
        recording = wfdb.rdrecord(rootname)
        return recording.p_signal
    if extension=='.mat':
        recording = loadmat(recording_file)[key]
    return recording

# Get leads from header.
def get_leads(header):
    leads = list()
    for i, l in enumerate(header.split('\n')):
        entries = l.split(' ')
        if i==0:
            num_leads = int(entries[1])
        elif i<=num_leads:
            leads.append(entries[-1])
        else:
            break
    return tuple(leads)

# Get frequency from header.
def get_frequency(header):
    frequency = None
    for i, l in enumerate(header.split('\n')):
        if i==0:
            try:
                frequency = l.split(' ')[2]
                if '/' in frequency:
                    frequency = float(frequency.split('/')[0])
                else:
                    frequency = float(frequency)
            except:
                pass
        else:
            break
    return frequency

# Get analog-to-digital converter (ADC) gains from header.
def get_adc_gains(header, leads):
    adc_gains = np.zeros(len(leads))
    for i, l in enumerate(header.split('\n')):
        entries = l.split(' ')
        if i==0:
            num_leads = int(entries[1])
        elif i<=num_leads:
            current_lead = entries[-1]
            if current_lead in leads:
                j = leads.index(current_lead)
                try:
                    adc_gains[j] = float(entries[2].split('/')[0])
                except:
                    pass
        else:
            break
    return adc_gains


def truncate_signal(signal,sampling_rate,length_in_secs):
    signal=signal[0:int(sampling_rate*length_in_secs)]
    return signal

def create_signal_dictionary(signal,full_leads):
    record_dict = {}
    for k in range(len(full_leads)):
        record_dict[full_leads[k]] = signal[k]
        
    return record_dict

def samples_to_volts(signal,adc_gain):
    signal_threshold = 10
    if(np.max(signal))>10:
        signal = signal/adc_gain
    return signal

def standardize_leads(full_leads):
    full_leads_array = np.asarray(full_leads)
    
    for i in np.arange(len(full_leads_array)):
        if(full_leads_array[i].upper() not in ('AVR','AVL','AVF')):
            full_leads_array[i] = full_leads_array[i].upper()
        else:
            if(full_leads_array[i].upper()=='AVR'):
                full_leads_array[i] = 'aVR'
            elif(full_leads_array[i].upper()=='AVL'):
                full_leads_array[i] = 'aVL'
            else:
                 full_leads_array[i] = 'aVF'
    return full_leads_array

def read_bounding_box_txt(filename):
    bbs = []

    with open(filename, 'r') as text_file:
        lines = text_file.readlines()
    
    for i, line in enumerate(lines):
        line = line.split('\n')[0]
        
        parts = line.split(',')
        x1 = float(parts[0])
        y1 = float(parts[1])
        x2 = float(parts[2])
        y2 = float(parts[3])
        try:
           label = float(parts[4])
        except ValueError:
            label = str(parts[4])

        box = BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2, label=label)
        bbs.append(box)

    return bbs

def write_bounding_box_txt(bboxes, filename):
    with open(filename, 'w') as text_file:
        for i in range(len(bboxes)):
            box = bboxes.bounding_boxes[i]
            x1 = box.x1
            y1 = box.y1
            x2 = box.x2
            y2 = box.y2
            label = box.label
            text_file.write(str(x1))
            text_file.write(',')
            text_file.write(str(y1))
            text_file.write(',')
            text_file.write(str(x2))
            text_file.write(',')
            text_file.write(str(y2))
            text_file.write(',')
            text_file.write(str(label))
            text_file.write('\n')


def convert_mm_to_volts(mm):
    return float(mm/10)

def convert_mm_to_seconds(mm):
    return float(mm*0.04)

def convert_inches_to_volts(inches):
    return float(inches*2.54)

def convert_inches_to_seconds(inches):
    return float(inches*1.016)

def write_wfdb_file(ecg_frame, filename, rate, header_file, write_dir, full_mode, mask_unplotted_samples):
    full_header = load_header(header_file)
    full_leads = get_leads(full_header)
    full_leads = standardize_leads(full_leads)

    lead_step = 10.0
    samples = len(ecg_frame[full_mode])
    array = np.zeros((1, samples))

    leads = []
    header_name, extn = os.path.splitext(header_file)
    header = wfdb.rdheader(header_name)

    for i, lead in enumerate(full_leads):
        leads.append(lead)
        if lead == full_mode:
            lead = 'full' + lead
        adc_gn = header.adc_gain[i]

        arr = ecg_frame[lead]
        arr = np.array(arr)
        arr[arr == np.nan] = BIT_NAN_16/adc_gn
        arr = arr.reshape((1, arr.shape[0]))
        array = np.concatenate((array, arr),axis = 0)
    
    head, tail  = os.path.split(filename)
    
    array = array[1:]
    wfdb.wrsamp(record_name = tail, 
                fs = rate, units = header.units,
                sig_name = leads, p_signal = array.T, fmt = header.fmt,
                adc_gain = header.adc_gain, baseline = header.baseline, 
                base_time = header.base_time, base_date = header.base_date, 
                write_dir = write_dir)
    
    with open(os.path.join(write_dir, tail + '.hea'), "a") as f:
        for line in header.comments:
            f.write("#" + line)
            f.write("\n")

        if mask_unplotted_samples:
            f.write("#mask_unplotted_samples: True")
            f.write("\n")
        else:
            f.write("#mask_unplotted_samples: False")
            f.write("\n")