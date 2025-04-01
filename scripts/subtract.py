#!/usr/bin/env python3

import os
import argparse
from glob import glob
import numpy as np
import imageio.v2 as imageio

def subtract_images(input_dir, subtract_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = sorted(glob(os.path.join(input_dir, "*.tif")))
    if not files:
        print("*** No TIFF files found in input directory.")
        return

    print(f"Found {len(files)} files.")

    ref = imageio.imread(subtract_file).astype(np.int32)

    for path in files:
        print(f"Processing {os.path.basename(path)} ...")
        image = imageio.imread(path).astype(np.int32)

        if image.shape != ref.shape:
            print(f"Skipping {path}: shape mismatch.")
            continue

        subtracted = np.clip(image - ref, 0, 65535).astype(np.uint16)

        out_name = os.path.basename(path)
        out_path = os.path.join(output_dir, out_name)
        imageio.imwrite(out_path, subtracted, format="TIFF")

    print(f"\nSubtracted images saved to: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subtract TIFF images from a reference image (memory-safe).")
    parser.add_argument("input_dir", help="Directory containing input TIFF images")
    parser.add_argument("subtract_file", help="Reference TIFF file to subtract from all input images")
    parser.add_argument("output_dir", help="Directory to save subtracted TIFF images")
    args = parser.parse_args()

    subtract_images(args.input_dir, args.subtract_file, args.output_dir)
