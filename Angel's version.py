#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 16:50:18 2018

@author: angelhuang
"""
import pyaudio
import serial 
import numpy as np
import audioop
import sys
import math 
import struct

MAX= 0
MIN = 0

def list_devices():
    " list out all the audio input devices"
    player = pyaudio.PyAudio()
    i = 0 
    n = player.get_device_count()
    while i < n:
        dev = player.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(str(i)+'. '+dev['name'])
        
        i += 1

def arduino_soundlight():
    chunk = 2**11 #alter to change the speed of changing lights 
    scale = 40 #alter to change the brightness of LED
    exponent = 3 #lower to create more difference between loud and quiet sounds
    samplerate = 16000 
    
    device = 1
    
    player = pyaudio.PyAudio()
    stream = player.open(format = pyaudio.paInt16,\
                         channels = 1, \
                         rate = samplerate, \
                         input = True, \
                         frames_per_buffer = chunk, \
                         input_device_index = device)
    
    print("Starting.... use Ctrl+C to stop")
    
    try:
        ser = serial.Serial('COM5', timeout=1)

        while True:
            data  = stream.read(chunk)

            print(data)
            print(len(data))
            # Do FFT
            levels = calculate_levels(data, 8)
            # Make it look better and send to serial
            levels = np.interp(levels, (0, 30000), (0, 255))
            
            for level in levels:
                # level = max(min(level /scale, 1.0), 0.0)
                # level = level**exponent
                # level = int(level * 255)
                # print(level)
                # ser.write(struct.pack('>B', level))
                if not level > 70: #minimizes noise
                    level = 0
                level = int(level)
                print(level)
                ser.write(struct.pack('>B', level))


    except KeyboardInterrupt:
        pass
    finally:
        print("\nStopping")
        levels = [0, 0, 0, 0, 0, 0, 0]
        for level in levels: #turns all the LEDs off before closing
            level = 0
            ser.write(struct.pack('>B', level))
        stream.close()
        player.terminate()
        ser.close()
        print("Done")

def calculate_levels(chunk, num_leds):

    fmt = "%dH"%(len(chunk)/2)
    data_np = struct.unpack(fmt, chunk)
    data_np = np.array(data_np, dtype = 'h')

    # get magnitude of fft
    data = np.fft.rfft(data_np)
    fft = np.abs(data)/len(data)
    #freq = np.fft.rfftfreq(len(fft), d=1./(16000))
    #print("length", len(freq))
    #print("freq = ", freq) #= max is 7992
    #print("length =", len(fft))
    #print("mag = ", fft[:1000])
    #print("mag = ", fft[1000:2000])
    
    #fft1 = fft[1: int(len(data)/2)+ 1]
    fft1 = fft[:]

    # get indices of elements that are above the median
    #elements_above = np.where(fft1 > np.median(fft))[0]
    
    # get first such index occurance
    #first = min(elements_above)

    # get last such index occuance
    #last = max(elements_above)

    # log-scale and select relevant frequencies to consider (where most frequencies lie)
    # log scale because human loudness perception is in DB
    fft1 = np.log10(fft1[:])

    # get evenly spaced numbers
    # first and last "splits" are the beginnning and end of array so we remove them
    #bin_indicies = np.linspace(0, len(fft1)-1, num_leds+1)[1:-1]
    #bin_indicies = np.array([57, 64, 76, 85, 90, 101]) 
    
    # convert to int
    #bin_indicies = np.array(bin_indicies, dtype=int)
    """
    C: 18, (34-35), 68, 135, 269
    D: 20, 39, 76, 151, 302
    E: 22, 43, 85, 170, 339
    F: 23, 46, 90, 180, 359 
    G: 26, 51, 101, 202, 403
    A: 29, 57, 114, 209, 452
    B: 33, 64, (127-128), 254, 507
    """
    noteC = sum(fft[15:20]) + sum(fft[31:36]) + sum(fft[65:70]) + sum(fft[132:137]) + sum(fft[266:271])
    noteD = sum(fft[17:22]) + sum(fft[36:41]) + sum(fft[73:78]) + sum(fft[148:153]) + sum(fft[299:304])
    noteE = sum(fft[19:24]) + sum(fft[40:45]) + sum(fft[82:87]) + sum(fft[167:172]) + sum(fft[336:341])
    noteF = sum(fft[20:25]) + sum(fft[43:48]) + sum(fft[87:92]) + sum(fft[177:182]) + sum(fft[356:361])
    noteG = sum(fft[23:30]) + sum(fft[48:53]) + sum(fft[98:103]) + sum(fft[199:204]) + sum(fft[400:405])
    noteA = sum(fft[26:31]) + sum(fft[54:59]) + sum(fft[111:116]) + sum(fft[206:211]) + sum(fft[449:454])
    noteB = sum(fft[30:35]) + sum(fft[61:66]) + sum(fft[124:129]) + sum(fft[251:256]) + sum(fft[504:509])
                                                    
    # break up into bins and sum
    #levels = np.array([sum(x) for x in np.split(fft1, bin_indicies)])
    levels = np.array([noteC, noteD, noteE, noteF, noteG, noteA, noteB])
    return levels
    
if __name__ == '__main__':
    #list_devices()
    arduino_soundlight()
