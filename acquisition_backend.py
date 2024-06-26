# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 19:49:51 2024

@author: anujb
"""

# acquisition_backend.py

import os
import serial
import picoDAQ_Lib  # Custom functions for Data Acquisition
import RPi.GPIO as GPIO
import numpy as np
from datetime import datetime

# Function to create a unique directory with a timestamp
def create_unique_directory(base_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_dir = os.path.join(base_path, timestamp)
    os.makedirs(unique_dir)
    return unique_dir

# Function to initialize directories for raw data, images, and videos
def initialize_directories(base_dir):
    rawdata_echo_dir = os.path.join(base_dir, "rawdata_echo")
    img_save_dir = os.path.join(base_dir, "images")
    vid_save_dir = os.path.join(base_dir, "videos")
    
    os.makedirs(rawdata_echo_dir)
    os.makedirs(img_save_dir)
    os.makedirs(vid_save_dir)
    
    return rawdata_echo_dir, img_save_dir, vid_save_dir

# Function to load imager settings
def load_imager_settings(ser, freq_target_MHz, timing, mode=1, adc=1):
    #ser is the serial for RP2040 connected to RPi4 
    #freq_targer_MHz is frequency of the pulse in MHz
    #timing is the acquisition time where a frame is captured. This refers to time in ns right after RX is enabled/TX is disabled
    #mode is the acquisition mode, where mode = 1 refers to capturing the frame at one fixed timing

    
    # GPIO and SPI setup
    GPIO_PINNO_TEST = 27
    GPIO_NUM_VCO_LE = 7  # SPI0_CE1 from Rpi
    GPIO_NUM_DAC_MOSI = 10
    GPIO_NUM_DAC_MISO = 9
    GPIO_NUM_DAC_CLK = 11
    GPIO_NUM_DAC_CE = 8
    GPIO_NUM_DAC_CE0B = 22

    pinDict_Main = dict(gpio_num_PINNO_TEST=GPIO_PINNO_TEST,
                        gpio_num_DAC_CE0B=GPIO_NUM_DAC_CE0B,
                        gpio_num_VCO_LE=GPIO_NUM_VCO_LE)

    CLK_FREQ_SPI_PICO = int(5e6)

    picoDAQ_Lib.setup_GPIO(pinDict_arg=pinDict_Main)

    spi_obj_vco = picoDAQ_Lib.get_spi_vco()

    OUTEN_user = 1
    PSET_user = 3
    regs = picoDAQ_Lib.calc_vco_reg_values(freq_target_MHz, OUTEN_user, PSET_user)

    regshx = ["{:#010x}".format(reg) for reg in regs]
    print("The registers are:", regshx)

    regs_list_of_ints = list(map(picoDAQ_Lib.int2bytes, regs))

    for i in range(len(regs)-1, -1, -1):
        regToWrite_list = regs_list_of_ints[i]
        print("writing register", i, regToWrite_list)
        spi_obj_vco.writebytes(regToWrite_list)

    DAC_val = 3815
    spi_obj_dac = picoDAQ_Lib.get_spi_dac_MAXIM5123()
    picoDAQ_Lib.writeDAC_MAXIM5123(spi_obj_dac, DAC_val, GPIO_NUM_DAC_CE0B)

    spi_obj_pico = picoDAQ_Lib.get_spi_pico(CLK_FREQ_SPI_PICO)
    n_bytes_block_arg = 1 << 12

    packet = f"{mode}.{timing}.{adc}\n"
    ser.write(packet.encode())
    print(f"Settings sent: {packet}")

    return spi_obj_pico, n_bytes_block_arg

# Function to acquire a frame
def acquire_frame(spi_obj_pico, n_bytes_block_arg):
    frames_data_nD_baseline, timeStamp_1D_baseline, flagSignatureFound_1D_baseline, bufferSignature_1D_baseline, missedBlobCount_1D = picoDAQ_Lib.read_block_singleOrMultiple_frames_at_unsynchronized_state_BIN_1Frame(spi_obj_pico, n_bytes_block_arg)
    return frames_data_nD_baseline

# Function to process a frame and calculate magnitude
def process_frame(frame):
    #The captured byte data of a frame is converted to I and Q first, and then to Magnitdue 
    F_IMG_I, F_IMG_Q = picoDAQ_Lib.convertToIQImage(frame)
    I_AE_VOLTS, Q_AE_VOLTS = picoDAQ_Lib.convertADCToVolts(F_IMG_I, F_IMG_Q)
    MAG_AE = np.sqrt(np.square(I_AE_VOLTS) + np.square(Q_AE_VOLTS))
    return MAG_AE

# Function to acquire and process air frames
def acquire_air_frame(spi_obj_pico, n_bytes_block_arg, num_frames=1):
    magnitudes = []
    for _ in range(num_frames):
        frame = acquire_frame(spi_obj_pico, n_bytes_block_arg)
        magnitude = process_frame(frame)
        magnitudes.append(magnitude)
    if num_frames > 1:
        return np.mean(magnitudes, axis=0)
    else:
        return magnitudes[0]
