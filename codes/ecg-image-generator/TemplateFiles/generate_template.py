import os
import wfdb
import random
from PIL import Image, ImageDraw, ImageFont


def generate_template(header_file, font_type, mode, template_file):
    filename, extn = os.path.splitext(header_file)
    fields = wfdb.rdheader(filename)
    
    if fields.comments == []:
        template_file_content = open(os.path.join('TemplateFiles','TextFile1.txt'), 'r')
        Lines = template_file_content.readlines()
        lines = []
        max = 0
        for line in Lines:
            if(len(line.strip()) > max):
                maxIdx = line.strip()
                max = len(line.strip())
            lines.append(line.strip())

    else:
        comments = fields.comments
        
        attributes = {}
        attributes['Date'] = str(fields.base_date)
        attributes['Time'] = str(fields.base_time)
        attributes['Name'] = header_file.split('.')[0].split('/')[-1]
        if attributes['Date'] == None:
            attributes['Date']= str(random.randint(1, 31)) + " " + random.choice(('Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')) + " " + str(random.randint(0, 23))
        attributes['Age'] = random.randint(10, 80) 
        attributes['Height'] = ''
        attributes['Weight'] = ''
        
        for c in comments:
            col = c.split(':')[0]
            val = c.split(':')[1]

            if col == 'Age' or col == 'Height' or col == 'Weight':
                val = val.replace(" ", "")
                if val == 'Unknown':
                    attributes[str(col)] = ''
                else:
                    attributes[str(col)] = int(val)
            else:
                attributes[str(col)] = val


        lines = []
        l1 = 'Date:' + attributes['Date'] + '     ' + attributes['Time'] + str("   ")
        l2 = 'Name:' + attributes['Name'] + '    ' + "Height:" + str(attributes['Height']) + ' '
        l3 = 'Sex:' + attributes['Sex'] + '           ' + "Weight:" + str(attributes['Weight']) + ' '
        l4 = 'Age:' + str(attributes['Age']) + '             ' 

        lines.append(l1)
        lines.append(l2)
        lines.append(l3)
        lines.append(l4)


    max = 0
    for line in lines:
        if(len(line.strip()) > max):
            maxIdx = line.strip()
            max = len(line.strip())

    
    font_size = random.randint(15, 30)
    font_type = os.path.join('Fonts','Arial.ttf')
    font = ImageFont.truetype(font_type, font_size, encoding="unic")
    text_width, text_height = font.getsize(maxIdx)

    #Write template file into an image and use this to print on the paper ecg
    canvas = Image.new('RGB', (text_width + 10, len(lines)*text_height + 10), "white")
    draw = ImageDraw.Draw(canvas)
    x_start = 5
    y_start = 5
    
    for l in lines:
        draw.text((5, y_start), l, 'black', font)
        y_start += (text_height)

    canvas.save(template_file, "PNG")


