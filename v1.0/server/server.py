import socket
import cv2
import threading
import time
import tkinter as tk
from tkinter import messagebox
from utils import deserialize_object, serialize_object, process_image

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def handle_client(conn, addr, port, log_area):
    log_area.insert(tk.END, f"Connected from {addr}\n")
    data = b''
    while True:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    image_part = deserialize_object(data)
    cv2.imshow(f"Received Part [Port {port}]", image_part)
    cv2.waitKey(500)

    start_time = time.time()
    processed = process_image(image_part)
    proc_time = time.time() - start_time

    cv2.imshow(f"Processed Image [Port {port}]", processed)
    cv2.waitKey(500)
    cv2.destroyAllWindows()

    response = {'image': processed, 'time': proc_time}
    conn.sendall(serialize_object(response))
    conn.close()
    log_area.insert(tk.END, f"Processed and sent back in {proc_time:.3f} sec.\n")

def start_server(port, log_area):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    log_area.insert(tk.END, f"Server running on port {port}...\n")
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr, port, log_area)).start()

def launch_server():
    root = tk.Tk()
    root.title("Image Processing Server")
    ip = get_local_ip()

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text=f"Server IP: {ip}").pack()

    tk.Label(frame, text="Enter Port:").pack()
    port_entry = tk.Entry(frame)
    port_entry.pack()

    log_area = tk.Text(root, height=15, width=50)
    log_area.pack(pady=10)

    def run_server():
        port = int(port_entry.get())
        threading.Thread(target=start_server, args=(port, log_area)).start()

    tk.Button(frame, text="Start Server", command=run_server).pack()
    root.mainloop()

if __name__ == "__main__":
    launch_server()
