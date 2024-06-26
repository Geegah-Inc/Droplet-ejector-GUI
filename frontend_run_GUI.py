# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 19:47:56 2024

@author: anujb
"""

# gui.py

import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import serial
from acquisition_backend import (
    load_sensor_settings, 
    acquire_frame, 
    process_frame, 
    acquire_air_frame
)
import time

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GHz Ultrasonic Droplet Analysis")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close event

        self.base_dir = "/home/geegahimager/Documents/RaspberryPi_Anuj/DATA"
        self.ser = serial.Serial('/dev/ttyACM0', 115200)
        self.freq_target_MHz = 1853
        self.timing = 125
        self.spi_obj_pico, self.n_bytes_block_arg = load_sensor_settings(self.ser, self.freq_target_MHz, self.timing)
        self.baseline_magnitude = acquire_air_frame(self.spi_obj_pico, self.n_bytes_block_arg, 1)
        self.update_plot = None
        self.running = False
        self.start_time = None
        self.animating_light = None

        # Set the dark theme with a stylish look
        self.configure(bg='black')

        # Resize the GUI window to match 800x480 display
        self.geometry('800x480')

        # Create frames for layout
        self.top_frame = tk.Frame(self, width=800, height=50, bg='black')
        self.top_frame.pack_propagate(False)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        self.plot_frame = tk.Frame(self, width=600, height=400, bg='black')
        self.plot_frame.pack_propagate(False)
        self.plot_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.button_frame = tk.Frame(self, width=200, height=400, bg='black')
        self.button_frame.pack_propagate(False)
        self.button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.plot1_frame = tk.Frame(self.plot_frame, width=200, height=200, bg='black', highlightbackground="white", highlightthickness=1)
        self.plot1_frame.pack_propagate(False)
        self.plot1_frame.grid(row=0, column=0, padx=5, pady=5)

        self.plot2_frame = tk.Frame(self.plot_frame, width=200, height=200, bg='black', highlightbackground="white", highlightthickness=1)
        self.plot2_frame.pack_propagate(False)
        self.plot2_frame.grid(row=0, column=1, padx=5, pady=5)

        self.plot3_frame = tk.Frame(self.plot_frame, width=200, height=200, bg='black', highlightbackground="white", highlightthickness=1)
        self.plot3_frame.pack_propagate(False)
        self.plot3_frame.grid(row=1, column=0, padx=5, pady=5)

        self.plot4_frame = tk.Frame(self.plot_frame, width=200, height=200, bg='black', highlightbackground="white", highlightthickness=1)
        self.plot4_frame.pack_propagate(False)
        self.plot4_frame.grid(row=1, column=1, padx=5, pady=5)

        # Title label
        self.title_label = tk.Label(self.top_frame, text="GHz Ultrasonic Droplet Analysis", font=("Arial", 16, "bold"), fg='white', bg='black')
        self.title_label.pack(side=tk.TOP, pady=10)

        # Create a figure and axis for the first plot (real-time ultrasonic image)
        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_title('Real-time ultrasonic image', color='white', fontsize=12, fontname='Arial', weight='bold')
        self.ax1.set_xlabel('Cols', fontsize=10, fontname='Arial', color='white', weight='bold')
        self.ax1.set_ylabel('Rows', fontsize=10, fontname='Arial', color='white', weight='bold')
        self.fig1.patch.set_facecolor('black')
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.plot1_frame)
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a figure and axis for the second plot (real-time line plot)
        self.fig2, self.ax2 = plt.subplots()
        self.ax2.set_xlabel('Time (s)', fontsize=10, fontname='Arial', color='white', weight='bold')
        self.ax2.set_ylabel('Magnitude (V)', fontsize=10, fontname='Arial', color='white', weight='bold')
        self.ax2.tick_params(axis='x', colors='white', labelsize=10)
        self.ax2.tick_params(axis='y', colors='white', labelsize=10)
        self.fig2.patch.set_facecolor('black')
        self.ax2.spines['top'].set_color('white')
        self.ax2.spines['bottom'].set_color('white')
        self.ax2.spines['left'].set_color('white')
        self.ax2.spines['right'].set_color('white')
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.plot2_frame)
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create empty figures and axes for the third and fourth plots
        self.fig3, self.ax3 = plt.subplots()
        self.ax3.axis('off')  # Hide axes
        self.fig3.patch.set_facecolor('black')
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.plot3_frame)
        self.canvas3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig4, self.ax4 = plt.subplots()
        self.ax4.axis('off')  # Hide axes
        self.fig4.patch.set_facecolor('black')
        self.canvas4 = FigureCanvasTkAgg(self.fig4, master=self.plot4_frame)
        self.canvas4.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Load and display the image on top of the buttons
        self.image = PhotoImage(file='/home/geegahimager/Desktop/geegah.png')
        self.image = self.image.subsample(4, 4)  # Make the image smaller (100x100)
        self.image_label = tk.Label(self.button_frame, image=self.image, bg='black')
        self.image_label.pack(side=tk.TOP, pady=10)

        # Create buttons
        self.calibrate_button = ttk.Button(self.button_frame, text="Calibrate", command=self.calibrate)
        self.calibrate_button.pack(side=tk.TOP, pady=5)
        self.calibrate_button.configure(style="Blue.TButton")

        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.TOP, pady=5)
        self.start_button.configure(style="Green.TButton")

        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.TOP, pady=5)
        self.stop_button.configure(style="Red.TButton")

        # Create button styles
        style = ttk.Style()
        style.theme_use('clam')  # Use a theme that allows background color changes
        style.configure("Blue.TButton", foreground="blue", background="black", font=("Arial", 10, "bold"))
        style.configure("Green.TButton", foreground="green", background="black", font=("Arial", 10, "bold"))
        style.configure("Red.TButton", foreground="red", background="black", font=("Arial", 10, "bold"))
        style.configure("Disabled.TButton", foreground="grey", background="black", font=("Arial", 10, "bold"))

        # Initialize data for the second plot (real-time line plot)
        self.time_data = []
        self.magnitude_data = []

    def calibrate(self):
        self.baseline_magnitude = acquire_air_frame(self.spi_obj_pico, self.n_bytes_block_arg, 1)
        print("Calibration completed.")

    def start(self):
        if self.baseline_magnitude is not None:
            self.running = True
            self.disable_buttons()
            self.reset_plot()
            self.update_plot = self.plot_frames(np.zeros_like(self.baseline_magnitude))
            self.start_time = time.time()  # Record start time
            self.update()  # Ensure the first update call is immediate
            self.animate_light()  # Start light animation
            print("Acquisition started.")

    def reset_plot(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.set_title('Real-time ultrasonic image', color='white', fontsize=12, fontname='Arial', weight='bold')
        self.ax1.set_xlabel('Cols', fontsize=10, fontname='Arial', color='white', weight='bold')
        self.ax1.set_ylabel('Rows', fontsize=10, fontname='Arial', color='white', weight='bold')
        self.ax2.set_xlabel('Time (s)', fontsize=10, fontname='Arial', color='white', weight='bold')
        self.ax2.set_ylabel('Magnitude (V)', fontsize=10, fontname='Arial', color='white', weight='bold')
        self.ax2.tick_params(axis='x', colors='white', labelsize=10)
        self.ax2.tick_params(axis='y', colors='white', labelsize=10)
        self.ax2.spines['top'].set_color('white')
        self.ax2.spines['bottom'].set_color('white')
        self.ax2.spines['left'].set_color('white')
        self.ax2.spines['right'].set_color('white')
        self.canvas1.draw()
        self.canvas2.draw()
        self.time_data.clear()
        self.magnitude_data.clear()

    def update(self):
        if self.running:
            try:
                new_frame = acquire_frame(self.spi_obj_pico, self.n_bytes_block_arg)
                new_magnitude = process_frame(new_frame)
                frame_diff = new_magnitude - self.baseline_magnitude
                self.update_plot(frame_diff)

                # Update time and magnitude data for the second plot (real-time line plot)
                current_time = time.time() - self.start_time
                avg_magnitude = np.mean(frame_diff)
                self.time_data.append(current_time)
                self.magnitude_data.append(avg_magnitude)

                # Calculate rolling average to avoid memory issues
                if len(self.magnitude_data) > 100:
                    self.time_data = self.time_data[-100:]
                    self.magnitude_data = self.magnitude_data[-100:]

                self.ax2.plot(self.time_data, self.magnitude_data, color='blue')
                self.canvas2.draw()
            except Exception as e:
                print(f"Error during acquisition: {e}")
            self.after(50, self.update)  # Reduced delay to speed up acquisition

    def stop(self):
        self.running = False
        self.enable_buttons()
        if self.animating_light:
            self.after_cancel(self.animating_light)  # Stop light animation
        print("Acquisition stopped.")

    def plot_frames(self, frame_diff):
        img = self.ax1.imshow(frame_diff, cmap='Spectral', aspect='auto', vmin=-0.1, vmax=0.1)
        colorbar = self.fig1.colorbar(img, ax=self.ax1)
        colorbar.ax.tick_params(colors='white')
        self.canvas1.draw()

        def update_plot(frame_diff):
            img.set_data(frame_diff)
            self.canvas1.draw()

        return update_plot

    def animate_light(self):
        if self.running:
            self.image_label.config(fg='yellow')
            self.animating_light = self.after(500, self.animate_light_off)

    def animate_light_off(self):
        if self.running:
            self.image_label.config(fg='white')
            self.animating_light = self.after(500, self.animate_light)

    def disable_buttons(self):
        self.calibrate_button.state(["disabled"])
        self.calibrate_button.configure(style="Disabled.TButton")
        self.start_button.state(["disabled"])
        self.start_button.configure(style="Disabled.TButton")

    def enable_buttons(self):
        self.calibrate_button.state(["!disabled"])
        self.calibrate_button.configure(style="Blue.TButton")
        self.start_button.state(["!disabled"])
        self.start_button.configure(style="Green.TButton")

    def on_closing(self):
        self.running = False
        if self.animating_light:
            self.after_cancel(self.animating_light)  # Stop light animation
        self.ser.close()
        self.quit()  # Stop the Tkinter event loop
        self.destroy()
        print("Application closed.")

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
