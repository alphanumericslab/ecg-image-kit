# NOTES BEFORE RUNNING: 
- Replace <input_path> and <output_path> below with the input and output directories, respectively.
- **To compare the two scripts as fairly as possible, ensure that lines 97 and 98 in gen_ecg_images_from_data_batch.py are commented out to prevent handwritten text!!!**
- Change cpu_count to a different number by adding "--cpu_count <your_number>" to the command, otherwise all available CPU
cores will be used!


# Command for the old script
```bash
python codes/ecg-image-generator/gen_ecg_images_from_data_batch.py \
    -i <input_path> \
    -o <output_path> \
    --store_config 1 \
    --lead_name_bbox \
    --lead_bbox \
    --augment \
    --hw_text \
    -rot 20 \
    --random_grid_color \
    --fully_random \
    --mask_unplotted_samples \
    --print_header
```

# Command for the new script
```bash
python codes/ecg-image-generator/gen_ecg_images_from_data_batch_parallel.py \
    -i <input_path> \
    -o <output_path> \
    --store_config 1 \
    --lead_name_bbox \
    --lead_bbox \
    --augment \
    -rot 20 \
    --random_grid_color \
    --fully_random \
    --mask_unplotted_samples \
    --print_header
```