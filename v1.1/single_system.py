import cv2
import numpy as np
import time
import os

def process_image(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred_image, 100, 200)

    # Apply binary thresholding
    _, thresholded_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

    # Apply histogram equalization
    equalized_image = cv2.equalizeHist(gray_image)

    # Resize the image
    resized_image = cv2.resize(gray_image, (128, 128))

    # Adjust contrast
    contrast_adjusted_image = cv2.convertScaleAbs(gray_image, alpha=1.5, beta=0)

    # Adjust brightness
    brightness_adjusted_image = cv2.convertScaleAbs(gray_image, alpha=1.0, beta=50)

    # Apply sharpening filter
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened_image = cv2.filter2D(gray_image, -1, kernel)

    # Convert to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Convert to LAB color space
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Apply morphological operations
    kernel = np.ones((5, 5), np.uint8)
    eroded_image = cv2.erode(gray_image, kernel, iterations=1)
    dilated_image = cv2.dilate(gray_image, kernel, iterations=1)
    opened_image = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, kernel)
    closed_image = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)

    # Apply median blur for noise reduction
    median_blurred_image = cv2.medianBlur(gray_image, 5)

    # Apply bilateral filtering for noise reduction
    bilateral_filtered_image = cv2.bilateralFilter(gray_image, 9, 75, 75)

    # Detect corners using Harris corner detection
    corner_image = np.copy(image)
    corners = cv2.cornerHarris(gray_image, 2, 3, 0.04)
    corner_image[corners > 0.01 * corners.max()] = [0, 0, 255]  # Mark corners in red

    return {
        "gray": gray_image,
        "blurred": blurred_image,
        "edges": edges,
        "thresholded": thresholded_image,
        "equalized": equalized_image,
        "resized": resized_image,
        "contrast_adjusted": contrast_adjusted_image,
        "brightness_adjusted": brightness_adjusted_image,
        "sharpened": sharpened_image,
        "hsv": hsv_image,
        "lab": lab_image,
        "eroded": eroded_image,
        "dilated": dilated_image,
        "opened": opened_image,
        "closed": closed_image,
        "median_blurred": median_blurred_image,
        "bilateral_filtered": bilateral_filtered_image,
        "corners": corner_image
    }

def save_processed_images(processed_images, output_dir):
    # Save all processed images
    for key, image in processed_images.items():
        output_path = os.path.join(output_dir, f"{key}.png")
        cv2.imwrite(output_path, image)
        print(f"Saved {key} image to {output_path}")

if __name__ == "__main__":
    # Create the output directory if it doesn't exist
    OUTPUT_DIR = "centralized_output"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load the TIFF image using OpenCV
    image = cv2.imread("sea.tiff")
    if image is None:
        print("Failed to load image. Please check the file path.")
        exit()

    # Save the original image
    original_image_path = os.path.join(OUTPUT_DIR, "original_image.png")
    cv2.imwrite(original_image_path, image)
    print(f"Saved original image to {original_image_path}")

    # Process the image
    start_time = time.time()
    processed_images = process_image(image)
    processing_time = time.time() - start_time

    # Save the processed images
    save_processed_images(processed_images, OUTPUT_DIR)

    print(f"Total processing time: {processing_time:.2f} seconds")