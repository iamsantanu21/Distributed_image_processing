from PIL import Image
import numpy as np
import cv2
import socket
import time
import concurrent.futures
import os
import pickle

def split_image(image):
    # Split the image into 4 parts
    height, width = image.shape[:2]
    mid_x, mid_y = width // 2, height // 2
    parts = [
        image[:mid_y, :mid_x],  # Top-left
        image[:mid_y, mid_x:],   # Top-right
        image[mid_y:, :mid_x],   # Bottom-left
        image[mid_y:, mid_x:]    # Bottom-right
    ]
    return parts

def concatenate_image(parts):
    # Concatenate the 4 parts into a single image
    top = np.hstack((parts[0], parts[1]))
    bottom = np.hstack((parts[2], parts[3]))
    final_image = np.vstack((top, bottom))
    return final_image

def receive_image_data(conn):
    # Receive the size of the data first
    size_data = conn.recv(8)
    size = int.from_bytes(size_data, byteorder='big')
    # Receive the actual data
    data = b''
    while len(data) < size:
        packet = conn.recv(min(4096, size - len(data)))
        if not packet:
            break
        data += packet
    # Deserialize the data
    return pickle.loads(data)

def send_image_part(host, port, image_part):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        _, img_encoded = cv2.imencode('.png', image_part)
        img_data = img_encoded.tobytes()

        # Send the size of the image data first
        size = len(img_data)
        client_socket.sendall(size.to_bytes(8, byteorder='big'))  # Send size as 8 bytes
        print(f"Sending {size} bytes to {host}:{port}")

        # Send the image data
        client_socket.sendall(img_data)

        # Receive all processed images
        processed_images = receive_image_data(client_socket)
        return processed_images

def process_part_parallel(server_info, image_part, index):
    host, port = server_info
    start_time = time.time()
    processed_images = send_image_part(host, port, image_part)
    processing_time = time.time() - start_time
    print(f"Processing time on server {port}: {processing_time:.2f} seconds")
    return index, processed_images  # Return the index along with the processed images

if __name__ == "__main__":
    # Create the output directory if it doesn't exist
    OUTPUT_DIR = "client_output"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load the TIFF image using Pillow
    tiff_image = Image.open('santanu.tiff')
    tiff_image = tiff_image.convert('RGB')  # Convert to RGB if necessary
    image = np.array(tiff_image)  # Convert to NumPy array for processing

    # Save the original image
    original_image_path = os.path.join(OUTPUT_DIR, "original_image.png")
    cv2.imwrite(original_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    print(f"Saved original image to {original_image_path}")

    # Split the image into 4 parts
    parts = split_image(image)
    for i, part in enumerate(parts):
        print(f"Part {i} shape: {part.shape}")

    # Define server addresses
    servers = [
        ('127.0.0.1', 65432),  # Replace with actual server IPs and ports
        ('127.0.0.1', 65433),
        ('127.0.0.1', 65434),
        ('127.0.0.1', 65435)
    ]

    # Initialize a dictionary to store processed parts for each type
    processed_parts = {
        "gray": [None] * len(parts),
        "blurred": [None] * len(parts),
        "edges": [None] * len(parts),
        "thresholded": [None] * len(parts),
        "equalized": [None] * len(parts)
    }

    start_time = time.time()

    # Use ThreadPoolExecutor to send parts to servers in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_part_parallel, server, part, i) for i, (server, part) in enumerate(zip(servers, parts))]
        for future in concurrent.futures.as_completed(futures):
            index, processed_images = future.result()  # Get the index and processed images
            for key in processed_parts:
                processed_parts[key][index] = processed_images[key]  # Store the processed part in the correct position

    total_processing_time = time.time() - start_time

    # Concatenate and save all final processed images
    for key in processed_parts:
        final_image = concatenate_image(processed_parts[key])
        final_image_path = os.path.join(OUTPUT_DIR, f"final_{key}_image.png")
        cv2.imwrite(final_image_path, final_image)
        print(f"Saved final {key} image to {final_image_path}")

    print(f"Total processing time: {total_processing_time:.2f} seconds")