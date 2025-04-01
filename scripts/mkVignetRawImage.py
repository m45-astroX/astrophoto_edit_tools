#!/usr/bin/env python3

import matplotlib
matplotlib.use('TkAgg')
import argparse
import tifffile
import numpy as np
import cv2
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ExposureAdjuster:
    def __init__(self, image, color_channel, output_file):
        self.output_file = output_file
        self.original = image
        self.modified = np.zeros_like(image)
        self.color_map = {'r': 0, 'g': 1, 'b': 2}
        self.channel = self.color_map[color_channel]
        self.modified[:, :, self.channel] = image[:, :, self.channel]
        self.channel_data = self.modified[:, :, self.channel]
        self.corrected = self.channel_data.copy()
        self.scale_factor = 1.0

        self.root = tk.Tk()
        self.root.title("Exposure Correction")

        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        self.hist_line, = self.ax.plot([], [], lw=1)
        self.ax.set_yscale('log')
        #self.ax.set_title("Histogram after Exposure Adjustment")
        self.ax.set_xlabel("Pixel Value (16bit)")
        self.ax.set_ylabel("Pixels")
        self.ax.set_xlim(0, 65535)

        ttk.Label(self.root, text='Set Peak Value:').pack()
        self.peak_var = tk.IntVar(value=int(np.median(self.channel_data)))
        self.entry = ttk.Entry(self.root, textvariable=self.peak_var, width=10)
        self.entry.pack()
        self.apply_button = ttk.Button(self.root, text='Apply', command=lambda: self.update_exposure(self.peak_var.get()))
        self.apply_button.pack(pady=5)

        self.button = ttk.Button(self.root, text="Save", command=self.save_image)
        self.button.pack(pady=5)
        ttk.Button(self.root, text='Exit', command=self.root.quit).pack(pady=5)

        self.update_exposure(self.peak_var.get())
        self.root.mainloop()

    def update_exposure(self, value):
        value = float(value)
        self.scale_factor = 65535.0 / value
        corrected = (self.channel_data * self.scale_factor).clip(0, 65535).astype(np.uint16)
        self.corrected = corrected

        hist, bin_edges = np.histogram(self.corrected, bins=1000, range=(0, 65535))
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        self.hist_line.set_data(bin_centers, hist + 1)
        self.ax.set_ylim(1, np.max(hist + 1) * 1.1)
        self.canvas.draw()

    def save_image(self):
        output = np.zeros_like(self.original)
        output[:, :, self.channel] = self.corrected
        tifffile.imwrite(self.output_file, output)
        print(f"    Output : '{self.output_file}'")


def main(input_file, color, output_file):
    image = tifffile.imread(input_file)
    if image.dtype != np.uint16 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Only 16-bit 3-channel RGB TIFF images are supported.")
    ExposureAdjuster(image, color, output_file)

if __name__ == "__main__" :
    
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input 16-bit TIFF file")
    parser.add_argument("--color", required=True, choices=['r', 'g', 'b'], help="Color channel to adjust")
    parser.add_argument('--output', default='corrected_output.tif', help='Output TIFF filename')
    args = parser.parse_args()
    main(args.input, args.color, args.output)
