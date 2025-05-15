# utils/image_utils.py
import cv2
import imagehash
from PIL import Image

def get_image_hash(image_bgr):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    return imagehash.phash(image_pil)
