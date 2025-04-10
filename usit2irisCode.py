import cv2
import numpy as np

def usit2IrisCode(img):
    """    
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

# --------- Example usage ---------

# Path to your input image
input_path = 'codes/image.png'

# Output path for the binary code image
output_path = 'codes/irisCode.png'

# Step 1: Read the image in grayscale
image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

print(image.shape)
# Step 2: Generate the binary code
binary_code = usit2IrisCode(image)

print(binary_code.shape)

# Step 3: Save binary code as an image
save_binary_code_as_image(binary_code, output_path)

print(f"Binary code saved as image: {output_path}")
