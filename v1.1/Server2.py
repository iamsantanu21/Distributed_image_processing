import cv2
import numpy as np
import socket
import time
import os
import pickle

def process_image(image_part):
    # Convert the image part to grayscale
    gray_image = cv2.cvtColor(image_part, cv2.COLOR_BGR2GRAY)

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
    hsv_image = cv2.cvtColor(image_part, cv2.COLOR_BGR2HSV)

    # Convert to LAB color space
    lab_image = cv2.cvtColor(image_part, cv2.COLOR_BGR2LAB)

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
    corner_image = np.copy(image_part)
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

def send_image_data(conn, image_data):
    # Serialize the image data
    data = pickle.dumps(image_data)
    # Send the size of the data first
    conn.sendall(len(data).to_bytes(8, byteorder='big'))
    # Send the actual data
    conn.sendall(data)

def start_server(host, port, output_dir):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")

                # Receive the size of the image data first
                size_data = conn.recv(8)
                size = int.from_bytes(size_data, byteorder='big')  # Fixed line
                print(f"Expecting {size} bytes of image data")

                # Receive the image data
                data = b''
                while len(data) < size:
                    packet = conn.recv(min(4096, size - len(data)))
                    if not packet:
                        break
                    data += packet
                    print(f"Received {len(packet)} bytes, total {len(data)} bytes")

                print("Finished receiving data")

                # Deserialize the image
                image_part = np.frombuffer(data, dtype=np.uint8)
                image_part = cv2.imdecode(image_part, cv2.IMREAD_COLOR)
                if image_part is None:
                    print("Failed to decode image")
                    continue
                else:
                    print("Image decoded successfully")
                    print(f"Image shape: {image_part.shape}")

                # Convert RGB to BGR if necessary
                if image_part.shape[2] == 3:  # Check if the image has 3 channels (RGB)
                    image_part = cv2.cvtColor(image_part, cv2.COLOR_RGB2BGR)

                # Save the received image part
                received_image_path = os.path.join(output_dir, f"received_part_{port}.png")
                cv2.imwrite(received_image_path, image_part)
                print(f"Saved received image part to {received_image_path}")

                # Process the image part
                start_time = time.time()
                processed_images = process_image(image_part)
                processing_time = time.time() - start_time

                # Save the processed images
                for key, processed_image in processed_images.items():
                    processed_image_path = os.path.join(output_dir, f"{key}_part_{port}.png")
                    cv2.imwrite(processed_image_path, processed_image)
                    print(f"Saved {key} image part to {processed_image_path}")

                # Send all processed images back to the client
                send_image_data(conn, processed_images)

                print(f"Processing time on server {port}: {processing_time:.2f} seconds")

if __name__ == "__main__":
    HOST = '127.0.0.1'  # Replace with the server's IP address
    PORT = 65433        # Replace with the server's port
    OUTPUT_DIR = "server_output"  # Directory to save server images
    start_server(HOST, PORT, OUTPUT_DIR)