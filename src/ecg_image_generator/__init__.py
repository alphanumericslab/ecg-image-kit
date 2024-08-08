from ecg_image_generator.gen_ecg_images_from_data_batch import run
import argparse
from ecg_image_generator.helper_functions import convert_function_inp_to_args_object
from ecg_image_generator.gen_ecg_image_from_data import run_single_file

def gen_batch_images(input_dir, output_dir, seed=-1, num_leads='twelve', max_num_images=-1, config_file='config.yaml', 
                    resolution = 200, pad_inches=0, print_header=0, num_columns =-1, full_mode='II', mask_unplotted_samples = False,
                    add_qr_code = False, link='', num_words=5, x_offset=30, y_offset=30, hws = 0.2, crease_angle = 90, 
                    num_creases_vertically=10, num_creases_horizontally=10, rotate = 0, noise=50, crop = 0.01, temperature=40000,
                    random_resolution=False, random_padding=False, random_grid_color=False, standard_grid_color=5, calibration_pulse=1, 
                    random_grid_present=1, random_print_header=0, random_bw=0, remove_lead_names=True, lead_name_bbox=False, store_config=0, 
                    deterministic_offset=False, deterministic_num_words=False, deterministic_hw_size=False, deterministic_angle=False,
                    deterministic_vertical=False, deterministic_horizontal=False, deterministic_rot=False, deterministic_noise=False, deterministic_crop=False,
                    deterministic_temp=False, fully_random=False, hw_text=False, wrinkles=False, augment=False, lead_bbox=False):
    
    parser = argparse.ArgumentParser()
    parser.input_directory = input_dir
    parser.output_directory = output_dir
    parser.max_num_images = max_num_images
    convert_function_inp_to_args_object(parser, seed, num_leads, config_file, resolution, pad_inches, print_header, num_columns, full_mode, mask_unplotted_samples,
                    add_qr_code, link, num_words, x_offset, y_offset, hws, crease_angle, num_creases_vertically, num_creases_horizontally, rotate, noise, crop, temperature,
                    random_resolution, random_padding, random_grid_color, standard_grid_color, calibration_pulse, random_grid_present, random_print_header, random_bw, remove_lead_names, lead_name_bbox, store_config, 
                    deterministic_offset, deterministic_num_words, deterministic_hw_size, deterministic_angle, deterministic_vertical, deterministic_horizontal, deterministic_rot, deterministic_noise, deterministic_crop,
                    deterministic_temp, fully_random, hw_text, wrinkles, augment, lead_bbox)
    run(parser)
    print("Function call")


def gen_image(input_file, header_file, output_dir, start_index=-1, seed=-1, num_leads='twelve', config_file='config.yaml', 
                resolution = 200, pad_inches=0, print_header=0, num_columns =-1, full_mode='II', mask_unplotted_samples = False,
                add_qr_code = False, link='', num_words=5, x_offset=30, y_offset=30, hws = 0.2, crease_angle = 90, 
                num_creases_vertically=10, num_creases_horizontally=10, rotate = 0, noise=50, crop = 0.01, temperature=40000,
                random_resolution=False, random_padding=False, random_grid_color=False, standard_grid_color=5, calibration_pulse=1, 
                random_grid_present=1, random_print_header=0, random_bw=0, remove_lead_names=True, lead_name_bbox=False, store_config=0, 
                deterministic_offset=False, deterministic_num_words=False, deterministic_hw_size=False, deterministic_angle=False,
                deterministic_vertical=False, deterministic_horizontal=False, deterministic_rot=False, deterministic_noise=False, deterministic_crop=False,
                deterministic_temp=False, fully_random=False, hw_text=False, wrinkles=False, augment=False, lead_bbox=False):

    parser = argparse.ArgumentParser()
    parser.input_file = input_file
    parser.header_file = header_file
    parser.output_directory = output_dir
    parser.start_index = start_index
    convert_function_inp_to_args_object(parser, seed, num_leads, config_file, resolution, pad_inches, print_header, num_columns, full_mode, mask_unplotted_samples,
                    add_qr_code, link, num_words, x_offset, y_offset, hws, crease_angle, num_creases_vertically, num_creases_horizontally, rotate, noise, crop, temperature,
                    random_resolution, random_padding, random_grid_color, standard_grid_color, calibration_pulse, random_grid_present, random_print_header, random_bw, remove_lead_names, lead_name_bbox, store_config, 
                    deterministic_offset, deterministic_num_words, deterministic_hw_size, deterministic_angle, deterministic_vertical, deterministic_horizontal, deterministic_rot, deterministic_noise, deterministic_crop,
                    deterministic_temp, fully_random, hw_text, wrinkles, augment, lead_bbox)
    run_single_file(parser)
    print("Single image")