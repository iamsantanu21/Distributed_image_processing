import socket
import cv2
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from utils import serialize_object, deserialize_object, split_image_into_4, concatenate_4_images

def test_connection(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Distributed Image Client")

        self.entries = []
        tk.Label(root, text="Enter 4 Server IPs and Ports").pack()
        for i in range(4):
            frame = tk.Frame(root)
            frame.pack()
            ip_entry = tk.Entry(frame, width=15)
            ip_entry.pack(side=tk.LEFT)
            port_entry = tk.Entry(frame, width=5)
            port_entry.pack(side=tk.LEFT)
            self.entries.append((ip_entry, port_entry))

        self.status_labels = []
        for i in range(4):
            lbl = tk.Label(root, text=f"Server {i+1} Status: Not checked")
            lbl.pack()
            self.status_labels.append(lbl)

        tk.Button(root, text="Test Connection", command=self.check_connections).pack(pady=5)
        tk.Button(root, text="Select Image & Process", command=self.start_processing).pack(pady=5)

        self.log_area = tk.Text(root, height=10, width=50)
        self.log_area.pack(pady=10)

    def check_connections(self):
        for i, (ip_entry, port_entry) in enumerate(self.entries):
            ip = ip_entry.get()
            port = int(port_entry.get())
            connected = test_connection(ip, port)
            if connected:
                self.status_labels[i].config(text=f"Server {i+1}: Connected")
            else:
                self.status_labels[i].config(text=f"Server {i+1}: Failed")

    def start_processing(self):
        image_path = filedialog.askopenfilename()
        if not image_path:
            return
        image = cv2.imread(image_path)
        parts = split_image_into_4(image)

        processed_parts = []
        times = []

        start_total = time.time()
        for i, (ip_entry, port_entry) in enumerate(self.entries):
            ip = ip_entry.get()
            port = int(port_entry.get())
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port)))
            s.sendall(serialize_object(parts[i]))
            s.shutdown(socket.SHUT_WR)

            data = b''
            while True:
                packet = s.recv(4096)
                if not packet:
                    break
                data += packet
            s.close()
            response = deserialize_object(data)
            processed_parts.append(response['image'])
            times.append(response['time'])

            self.log_area.insert(tk.END, f"Server {i+1} processed in {response['time']:.4f} sec\n")

        end_total = time.time()
        total_time = end_total - start_total
        final_image = concatenate_4_images(processed_parts)
        cv2.imshow("Final Processed Image", final_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        self.log_area.insert(tk.END, f"Total processing (including network): {total_time:.4f} sec\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
