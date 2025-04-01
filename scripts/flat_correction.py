#!/usr/bin/env python3

import os
import argparse
import numpy as np
import imageio.v2 as imageio
from glob import glob
from tifffile import imwrite

def correct_image(image, flat_r, flat_g, flat_b):
    image = image.astype(np.float32)
    corrected = np.zeros_like(image, dtype=np.float32)
    corrected[..., 0] = image[..., 0] / flat_r  # R
    corrected[..., 1] = image[..., 1] / flat_g  # G
    corrected[..., 2] = image[..., 2] / flat_b  # B
    return np.clip(corrected, 0, 65535).astype(np.uint16)


def normalize_flat(flat_image, channel_index):
    channel = flat_image[..., channel_index].astype(np.float32)
    return channel / np.max(channel)


def process_images(input_dir, output_dir, flat_r_path, flat_g_path, flat_b_path):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = sorted(glob(os.path.join(input_dir, "*.tif")))
    #print(f"Found {len(files)} files.")

    flat_r_image = imageio.imread(flat_r_path)
    flat_g_image = imageio.imread(flat_g_path)
    flat_b_image = imageio.imread(flat_b_path)

    flat_r = normalize_flat(flat_r_image, 0)  # Red
    flat_g = normalize_flat(flat_g_image, 1)  # Green
    flat_b = normalize_flat(flat_b_image, 2)  # Blue

    for path in files:
        print(f"    Processing {os.path.basename(path)} ...")
        image = imageio.imread(path).astype(np.float32)
        corrected = correct_image(image, flat_r, flat_g, flat_b)
        out_path = os.path.join(output_dir, os.path.basename(path))
        imwrite(out_path, corrected)


if __name__ == "__main__" :

    parser = argparse.ArgumentParser(description="Flat-field correction for RGB 16bit TIFF images.")
    parser.add_argument("input_dir", help="Input directory with TIFF images")
    parser.add_argument("output_dir", help="Output directory for corrected TIFF images")
    parser.add_argument("--flat_r", required=True, help="Flat-field image for Red channel")
    parser.add_argument("--flat_g", required=True, help="Flat-field image for Green channel")
    parser.add_argument("--flat_b", required=True, help="Flat-field image for Blue channel")
    args = parser.parse_args()

    process_images(args.input_dir, args.output_dir, args.flat_r, args.flat_g, args.flat_b)
