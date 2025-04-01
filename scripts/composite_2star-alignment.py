#!/usr/bin/env python3

import numpy as np
import cv2
import matplotlib
matplotlib.use('GTK3Agg')
import matplotlib.pyplot as plt
from tifffile import imread, imwrite
import argparse
import os
from glob import glob
import tempfile
import pickle
import gc


def compute_centroid(image, cx, cy, box_size) :

    half = box_size // 2
    y1, y2 = int(cy - half), int(cy + half)
    x1, x2 = int(cx - half), int(cx + half)
    subimg = image[y1:y2, x1:x2]
    Y, X = np.mgrid[y1:y2, x1:x2]
    total = np.sum(subimg)
    if total == 0:
        return (cx, cy)
    cx_centroid = np.sum(X * subimg) / total
    cy_centroid = np.sum(Y * subimg) / total
    print(f"    (x, y)   = {cx_centroid:.1f}, {cy_centroid:.1f} ")
    print(f"    (Rx, Ry) = {cx}, {cy}")
    return (cx_centroid, cy_centroid)


def select_star_point(image, title, box_size) :

    coords = []

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            coords.append((int(event.xdata), int(event.ydata)))
            plt.close()

    def onscroll(event):
        ax = plt.gca()
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return
        scale_factor = 1.2 if event.button == 'up' else 0.8
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        plt.draw()

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(image, cmap='gray')
    ax.set_title(title)
    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('scroll_event', onscroll)
    plt.show()

    if coords:
        return compute_centroid(image, coords[0][0], coords[0][1], box_size)
    else:
        print("*** No star selected.")
        return None


def compute_transform(ref_pts, tgt_pts) :

    ref = np.array(ref_pts, dtype=np.float32)
    tgt = np.array(tgt_pts, dtype=np.float32)
    matrix = cv2.estimateAffinePartial2D(tgt, ref)[0]
    return matrix


def main(input_dir, output_file, box_size) :

    files = sorted(glob(os.path.join(input_dir, "*.tif")))
    if not files:
        print("*** No TIFF files found.")
        return

    ref_image = imread(files[0])
    gray_ref = np.mean(ref_image, axis=2) if ref_image.ndim == 3 else ref_image
    h, w = gray_ref.shape
    
    print("\n=== Starting star selecting phase ===")
    ref_star1 = select_star_point(gray_ref, "    Click on reference star 1", box_size)
    ref_star2 = select_star_point(gray_ref, "    Click on reference star 2", box_size)
    if ref_star1 is None or ref_star2 is None:
        print("*** Reference selection failed.")
        return
    ref_pts = [ref_star1, ref_star2]

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl")
    star_positions = []

    for idx, path in enumerate(files):
        print(f"\n[{idx+1}/{len(files)}] {os.path.basename(path)}")
        if idx == 0:
            star_positions.append((ref_star1, ref_star2))
        else:
            image = imread(path)
            gray = np.mean(image, axis=2) if image.ndim == 3 else image
            star1 = select_star_point(gray, f"    Click on star 1 ({os.path.basename(path)})", box_size)
            star2 = select_star_point(gray, f"    Click on star 2 ({os.path.basename(path)})", box_size)
            if star1 is None or star2 is None:
                print("*** Skipping image due to star selection failure.")
                star_positions.append(None)
            else:
                star_positions.append((star1, star2))
            del image, gray
            gc.collect()

    with open(tmp_file.name, "wb") as f:
        pickle.dump(star_positions, f)

    print("\n=== Starting Compositing Phase ===")
    with open(tmp_file.name, "rb") as f:
        star_positions = pickle.load(f)

    composite = None
    count = 0

    for idx, path in enumerate(files):
        print(f"[Composite {idx+1}/{len(files)}] {os.path.basename(path)}")
        image = imread(path)
        if idx == 0:
            aligned = image.astype(np.float64)
        else:
            if star_positions[idx] is None:
                print("*** Skipping due to missing star positions.")
                continue
            gray = np.mean(image, axis=2) if image.ndim == 3 else image
            matrix = compute_transform(ref_pts, star_positions[idx])
            aligned = cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_LINEAR).astype(np.float64)

        if composite is None:
            composite = aligned
        else:
            composite += aligned
        count += 1
        del image, aligned
        gc.collect()

    if count == 0:
        print("*** Error")
        print("No images successfully processed.")
        return

    composite = np.clip(composite / count, 0, 65535).astype(np.uint16)
    imwrite(output_file, composite)
    print(f"    Output: {output_file}")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Directory with TIFF images")
    parser.add_argument("output_file", help="Output composite TIFF filename")
    parser.add_argument("--box", type=int, default=30, help="Box size for star region (default: 30)")
    args = parser.parse_args()

    print("BEGIN :: composite 2star-alignment")
    main(args.input_dir, args.output_file, args.box)
    print("END :: composite 2star-alignment")
