import imageio
from PIL import Image
import argparse
import imgaug as ia
from imgaug import augmenters as iaa
import numpy as np
import matplotlib.pyplot as plt
import os, sys, argparse
import numpy as np
from scipy.io import savemat, loadmat
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from math import ceil 
import time
import random

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source_directory', type=str, required=True)
    parser.add_argument('-i', '--input_file', type=str, required=True)
    parser.add_argument('-o', '--output_directory', type=str, required=True)
    parser.add_argument('-r','--rotate',type=int,default=25)
    parser.add_argument('-n','--noise',type=int,default=25)
    parser.add_argument('-c','--crop',type=float,default=0.01)
    parser.add_argument('-t','--temperature',type=int,default=6500)
    return parser

# Main function for running augmentations
def get_augment(input_file,output_directory,rotate=25,noise=25,crop=0.01,temperature=6500,bbox=False):
    filename = input_file
    #Number of files in input directory
    image_path = filename
    if(bbox):
        boxed_file_head, boxed_file_ext = os.path.splitext(filename)
        boxed_file = boxed_file_head + '-boxed.png'
        image_boxed = imageio.imread(boxed_file,pilmode='RGB')
        images_boxed = [image_boxed]

    image = imageio.imread(image_path,pilmode='RGB')
    
    images = [image]
    rot = random.randint(-rotate, rotate)
    crop_sample = random.uniform(0, crop)
    #Augment in a sequential manner. Create an augmentation object
    seq = iaa.Sequential([
          iaa.Affine(rotate=rot),
          iaa.AdditiveGaussianNoise(scale=(noise, noise)),
          iaa.Crop(percent=crop_sample),
          iaa.ChangeColorTemperature(temperature)
          ])
    
   
    #Apply the sequential transform
    images_aug = seq(images=images)

    if(bbox):
        images_aug_boxed = seq(images=images_boxed)
        plt.imsave(fname=boxed_file,arr=images_aug_boxed[0])
    head, tail = os.path.split(filename)
    f = os.path.join(output_directory,tail)
    plt.imsave(fname=f,arr=images_aug[0])
    

    return f

