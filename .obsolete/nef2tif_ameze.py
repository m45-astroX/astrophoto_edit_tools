#!/usr/bin/env python3

import rawpy
import numpy as np
import os
import argparse
from glob import glob
from tifffile import imwrite
from rawpy._rawpy import DemosaicAlgorithm  # Enum を正しく使う

def convert_nef_to_tif(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = sorted(glob(os.path.join(input_dir, "*.NEF")))
    if not files:
        print("*** No NEF files found.")
        return

    print(f"Found {len(files)} NEF files.")

    for path in files:
        print(f"Processing {os.path.basename(path)} ...")
        try:
            with rawpy.imread(path) as raw:
                rgb = raw.postprocess(
                    output_bps=16,
                    gamma=(1, 1),
                    no_auto_bright=True,
                    use_camera_wb=True,
                    demosaic_algorithm=DemosaicAlgorithm.AHD,  # Enum を渡す
                    fbdd_noise_reduction=1
                )

                out_name = os.path.splitext(os.path.basename(path))[0] + ".tif"
                out_path = os.path.join(output_dir, out_name)
                imwrite(out_path, np.clip(rgb, 0, 65535).astype(np.uint16))
                print(f"✔ Saved: {out_path}")

        except Exception as e:
            print(f"*** Error processing {path}: {e}")

    print(f"\n✅ Conversion completed. TIFFs saved to: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert NEF to 16bit TIFF using AHD demosaic.")
    parser.add_argument("input_dir", help="Directory containing NEF files")
    parser.add_argument("output_dir", help="Directory to save TIFF files")
    args = parser.parse_args()

    convert_nef_to_tif(args.input_dir, args.output_dir)
