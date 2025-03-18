import socket
import cv2
import numpy as np
import time
import pickle

def process_image(img):
    """Apply image processing (e.g., edge detection)."""
    return cv2.Canny(img, 100, 200)

def server_program(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        # Receive data
        data = b""
        while True:
            packet = conn.recv(4096)
            if not packet: break
            data += packet
        
        img_part = pickle.loads(data)
        start_time = time.time()  # Start time for processing
        
        processed_part = process_image(img_part)
        
        end_time = time.time()  # End time for processing
        processing_time = end_time - start_time
        print(f"Processing Time: {processing_time:.4f} seconds")

        # Send processed image part and processing time
        conn.sendall(pickle.dumps((processed_part, processing_time)))
        conn.close()

if __name__ == "__main__":
    import sys
    HOST = "127.0.0.1"
    PORT = int(sys.argv[1])  # Run different servers on different ports
    server_program(HOST, PORT)
