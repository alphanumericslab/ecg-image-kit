import cv2
import numpy as np
import math
import skimage.exposure
import random
import imageio
import imutils
import argparse
import imgaug as ia
from imgaug import augmenters as iaa
import matplotlib.pyplot as plt
import os, sys, argparse
from scipy.io import savemat, loadmat
from skimage import util
from PIL import Image
from math import ceil 
import heapq
import time

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',dest='source_dir',type=str,required=True)
    parser.add_argument('-i', '--input_file', type=str, required=True)
    parser.add_argument('-o', '--output_directory', type=str, required=True)
    parser.add_argument('--wrinkles',action='store_true',default=False)
    parser.add_argument('--creases',action='store_true',default=False)
    parser.add_argument('-ca','--crease_angle',type=int,default=0)
    parser.add_argument('-nv','--num_creases_vertically',type=int,default=3)
    parser.add_argument('-nh','--num_creases_horizontally',type=int,default=2)
    return parser

#Select a random patch of block size from the given texture image
def randomPatch(texture, block_size):
    h, w, _ = texture.shape
    #Choose a random i and j to sample block from
    i = random.randint(h - block_size)
    j = random.randint(w - block_size)
    return texture[i:i+block_size, j:j+block_size]

#Find the overlap difference
def L2OverlapDiff(patch, block_size, overlap, res, y, x):
    error = 0
    if x > 0:
        left = patch[:, :overlap] - res[y:y+block_size, x:x+overlap]
        error += np.sum(left**2)

    if y > 0:
        up   = patch[:overlap, :] - res[y:y+overlap, x:x+block_size]
        error += np.sum(up**2)

    if x > 0 and y > 0:
        corner = patch[:overlap, :overlap] - res[y:y+overlap, x:x+overlap]
        error -= np.sum(corner**2)

    return error
 
#Given overlap find the block that gives least difference
def randomBestPatch(texture, block_size, overlap, res, y, x):
    h, w, _ = texture.shape
    errors = np.zeros((h - block_size, w - block_size))

    #Traverse through each block an calculate the overlap difference
    for i in range(h - block_size):
        for j in range(w - block_size):
            patch = texture[i:i+block_size, j:j+block_size]
            e = L2OverlapDiff(patch, block_size, overlap, res, y, x)
            errors[i, j] = e

    #Unravel to return block with least error
    i, j = np.unravel_index(np.argmin(errors), errors.shape)
    return texture[i:i+block_size, j:j+block_size]


def minCutPath(errors):
    # dijkstra's algorithm vertical
    pq = [(error, [i]) for i, error in enumerate(errors[0])]
    heapq.heapify(pq)

    h, w = errors.shape
    seen = set()

    while pq:
        error, path = heapq.heappop(pq)
        curDepth = len(path)
        curIndex = path[-1]

        if curDepth == h:
            return path

        for delta in -1, 0, 1:
            nextIndex = curIndex + delta

            if 0 <= nextIndex < w:
                if (curDepth, nextIndex) not in seen:
                    cumError = error + errors[curDepth, nextIndex]
                    heapq.heappush(pq, (cumError, path + [nextIndex]))
                    seen.add((curDepth, nextIndex))

# Finding the patch with least overlap diff as the mincut patch                 
def minCutPatch(patch, block_size, overlap, res, y, x):
    patch = patch.copy()
    dy, dx, _ = patch.shape
    minCut = np.zeros_like(patch, dtype=bool)

    if x > 0:
        left = patch[:, :overlap] - res[y:y+dy, x:x+overlap]
        leftL2 = np.sum(left**2, axis=2)
        for i, j in enumerate(minCutPath(leftL2)):
            minCut[i, :j] = True

    if y > 0:
        up = patch[:overlap, :] - res[y:y+overlap, x:x+dx]
        upL2 = np.sum(up**2, axis=2)
        for j, i in enumerate(minCutPath(upL2.T)):
            minCut[:i, j] = True

    np.copyto(patch, res[y:y+dy, x:x+dx], where=minCut)

    return patch

