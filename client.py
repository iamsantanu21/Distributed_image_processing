import socket
import cv2
import numpy as np
import time
import pickle
import threading

def split_image(img):
    """Split image into 4 equal parts."""
    height, width = img.shape[:2]
    mid_h, mid_w = height // 2, width // 2

    return [
        img[0:mid_h, 0:mid_w],  # Top-left
        img[0:mid_h, mid_w:width],  # Top-right
        img[mid_h:height, 0:mid_w],  # Bottom-left
        img[mid_h:height, mid_w:width],  # Bottom-right
    ]

def merge_images(parts, original_shape):
    """Merge 4 processed image parts into one."""
    mid_h, mid_w = original_shape[0] // 2, original_shape[1] // 2

    top_half = np.hstack((parts[0], parts[1]))
    bottom_half = np.hstack((parts[2], parts[3]))
    return np.vstack((top_half, bottom_half))

def send_image_part(host, port, img_part, results, index):
    """Send an image part to a server and receive processed part in parallel."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        # Send image part
        client_socket.sendall(pickle.dumps(img_part))

        # Receive processed part
        data = b""
        while True:
            packet = client_socket.recv(4096)
            if not packet: break
            data += packet

        processed_part, processing_time = pickle.loads(data)
        client_socket.close()

        results[index] = (processed_part, processing_time)  # Store result safely

    except Exception as e:
        print(f"Error communicating with server {port}: {e}")

def main():
    HOSTS = ["127.0.0.1", "127.0.0.1", "127.0.0.1", "127.0.0.1"]  # Replace with actual server IPs
    PORTS = [5005, 5006, 5007, 5008]  # Ports for 4 servers

    # Load image
    img = cv2.imread("image.jpg", cv2.IMREAD_GRAYSCALE)
    original_shape = img.shape
    image_parts = split_image(img)

    client_start = time.time()  # Start total time

    results = [None] * 4  # Store processed images and processing times
    threads = []

    # Send parts to servers in parallel
    for i in range(4):
        thread = threading.Thread(target=send_image_part, args=(HOSTS[i], PORTS[i], image_parts[i], results, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    client_end = time.time()  # End total time
    total_client_time = client_end - client_start

    # Extract processed parts and times
    processed_parts, processing_times = zip(*results)

    # Merge processed image
    final_image = merge_images(processed_parts, original_shape)

    # Show and save result
    cv2.imshow("Processed Image", final_image)
    cv2.imwrite("processed_output.jpg", final_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Print time statistics
    for i, time_taken in enumerate(processing_times):
        print(f"Server {i+1} Processing Time: {time_taken:.4f} seconds")
    print(f"Total Client Time: {total_client_time:.4f} seconds")

if __name__ == "__main__":
    main()
