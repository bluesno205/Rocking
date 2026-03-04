import numpy as np
import cv2
from PIL import Image, ImageDraw

def print_adjust_parameters(resize_image):
    print(f"Resize_image: {resize_image}")

def image_cutting(image):
    height, width = image.shape[:2]
    top_cut = height // 3  
    bottom_cut = height - (height // 3)  
    cropped_image = image[top_cut:bottom_cut, :]
    return cropped_image

def resize_image(image, scale):
    # 计算新的尺寸
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    new_size = (width, height)
    # 调整图像大小
    resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)
    return resized_image