#Main function for image quilting
def quilt(image_path, block_size, num_block, mode, sequence=False):
    texture = Image.open(image_path)
    texture = util.img_as_float(texture)
    overlap = block_size // 6
    num_blockHigh, num_blockWide = num_block

    h = (num_blockHigh * block_size) - (num_blockHigh - 1) * overlap
    w = (num_blockWide * block_size) - (num_blockWide - 1) * overlap

    res = np.zeros((h, w, texture.shape[2]))

    #Loop to find random best patch that has minimum cut
    for i in range(num_blockHigh):
        for j in range(num_blockWide):
            y = i * (block_size - overlap)
            x = j * (block_size - overlap)
            patch = randomBestPatch(texture, block_size, overlap, res, y, x)
            
            patch = minCutPatch(patch, block_size, overlap, res, y, x)
            res[y:y+block_size, x:x+block_size] = patch

    image = (res * 255).astype(np.uint8)
    return image

#Function to compute coordinates of crease lines
def getCoords(angle,n,hh,ww):
    #Case when number of creases is 0
    if(n==0):
        return [[]],[[]]
    #Gap needed between lines would be the gap when lines are split among heights and weight of the image
    gap = int((hh+ww)/(n+1))
    
    #Coords1 refer to x and y coordinates of first point. Coords2 refer to x and y coordinates of second point.
    coords1 = []
    coords2 = []

    #Nested if else to handle different cases of angle
    if(angle<90 and angle!=0):
        #Divide the height and width of the image among n segments
        yc = 0
        xc = 0
        flag = 0
        for i in range(0,n):
            #Once xc+gap exceeds width of the image the lines will begin from the y axis. We track this with a flag
            if((xc+gap)<ww):
                xc = xc+ gap
            else:
                if(flag==0):
                    yc = xc + gap - ww
                    xc = ww 
                    flag = 1
                else:
                    yc = yc+ gap
                    xc = ww
            coord = [int(xc),int(yc)]
            coords1.append(coord)
    #If angle is 90 we just divide segments across the x axis
    elif(angle==90):
        yc = 0
        xc = 0
        gap = ww/(n+1)
        for i in range(0,n):
            xc = xc+gap
            coord = [int(xc),int(yc)]
            coords1.append(coord)
    #If angle is 180 or 0 we just divide segments across the y axis
    elif(angle==180 or angle==0):
        gap = hh/(n+1)
        xc = 0
        yc = 0
        for i in range(0,n):
            yc = yc+gap
            coord = [int(xc),int(yc)]
            coords1.append(coord)
    #If angle is greater than 90 then first start drawing lines from the y axis and then compute the x coordinates
    else:
        xc = 0
        yc = hh
        flag = 0
        for i in range(0,n):
            if((xc+gap)<ww):
                xc = xc + gap
            else:
                if(flag==0):
                    yc = (yc-(xc + gap - hh))
                    xc = ww
                    flag = 1
                else:
                    yc = yc - gap
                    xc = ww
            coord = [int(xc),int(yc)]
            coords1.append(coord)
    #Once the x and y coordinates of the starting point of the line are computed, compute the end point from slope
    for i in range(len(coords1)):
        x = coords1[i][0]
        y = coords1[i][1]
        m= np.tan((180-angle)*np.pi/180)
        c = int(y - m*x)
        #Computing end point from slope intercept form
        if(angle>90):
            if(c<0):
                yc = 0
                xc = int(-c/m)
            else:
                xc = ww
                yc = int(m*xc + c)
        #If angle is 90 we cannot use slope intercept form. We directly compute the end point coordinates
        elif (angle==90):
            yc = hh
            xc = (i+1)*(ww/(n+1))
        #If angle is 180 or 0, we again cannot compute end points using slope intercept form. We compute coordinates directly by division
        elif (angle==180 or angle==0):
            yc = (i+1)*(hh/(n+1))
            xc = ww
        #If angle is greater than 90 use slope intercept form
        else:
            if(c>hh):
                yc = hh
                xc = (yc - c)/m
            else:
                xc = 0
                yc = c
        coord = [int(xc),int(yc)]
        coords2.append(coord)
    return coords1,coords2

