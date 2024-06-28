# Droplet-ejector-GUI
A GUI for RPi4 that controls RP2040 imager unit attached to droplet ejector. 

# Introduction
This repository contains Python scripts for a GUI for GHz ultrasonic imager (RP2040) connected to a Raspberry Pi 4 system. The scripts handle data acquisition, real-time visualization, as well as further processed averaged pixel plots of the ultrasonic imaging data. There are two plot windows in this GUI: one showing the processed ultrasonic image (Magnitude/V with baseline adjusted) and the other plotting average of all pixels vs time that updates as new images are captured in real-time. 

# Features
These scripts are designed to:
1. Initialize the ultrasonic imager settings
2. On-demand acquisition of the background frame (calibration)
3. Acquire ultrasonic data and store them in a new directory for each experiment/run
4. Plot the real-time 2D Magntidue and the average of all pixels in two separate plots that updates in real-time

# Prerequisites
Before you use any of the scripts, ensure you have the following installed in your RPi4:
1. Python 3. x installed'
2. Python library specific to RP2040 connections: spidev, RPi.GPIO, serial
3. Python libraries for operations and GUI: sys, os, time, math, NumPy, tkinter
4. Python libraries for image generation, visualization, and analysis: matplotlib

Before installing any new modules

Python 3 is usually pre-installed on RPi4. You can check by running:

```bash
python3 --version
```
If not installed, you can install it using:

```bash
sudo apt-get update
sudo apt-get install python3
```

You can combine the commands to install everything in one go:
```bash
sudo apt-get install python3 python3-spidev python3-rpi.gpio python3-serial python3-numpy python3-tk python3-matplotlib
```

Else, you can follow step-wise installation of individual modules:


Python libraries specific to RP2040 connections: spidev, RPi.GPIO, serial
```bash
sudo apt-get install python3-spidev
sudo apt-get install python3-rpi.gpio
sudo apt-get install python3-serial
```

Python libraries for operations and GUI: sys, os, time, math, NumPy, tkinter

```bash
sudo apt-get install python3-numpy
sudo apt-get install python3-tk
```

Python libraries for image generation, visualization, and analysis: matplotlib

```bash
sudo apt-get install python3-matplotlib
```

# Image acquisition and processing scripts
The following scripts all allow for data acquisition using the Opal Kelly Imager. Each acquisition script has a section that allows users to load the raw data to generate images and compute different acoustic parameters.

1. **Geegah_RP2040_Liveimaging.py**: Acquisition of N number of frames with an option to visualize them in real-time for the entire 128 x 128 pixels. This operates at a fixed frequency and echo acquisition timing.
2.  **Geegah_RP2040_Liveimaging_withNoEcho.py**: Acquisition of N number of frames with an option to visualize them in real-time for the entire 128 x 128 pixels. This operates at a fixed frequency and echo acquisition timing. This also includes acquiring baseline acquisition at a later time when the echo dies off which can be used to calculate the true signal change of the samples yielding more accurate Acoustic Impedance.
3. **Geegah_RP2040_FrequencySweep.py**: Acquisition of images at a range of frequencies (1.5 - 2.0 GHz, with a step as low as 0.01 MHz). Allows capturing N frames at a fixed acquisition echo timing.


# Helper libraries
These consist of classes or functions that support the acquisition and processing of scripts. These do not have to be run individually.

1. **geegah_hp.py** Helper functions for image acquisition and post-processing


# Getting started: 

**Clone the repository**
```bash
git clone git@github.com:Geegah-Inc/Geegah-RP2040.git
```
