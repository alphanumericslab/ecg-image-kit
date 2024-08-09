from ecg_image_generator import gen_batch_images, gen_image
import os, sys, argparse
import shutil

#generate simple file    
input_dir = os.path.join(os.getcwd(), 'test_data/sample_input')
output_dir = os.path.join(os.getcwd(), 'temp')

if os.path.isdir(output_dir) == False:
    os.mkdir(output_dir)


#Generate simple image without any attributes
gen_batch_images(input_dir=input_dir, output_dir=output_dir, max_num_images=10)

#printed_text
gen_batch_images(input_dir=input_dir, output_dir=output_dir, print_header=True, max_num_images=10)

#with attributes
gen_batch_images(input_dir=input_dir, output_dir=output_dir, seed=10, lead_name_bbox=True, lead_bbox=True, random_print_header=0.8, calibration_pulse=0.5, store_config=1, add_qr_code=True, full_mode=['II', 'III'], max_num_images=10, standard_grid_color=1)

#handwritten text
gen_batch_images(input_dir=input_dir, output_dir=output_dir, seed=10, hw_text=True, num_words=4, x_offset=30, y_offset=20, random_grid_color=True, full_mode=['aVF'],  max_num_images=10)

#creases and wrinkles
gen_batch_images(input_dir=input_dir, output_dir=output_dir, seed=10, wrinkles=True, crease_angle=45, random_grid_color=True, add_qr_code=True, max_num_images=10)

#Augmentation
gen_batch_images(input_dir=input_dir, output_dir=output_dir, seed=10, augment=True, rotate=5, noise=40, deterministic_rot=True, deterministic_noise=True, random_grid_color=True, max_num_images=10)

#rotation and crop augmentation
gen_batch_images(input_dir=input_dir, output_dir=output_dir, seed=10, augment=True, rotate=30, crop=0.1, deterministic_rot=True, deterministic_noise=True, max_num_images=10)

#all distortions
gen_batch_images(input_dir=input_dir, output_dir=output_dir, seed=10, augment=True, rotate=5, noise=40, deterministic_rot=True, deterministic_noise=True, hw_text=True, num_words=4, x_offset=30, y_offset=20, wrinkles=True, crease_angle=45, print_header=True, add_qr_code=True, max_num_images=10)

#gnerate single image
gen_image(input_file=os.path.join(os.getcwd(), input_dir, '00001_hr.dat'), header_file=os.path.join(os.getcwd(), input_dir, '00001_hr.hea'), output_dir=output_dir, seed=10, augment=True, rotate=5, noise=40, deterministic_rot=True, deterministic_noise=True, hw_text=True, num_words=4, x_offset=30, y_offset=20, wrinkles=True, crease_angle=45, print_header=True, add_qr_code=True, store_config=1, lead_bbox=True, lead_name_bbox=True, store_plotted_pixels=True)

shutil.rmtree(output_dir)