#Main fnction to apply wrinkles and creases
def get_creased(input_file,output_directory,ifWrinkles=False,ifCreases=False,crease_angle=0,num_creases_vertically=3,num_creases_horizontally=2,bbox=False):
    filename = input_file

    if(ifWrinkles):
    #Seed with a different selection of a wrinkle image
    # read wrinkle image as grayscale and convert to float in range 0 to 1
        wrinkle_file_name = os.path.join(os.path.join('CreasesWrinkles','wrinkles-dataset') , random.choice(os.listdir(os.path.join('CreasesWrinkles','wrinkles-dataset'))))
        wrinklesImg = quilt(wrinkle_file_name,250,(1,1),'Cut')
        wrinklesImg=cv2.cvtColor(wrinklesImg, cv2.COLOR_BGR2GRAY)
        wrinklesImg = wrinklesImg.astype("float32") / 255.0

    img_path = filename
    img = cv2.imread(img_path).astype("float32") / 255.0
    
    hh, ww = img.shape[:2]

    if ifWrinkles:
    # resize wrinkles to same size as ecg input image
        wrinkles = cv2.resize(wrinklesImg, (ww,hh), fx=0, fy=0)
        # shift image brightness so mean is (near) mid gray
        mean = np.mean(wrinkles)
        shift = mean - 0.4
        wrinkles = cv2.subtract(wrinkles, shift)
        
    if(ifCreases):
    # draw creases as blurred lines on black background
    # Compute coordinates of crease lines
        coords1,coords2 = getCoords(crease_angle,num_creases_horizontally,hh,ww)
        coords3,coords4 = getCoords(90+crease_angle,num_creases_vertically,hh,ww)
            
        creases = np.full((hh,ww),1, dtype=np.float32)
        if(num_creases_horizontally!=0):
           for i in range(len(coords1)):
            x1 = coords1[i][0]
            x2 = coords2[i][0]
            y1 = coords1[i][1]
            y2 = coords2[i][1]
            #Drawing lines
            if((x1-10)<0):
                cv2.line(creases,(x1,y1) , (x2,y2),1.25, 5)
                cv2.line(creases,(x1,y1-5) , (x2,y2-5),1.15, 5)
                cv2.line(creases,(x1,y1 + 5) , (x2,y2+5),1.15, 5)
                cv2.line(creases,(x1,y1+10) , (x2,y2+10),1.05, 5)
                cv2.line(creases,(x1,y1-10) , (x2,y2-10),1.05, 5)
            else:
                cv2.line(creases,(x1,y1) , (x2,y2),1.25, 5)
                cv2.line(creases,(x1-5,y1) , (x2-5,y2),1.15, 5)
                cv2.line(creases,(x1+5,y1) , (x2+5,y2),1.15, 5)
                cv2.line(creases,(x1-10,y1) , (x2-10,y2),1.05, 5)
                cv2.line(creases,(x1+10,y1) , (x2+10,y2),1.05, 5)
            #Drawing lines
        if(num_creases_vertically!=0):
            for i in range(len(coords3)):
                x1 = coords3[i][0]
                x2 = coords4[i][0]
                y1 = coords3[i][1]
                y2 = coords4[i][1]
                if((x1-10)<0):
                    cv2.line(creases,(x1,y1) , (x2,y2),1.25, 5)
                    cv2.line(creases,(x1,y1-5) , (x2,y2-5),1.15, 5)
                    cv2.line(creases,(x1,y1 + 5) , (x2,y2+5),1.15, 5)
                    cv2.line(creases,(x1,y1+10) , (x2,y2+10),1.05, 5)
                    cv2.line(creases,(x1,y1-10) , (x2,y2-10),1.05, 5)
                else:
                    cv2.line(creases,(x1,y1) , (x2,y2),1.25, 5)
                    cv2.line(creases,(x1-5,y1) , (x2-5,y2),1.15, 5)
                    cv2.line(creases,(x1+5,y1) , (x2+5,y2),1.15, 5)
                    cv2.line(creases,(x1-10,y1) , (x2-10,y2),1.05, 5)
                    cv2.line(creases,(x1+10,y1) , (x2+10,y2),1.05, 5)
        #Blur folds and crease array
        folds_creases = cv2.GaussianBlur(creases, (3,3), 0)
        folds_creases = cv2.cvtColor(folds_creases,cv2.COLOR_GRAY2BGR)
        #Apply folds and crease mask
        img = (img*folds_creases)
        
            
    # If wrinkles need to be added, add the wrinkles mask
    if ifWrinkles:
        transform = wrinkles
        # threshold wrinkles and invert
        thresh = cv2.threshold(transform,0.6,1,cv2.THRESH_BINARY)[1]
        thresh = cv2.cvtColor(thresh,cv2.COLOR_GRAY2BGR) 
        thresh_inv = 1-thresh
        transform = cv2.cvtColor(transform,cv2.COLOR_GRAY2BGR)

        low = 2.0 * img * transform
        high = 1 - 2.0 * (1-img) * (1-transform)
        img = low*thresh_inv + high*thresh

    img = ( 255 * img ).clip(0, 255).astype(np.uint8)
   
    # save results
    cv2.imwrite(filename, img)
    
    return filename
    