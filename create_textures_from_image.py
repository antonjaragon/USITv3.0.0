import subprocess
import cv2
import numpy as np
from pathlib import Path

import logging

# Set up logging
logging.basicConfig(
    filename='errors.log',
    filemode='a',  # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)



# Base paths
masks_base = Path('./data/masks')
circles_base = Path('./data/circles')
input_base = Path('./data/input_images')
textures_base = Path('./data/textures')
cnn_script = Path('./packages/cnnmasktomanuseg/cnnmasktomanuseg.py')
iris_code_base = Path('./data/irisCode')  # Output folder (where irisCode images will be saved)
codes_base = Path('./data/codes')  # Input folder (where .bmp files are stored after lg conversion)

# Function to calculate USIT code
def calculate_usit_code(img):
    """
    Converts an image into a binary code similar to MATLAB's calcolaCodiceDaUSIT.
    
    Parameters:
        img (numpy.ndarray): Grayscale image as uint8.
    
    Returns:
        binary_code (numpy.ndarray): A 2D array where each row has 512 bits.
    """
    img = img.astype(np.uint8)
    bit_array = np.unpackbits(img, axis=1)
    binary_vector = bit_array.flatten()

    remainder = binary_vector.size % 512
    if remainder != 0:
        padding = 512 - remainder
        binary_vector = np.pad(binary_vector, (0, padding), mode='constant')

    binary_code = binary_vector.reshape(-1, 512)
    return binary_code

# Function to save binary code as an image
def save_binary_code_as_image(binary_code, save_path):
    """
    Saves the binary code (0s and 1s) as an image (black & white).
    
    Parameters:
        binary_code (numpy.ndarray): 2D binary matrix
        save_path (str): Path to save the output image
    """
    # Multiply by 255 to make it a visible image (0 = black, 1 = white)
    binary_image = (binary_code * 255).astype(np.uint8)
    cv2.imwrite(save_path, binary_image)

# --------- Step 1: Process masks directory and generate textures ---------
# Scan all PNG files inside the masks directory (including subfolders)
for mask_file in masks_base.rglob('*.png'):
    # Get relative path from the masks folder (e.g., subfolder1/subfolder2/file1.png)
    relative_path = mask_file.relative_to(masks_base)
    stem = mask_file.stem  # "file1"

    # Folder paths based on relative structure
    circle_dir = circles_base / relative_path.parent
    input_tiff = input_base / relative_path.with_suffix('.tiff')
    input_tif = input_base / relative_path.with_suffix('.tif')  # Check for .tif files as well
    inner_txt = circle_dir / f'{stem}.inner.txt'
    outer_txt = circle_dir / f'{stem}.outer.txt'
    output_texture = textures_base / relative_path.with_name(f"{stem}_texture.bmp")
    output_texture_enhanced = textures_base / relative_path.with_name(f"{stem}_enhanced_texture.bmp")

    # Make sure necessary folders exist
    circle_dir.mkdir(parents=True, exist_ok=True)
    output_texture.parent.mkdir(parents=True, exist_ok=True)

    # Command 1: run the python script with directory as output
    cmd1 = [
        'python', str(cnn_script),
        str(mask_file),
        str(circle_dir)
    ]

    # Command 2: run manuseg
    cmd2 = [
        'manuseg',
        '-i', str(input_tiff),  # Default .tiff file
        '-c', str(inner_txt), str(outer_txt),
        '', '',
        '-o', str(output_texture),
        '-q'
    ]

    # Command 3: same as cmd2, but with -e and different output name
    cmd3 = [
        'manuseg',
        '-i', str(input_tiff),  # Default .tiff file
        '-c', str(inner_txt), str(outer_txt),
        '', '',
        '-o', str(output_texture_enhanced),
        '-q',
        '-e'
    ]

    # Command 4: run lg command to convert texture to an image
    output_lg_dir = codes_base / relative_path.parent  # Maintain the same relative path structure
    output_lg_dir.mkdir(parents=True, exist_ok=True)  # Create the necessary dirs for lg output

    # Using the stem name for the output file
    output_lg_file = output_lg_dir / f"{stem}.bmp"

    cmd4 = [
        'lg',
        '-i', str(output_texture),  # using the generated texture file
        '-o', str(output_lg_file)
    ]

    try:
        print(f"\nRunning CNN mask to manuseg for: {mask_file}")
        try:
            subprocess.run(cmd1, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"cmd1 failed for {mask_file}: {e}")
            continue

        # Determine which input file exists: .tiff or .tif
        input_image = input_tiff if input_tiff.exists() else input_tif

        # Update commands with the correct input image
        cmd2[2] = str(input_image)
        cmd3[2] = str(input_image)

        print(f"Running manuseg (default) for: {input_image}")
        try:
            subprocess.run(cmd2, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"cmd2 failed for {input_image}: {e}")
            continue

        print(f"Running manuseg (enhanced) for: {input_image}")
        try:
            subprocess.run(cmd3, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"cmd3 failed for {input_image}: {e}")
            continue

        print(f"Running lg command for: {output_texture}")
        try:
            subprocess.run(cmd4, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"cmd4 (lg) failed for {output_texture}: {e}")
            continue
        
    except Exception as e:
        logging.error(f"Unexpected error for {mask_file}: {str(e)}")
        continue

    # --------- Step 2: Generate IrisCode for each file immediately after processing the texture ---------
    # Read the generated texture image for the irisCode calculation
    image = cv2.imread(str(output_lg_file), cv2.IMREAD_GRAYSCALE)

    # Generate the binary code (USIT code)
    binary_code = calculate_usit_code(image)

    # Folder path for irisCode based on the relative path structure
    iris_code_dir = iris_code_base / relative_path.parent
    iris_code_dir.mkdir(parents=True, exist_ok=True)  # Ensure subdirectories exist

    # Save the binary code as an image
    iris_code_image_path = iris_code_dir / f"{stem}_irisCode.bmp"
    save_binary_code_as_image(binary_code, str(iris_code_image_path))

    print(f"Binary code saved as image: {iris_code_image_path}")

print("\n✅ All files processed.")
