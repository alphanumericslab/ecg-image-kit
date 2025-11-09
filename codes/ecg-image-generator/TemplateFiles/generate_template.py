import os
import wfdb
import random
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from datetime import date, timedelta
import numpy as np

test_date1 = date(1940, 1, 1)

import random
from datetime import datetime, timedelta

def random_datetime(start_date, end_date):
    """Generate random datetime between two dates"""
    time_between = end_date - start_date
    total_seconds = time_between.total_seconds()
    random_seconds = random.uniform(0, total_seconds)
    return start_date + timedelta(seconds=random_seconds)

def generate_template(header_file):
    filename, extn = os.path.splitext(header_file)
    fields = wfdb.rdheader(filename)

    start = datetime(1960, 1, 1)
    end = datetime(2022, 1, 1)
    random_dt = random_datetime(start, end)

    if fields.comments == []:
        attributes = {}

        if fields.base_date is not None:
            attributes['Date'] = fields.base_date
        else:
            attributes['Date'] = random_dt.strftime(random.choice(["%d/%m/%Y", "%d-%m-%Y"]))
        if fields.base_time is not None:
            attributes['Time'] = str(fields.base_time)
        else:
            attributes['Time'] = random_dt.strftime("%H:%M:%S")
        attributes['ID'] = 'ID: ' + filename.split('/')[-1]
        attributes['Name'] =  'Name: ' 
        if attributes['Date'] != "":
            attributes['Date'] = 'Date:'  + str(attributes['Date'])
        if attributes['Time'] != "":
            attributes['Date'] += ', ' + attributes['Time']
        attributes['Sex'] = f"Sex: {random.choice(['Male', 'Female'])}"
        attributes['Age'] = f"Age: {random.choice(range(12, 75))} yrs"
        printedText = {}
        printedText[0] = ['ID', 'Name', 'Date']
        printedText[1] = ["Age"]
        printedText[2] = ["Sex"]

        return printedText, attributes, 1

    else:
        comments = fields.comments
        
        attributes = {}
        
        
        if fields.base_date is not None:
            attributes['Date'] = fields.base_date
        else:
            attributes['Date'] = random_dt.strftime(random.choice(["%d/%m/%Y", "%d-%m-%Y"]))
        if fields.base_time is not None:
            attributes['Time'] = str(fields.base_time)
        else:
            attributes['Time'] = random_dt.strftime("%H:%M:%S")
            
        attributes['ID'] = 'ID: ' + filename.split('/')[-1]
        attributes['Name'] =  'Name: ' #+ str(str(random.randint(10**(8-1), (10**8)-1)))
    
        attributes['Height'] = ''
        attributes['Weight'] = ''
        attributes['Sex'] = random.choice(["Male", "Female"])
        
        for c in comments:
            col = c.split(':')[0]
            val = c.split(':')[1]
            
            if col == 'Age' or col == 'Height' or col == 'Weight':
                val = val.replace(" ", "")
                if val == 'Unknown':
                    attributes[str(col)] = ''
                else:
                    attributes[str(col)] = str(val)
            else:
                val = val.replace(" ", "")
                attributes[str(col)] = val

        if 'DOB' in attributes.keys():
            attributes['DOB'] = 'DOB: ' + attributes['DOB'] 
            if 'Age' in attributes.keys():
                attributes['DOB'] += '(Age: ' + attributes['Age'] + ' yrs)'
        else:
            attributes['DOB'] = 'Age: ' + attributes['Age'] + ' yrs'

        if attributes['Weight'] != '':
            attributes['Weight'] = 'Weight: ' + attributes['Weight'] + ' kg'

        if attributes['Height'] != '':
            attributes['Height'] = 'Height: ' + attributes['Height'] + ' cm'

        attributes['Date'] = str(attributes['Date'])
        attributes['Date'] = 'Date: '+  attributes['Date'] + ', ' + attributes['Time']
        attributes['Sex'] = 'Sex: ' + attributes['Sex']
        
        printedText = {}
        printedText[0] = ['ID', 'Name', 'Date']
        printedText[1] = ['DOB', 'Height', 'Weight']
        printedText[2] = ['Sex']

        return printedText, attributes, 1

        




