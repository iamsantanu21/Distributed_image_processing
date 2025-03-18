import cv2
import numpy as np
import pickle

def serialize_object(obj):
    return pickle.dumps(obj)

def deserialize_object(data):
    return pickle.loads(data)

def process_image(image):
    # Lightweight processing: grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return processed

def split_image_into_4(image):
    h, w, _ = image.shape
    return [
        image[0:h//2, 0:w//2],
        image[0:h//2, w//2:],
        image[h//2:, 0:w//2],
        image[h//2:, w//2:]
    ]

def concatenate_4_images(parts):
    top = np.hstack((parts[0], parts[1]))
    bottom = np.hstack((parts[2], parts[3]))
    return np.vstack((top, bottom))
