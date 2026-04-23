######################################
# This program was developed with help and code from the following sources:
# 
# - https://learnpython.com/blog/plot-waveform-in-python/, for audio processing section and audio file plotting
# - https://www.geeksforgeeks.org/python/reading-and-writing-lists-to-a-file-in-python/, for reading from a file
#
######################################

import os
import wave
import numpy as np
import matplotlib.pyplot as plt

# Change these to match desired data folder
recording_session = '20260413_213232'
recording_take = 1

# Change these for plotting purposes
# Units: seconds
x_lim_min = 0
x_lim_max = 361

# Import audio file and pressure_strain text file
audio_file = os.path.join('/Users/rgonzales/Documents/ThesisCode/DataCollect', recording_session, 'Recording_' + str(recording_take), 'mic.wav')
audio = wave.open(audio_file, 'rb')
data_path = os.path.join('/Users/rgonzales/Documents/ThesisCode/DataCollect', recording_session, 'Recording_' + str(recording_take), 'pressure_strain.txt')


######################################
# Audio processing

# Get important properties of audio recording
sample_rate = audio.getframerate()
num_samples = audio.getnframes()

# Obtain the two channels
signal_buffer = audio.readframes(num_samples)
signal_array = np.frombuffer(signal_buffer, dtype=np.int32)

# Due to how the ICS-43434 alternates between channels when outputting data, 
# even indices correspond to the "Left" channel and odd indices to the "Right" channel. 
# The microphone's channel select pin was tied to 5 V, so the useful signal is on the 
# "Right" channel.
signal = signal_array[1::2] # change this to [0::2] if "Left" is needed

# The MEMS microphone outputs 1 bit of high impedance, 24 bits of data, and ends 
# with 7 bits of high impedance. To get the proper value reading, we shift each 
# int32 in the array by 7 bits to the right.
shifted_signal = []
for i in range (0, len(signal)):
    temp = signal[i] >> 7
    shifted_signal.append(temp)

# Create time array for plotting
length = num_samples/sample_rate
time_audio = np.linspace(0, length, num = num_samples)

# Create vertical axis bounds for plotting.
# 10% gap between maximum amplitude and border of plot, 
# ignoring the peak in the first second of recording
left_ignore = 1 * sample_rate
y_min_lim = np.min(shifted_signal[left_ignore:]) - 0.1 * np.abs(np.min(shifted_signal[left_ignore:]))
y_max_lim = np.max(shifted_signal[left_ignore:]) + 0.1 * np.abs(np.max(shifted_signal[left_ignore:]))

######################################
# Serial data processing
# Recall each line has the following format (without commas):
# (index, time [ms], diff_pressure [kPa], gauge_pressure [kPa], strain_left [lbs], strain_top [lbs], strain_right [lbs])

data_array = []
with open(data_path, '+r') as file:
    for line in file:
        # Split each line of data at the whitespace characters
        # Convert all values into floats
        items = line.split()
        for i in range(len(items)):
            items[i] = float(items[i])
        data_array.append(items)

# For easier time with plotting
data_array = np.array(data_array)

# Data conversions
MS_TO_S = 0.001
# KPA_TO_CMH20 = 10.19716
LBS_TO_KG = 1 / 2.20462
GRAVITY = 9.80665

time = data_array[:,1] * MS_TO_S
diff_pressure = data_array[:,2]
gauge_pressure = data_array[:,3]
strain_left = (data_array[:,4] - data_array[0, 4]) * LBS_TO_KG * GRAVITY
strain_top = (data_array[:,5] - data_array[0, 5]) * LBS_TO_KG * GRAVITY
strain_right = (data_array[:,6] - data_array[0, 6]) * LBS_TO_KG * GRAVITY


# Adjust plt.xlim arguments to make sure they are valid
if (x_lim_min < 0): x_lim_min = 0
if (x_lim_max > length): x_lim_max = length

# Plot audio, pressure, and force together, aligned with respect to time
plt.figure(figsize=(15, 10))

plt.subplot(3,1,1)
plt.plot(time_audio, shifted_signal, label='Audio')
plt.title('Audio Waveform')
plt.ylabel('Amplitude')
plt.xlim(x_lim_min, x_lim_max)
plt.ylim(y_min_lim, y_max_lim)
plt.legend()

plt.subplot(3,1,2)
plt.plot(time, data_array[:,2], label='Diff. Pressure Sensor')
plt.plot(time, data_array[:,3], label='Gauge Pressure Sensor')
plt.title('Pressure Sensor Data')
plt.ylabel('Kilopascals [kPa]')
plt.xlim(x_lim_min, x_lim_max)
plt.legend()

plt.subplot(3,1,3)
plt.plot(time, strain_left, label='Bottom Left Gauge')
plt.plot(time, strain_top, label='Top Center Gauge')
plt.plot(time, strain_right, label='Bottom Right Gauge')
plt.plot(time, strain_left + strain_top + strain_right, label='Total Force')
plt.title('Strain Gauge Data')
plt.xlabel('Time [s]')
plt.ylabel('Newtons [N]')
plt.xlim(x_lim_min, x_lim_max)
plt.legend()

plt.show()