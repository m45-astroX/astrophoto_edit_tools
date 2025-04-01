import matplotlib
matplotlib.use('TkAgg')

#!/usr/bin/env python3

import argparse
import tifffile
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

def on_click(event, ax, fig, bin_centers, hist, callback):
    x = event.xdata
    if x is not None:
        callback(x)
        fig.canvas.mpl_disconnect(fig._click_cid)
        plt.close(fig)

def select_peak_gui(hist, bin_centers):
    root = tk.Tk()
    root.title("Histogram Viewer")

    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    ax.plot(bin_centers, hist)
    ax.set_yscale("log")
    ax.set_title("Click on peak value to normalize (log scale)")
    ax.set_xlabel("Pixel Value")
    ax.set_ylabel("Frequency")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

    selected_x = {}

    def callback(x):
        selected_x["value"] = x
        root.quit()

    fig._click_cid = fig.canvas.mpl_connect("button_press_event", lambda event: on_click(event, ax, fig, bin_centers, hist, callback))
    tk.mainloop()
    root.destroy()

    return selected_x.get("value", None)

def main(input_path, output_path, color, ev):
    image = tifffile.imread(input_path)
    if image.dtype != np.uint16:
        raise ValueError("Only 16-bit TIFF images are supported.")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Image must be a 3-channel RGB TIFF.")

    color_map = {'r': 0, 'g': 1, 'b': 2}
    keep_index = color_map[color]
    modified = np.zeros_like(image)
    modified[:, :, keep_index] = image[:, :, keep_index]

    # ヒストグラム生成
    flat = modified[:, :, keep_index].flatten()
    hist, bin_edges = np.histogram(flat, bins=1000, range=(0, 65535))
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # GUI でピーク選択
    selected_peak = select_peak_gui(hist, bin_centers)
    if selected_peak is None:
        print("*** Error ***\nNo peak selected.\nAbort.")
        return

    # EVスケーリング
    scale = 255.0 / selected_peak
    scale *= 2 ** ev

    corrected = (modified * scale).clip(0, 65535).astype(np.uint16)
    tifffile.imwrite(output_path, corrected)

    # EV補正後のヒストグラムを保存
    flat_corrected = corrected[:, :, keep_index].flatten()
    hist_corr, bin_edges_corr = np.histogram(flat_corrected, bins=1000, range=(0, 65535))
    bin_centers_corr = (bin_edges_corr[:-1] + bin_edges_corr[1:]) / 2

    fig_corr, ax_corr = plt.subplots()
    ax_corr.plot(bin_centers_corr, hist_corr + 1)
    ax_corr.set_yscale('log')
    ax_corr.set_title('Histogram after EV Correction')
    ax_corr.set_xlabel('Pixel Value')
    ax_corr.set_ylabel('Log Frequency')
    ax_corr.grid(True)
    fig_corr.tight_layout()
    fig_corr.savefig("corrected_histogram.png")
    print("📊 Saved corrected histogram: corrected_histogram.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exposure correction by EV and channel selection")
    parser.add_argument("input", help="Input TIFF file")
    parser.add_argument("output", help="Output TIFF file")
    parser.add_argument("--color", required=True, choices=['r', 'g', 'b'], help="Color channel to process")
    parser.add_argument("--ev", type=float, default=0.0, help="Exposure adjustment in EV (default: 0)")
    args = parser.parse_args()

    main(args.input, args.output, args.color, args.ev)
