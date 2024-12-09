# https://huggingface.co/docs/transformers/en/model_doc/zoedepth
from transformers import AutoImageProcessor, ZoeDepthForDepthEstimation
import torch
import numpy as np
from PIL import Image
import requests

zoe = "Intel/zoedepth-nyu-kitti"
img_proc = AutoImageProcessor.from_pretrained(zoe)
model = ZoeDpethForDepthEstimation.from_pretrained(zoe)



"""
Estimates depth from an image given by url (can be modified into using numpy/tensor input)
Returns a tensor of Size [x_dim, y_dim], with pixels ranging from 0 to 1.
"""
def estimate_depth(url, x_dim, y_dim):
    img = Image.open(requests.get(url,stream=True).raw)
    inputs = image_proc(images=img, return_tensors="pt")
    with torch.no_grad():
        outputs = model(inputs['pixel_values'])
        processed_output = img_proc.post_process_depth_estimation(outputs, source_sizes=[(x_dim, y_dim)])
    depth = processed_output[0]['predicted_depth']
    depth = (depth - depth.min()) / (depth.max()-depth.min())
    return depth

