#!/usr/bin/env python3

import os
import argparse
import numpy as np
import imageio.v2 as imageio

def load_tiff_images_from_directory(directory) :

    tiff_files = sorted([os.path.join(directory, f) for f in os.listdir(directory)
                        if f.lower().endswith(('.tif', '.tiff'))])

    if not tiff_files:
        print("*** Error ***")
        print("No TIFF files found in directory.")
        print("abort.")
        return None

    images = []
    for tiff_file in tiff_files:
        try:
            image = imageio.imread(tiff_file)
            if image.dtype != np.uint16:
                print(f"Warning: {tiff_file} is not 16bit. Converting to uint16.")
                image = (image.astype(np.float32) * (65535.0 / np.max(image))).astype(np.uint16)
            images.append(image)
            print(f"Loaded : {tiff_file}")
        except Exception as e:
            print("*** Error ***")
            print(f"Failed to load {tiff_file}: {e}")
            continue

    return images if images else None


def composite_images(images, method="mean") :
    if not images:
        print("*** Error ***")
        print("No valid images to composite.")
        print("abort.")
        return None

    images_stack = np.stack(images, axis=0)
    composite = np.zeros_like(images_stack[0], dtype=np.uint16)

    for c in range(3):
        if method == "mean":
            composite[..., c] = np.clip(np.mean(images_stack[..., c], axis=0), 0, 65535).astype(np.uint16)
        elif method == "max":
            composite[..., c] = np.clip(np.max(images_stack[..., c], axis=0), 0, 65535).astype(np.uint16)
        elif method == "min":
            composite[..., c] = np.min(images_stack[..., c], axis=0).astype(np.uint16)
        else:
            print("*** Error ***")
            print("Invalid method. Use 'mean', 'max', or 'min'.")
            print("abort.")
            return None

    return composite


def main() :

    parser = argparse.ArgumentParser(description="TIFF Image Composite Script")
    parser.add_argument("indir", help="Input directory containing 16bit TIFF files")
    parser.add_argument("-o", "--outfile", default="composite.tif", help="Output filename (default: composite.tif)")
    parser.add_argument("-m", "--method", choices=["mean", "max", "min"], default="mean", help="Composite method")

    args = parser.parse_args()
    images = load_tiff_images_from_directory(args.indir)

    if images:
        composite_image = composite_images(images, args.method)
        if composite_image is not None:
            imageio.imwrite(args.outfile, composite_image, format='TIFF')
            print(f"    Output : {args.outfile}")


if __name__ == "__main__" :

    print("BEGIN :: composite")
    main()
    print("END :: composite")
