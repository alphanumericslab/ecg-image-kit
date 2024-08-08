import os
import wfdb
from PIL import Image
import json
import matplotlib.pyplot as plt
import subprocess
import pickle
import multiprocessing
import time

f1 = os.path.join(os.getcwd(), "../../../output/new1/textfile.pkl")


def run_subprocess(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
        
    if process.returncode == 0:
        print("Script executed successfully")
        print("Output:", stdout)
    else:
        print("Script execution failed")
        print("Error:", stderr)
        

def run():
    with open(f1, 'rb') as f:
        loaded_list = pickle.load(f)

    st_time = time.time()
    '''for line in loaded_list[:10]:
        print(line)
        process = subprocess.Popen(line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("Script executed successfully")
            print("Output:", stdout)
        else:
            print("Script execution failed")
            print("Error:", stderr)

    en_time = time.time()
    print(en_time - st_time)'''

    st_time = time.time()
    with multiprocessing.Pool() as pool:
            pool.map(run_subprocess, loaded_list[:10])

    print(time.time() - st_time)

if __name__ == '__main__':
    run()