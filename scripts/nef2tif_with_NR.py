#!/usr/bin/env python3

import rawpy
import numpy as np
import os
import argparse
from glob import glob
from tifffile import imwrite
from rawpy import DemosaicAlgorithm
from rawpy import FBDDNoiseReductionMode

def main(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = sorted(glob(os.path.join(input_dir, "*.NEF")))
    if not files:
        print("*** No NEF files found.")
        return

    print(f"Found {len(files)} NEF files.")

    for path in files:
        print(f"Processing {os.path.basename(path)} ...")
        with rawpy.imread(path) as raw:
            print("Assuming RAW bit depth is 14 bits")

            # RAWを16bitで展開（線形補正、ガンマ補正なし）
            rgb = raw.postprocess(
                output_bps=16,
                gamma=(1, 1),
                no_auto_bright=True,
                use_camera_wb=True,
                demosaic_algorithm=DemosaicAlgorithm.AMAZE,
                fbdd_noise_reduction=FBDDNoiseReductionMode.Full,
                median_filter_passes=1
            )

            # 14bit相当の範囲(0-16383)から16bit範囲(0-65535)へスケーリング
            rgb = (rgb.astype(np.float32) * (65535.0 / 16383.0)).clip(0, 65535).astype(np.uint16)

            out_name = os.path.splitext(os.path.basename(path))[0] + ".tif"
            out_path = os.path.join(output_dir, out_name)
            imwrite(out_path, rgb)

    print(f"\n✅ Conversion completed. TIFs saved to: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Directory containing NEF files")
    parser.add_argument("output_dir", help="Directory to save TIF files")
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
