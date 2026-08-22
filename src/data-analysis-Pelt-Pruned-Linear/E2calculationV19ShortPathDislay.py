#created by Silvio Maetzke, as tool to find in SOC signal best point to recharge  battery via range extender or Fuel cell
#V18 insterad of only .mat file now also dat or mf4 files
import numpy as np
import matplotlib.pyplot as plt
import ruptures as rpt
from scipy.signal import savgol_filter
import pandas as pd
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.io import loadmat
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
from asammdf import MDF



# Clear Console Output
os.system('cls')
# Clear previous plots
plt.clf()  # Clear the current figure
plt.cla()  # Clear the current axes
plt.close()  # Close the current figure

# Create the main window
root = tk.Tk()
root.title("Drive Cycle Selection")

# Define global variables
flip_DeltaSOC_Slope = False
selectedFile = ""
penalty = 100
min_segment_length = 200
frac = 0.02

signal_names = []
mdf = None
SOC_signal_var = tk.StringVar()  # Initialize after root window

def on_submit():
    global flip_DeltaSOC_Slope, selectedFile, penalty, min_segment_length, frac
    flip_DeltaSOC_Slope = bool(delta_soc_slope_var.get())
    selectedFile = file_var.get()
    penalty = int(penalty_var.get())
    min_segment_length = int(min_segment_length_var.get())
    frac = float(frac_var.get())
    print(f"Flip Delta SOC/Slope: {flip_DeltaSOC_Slope}")
    print(f"browsed File: {selectedFile}")
    print(f"Penalty: {penalty}")
    print(f"Min Segment Length: {min_segment_length}")
    print(f"smooth SOC frac small more spike: range [0,1]: {frac}")
    root.destroy()

def load_file():
    global mdf, data
    file_path = filedialog.askopenfilename(initialdir="test_data", filetypes=[("Data files", "*.mf4 *.dat *.mat")])
    if not file_path:
        return
    file_var.set(file_path)
    ext = file_path.split('.')[-1].lower()

    try:
        signal_names.clear()
        if ext in ['mf4', 'dat']:
            mdf = MDF(file_path)
            signal_names.extend(list(mdf.channels_db.keys()))
        elif ext == 'mat':
            data = loadmat(file_path)
            signal_names.extend(list(data.keys()))
        else:
            messagebox.showerror("Error", f"Unsupported file type: .{ext}")
            return

        SOC_dropdown['values'] = signal_names
        if signal_names:
            SOC_signal_var.set(signal_names[0])

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {e}")

# Create a label and dropdown for Delta SOC/Slope selection
delta_soc_slope_label = ttk.Label(root, text="Select Delta SOC/Slope Condition:")
delta_soc_slope_label.pack(pady=5)

delta_soc_slope_var = tk.IntVar()
delta_soc_slope_dropdown = ttk.Combobox(root, textvariable=delta_soc_slope_var)
delta_soc_slope_dropdown['values'] = (0, 1)
delta_soc_slope_dropdown.current(0)
delta_soc_slope_dropdown.pack(pady=5)

# File selection
file_var = tk.StringVar()
ttk.Label(root, text="Select .mat, .mf4, or .dat file:").pack(pady=5)
ttk.Button(root, text="Browse", command=load_file).pack(pady=5)
ttk.Label(root, textvariable=file_var, wraplength=400).pack(pady=5)

# SOC signal selection
ttk.Label(root, text="Select SOC Signal:").pack(pady=5)
SOC_dropdown = ttk.Combobox(root, textvariable=SOC_signal_var, width=50)
SOC_dropdown.pack(pady=5)

# Penalty
penalty_label = ttk.Label(root, text="Penalty:")
penalty_label.pack(pady=5)
penalty_var = tk.StringVar(value=str(penalty))
penalty_entry = ttk.Entry(root, textvariable=penalty_var)
penalty_entry.pack(pady=5)

# Min Segment Length
min_segment_length_label = ttk.Label(root, text="Min Segment Length:")
min_segment_length_label.pack(pady=5)
min_segment_length_var = tk.StringVar(value=str(min_segment_length))
min_segment_length_entry = ttk.Entry(root, textvariable=min_segment_length_var)
min_segment_length_entry.pack(pady=5)

# Frac for smoothing SOC signal
frac_label = ttk.Label(root, text="smooth SOC frac small more spike: range [0,1]:")
frac_label.pack(pady=5)
frac_var = tk.StringVar(value=str(frac))
frac_entry = ttk.Entry(root, textvariable=frac_var)
frac_entry.pack(pady=5)

# Submit button
submit_button = ttk.Button(root, text="Submit", command=on_submit)
submit_button.pack(pady=20)

root.mainloop()

# Load the selected signal
try:
    if isinstance(mdf, MDF):
        SOC_signal = mdf.get(SOC_signal_var.get())
        SOC = SOC_signal.samples
        time = SOC_signal.timestamps
    else:
        SOC = data[SOC_signal_var.get()].squeeze()
        if 'time' in data:
            time = data['time'].squeeze()
        else:
            time_raster = 0.1
            time_array = np.arange(0, len(SOC) * time_raster, time_raster)
            SOC = SOC[4:]
            time = time_array[4:]

except Exception as e:
    print(f"An error occurred: {e}")

# LOWESS Smoothing
SOC_smooth = lowess(SOC, time, frac=frac, return_sorted=False)

# Prepare signal
signal = np.column_stack((SOC_smooth, time))

# PELT Change Point Detection
cp_linear = rpt.Pelt(model="linear", min_size=min_segment_length).fit(signal).predict(pen=penalty)
segment_edges = [0] + cp_linear

# Analyze Segments
n_segments = len(segment_edges) - 1
slopes = np.zeros(n_segments)
means = np.zeros(n_segments)
delta_SOC = np.zeros(n_segments)
durations = np.zeros(n_segments)

for i in range(n_segments):
    idx1 = segment_edges[i]
    idx2 = segment_edges[i+1]
    seg_time = time[idx1:idx2+1]
    seg_SOC = SOC[idx1:idx2+1]
    p = np.polyfit(seg_time, seg_SOC, 1)
    slopes[i] = p[0]
    means[i] = np.mean(seg_SOC)
    delta_SOC[i] = seg_SOC[-1] - seg_SOC[0]
    durations[i] = seg_time[-1] - seg_time[0]

slope_threshold = np.percentile(slopes, 75)
is_rising = slopes > slope_threshold
is_declining = slopes < 0

max_delta_SOC = np.max(delta_SOC)
if flip_DeltaSOC_Slope:
    big_rise_idx = np.argmax(delta_SOC)
else:
    big_rise_idx = np.argmax(slopes)

for i in range(big_rise_idx, big_rise_idx + 20):
    if not is_declining[i + 1]:
        big_rise_idx += 1
    else:
        break

T1 = time[segment_edges[big_rise_idx]]
T2 = time[segment_edges[big_rise_idx + 1]]
SOC_peak = SOC[segment_edges[big_rise_idx + 1]]
SOC_init = SOC[0]

min_fail_magnitude = 0.5 * max_delta_SOC
failing_segments = np.where(delta_SOC < -min_fail_magnitude)[0]
failing_after_rise = failing_segments[failing_segments > big_rise_idx]

if failing_after_rise.size > 0:
    first_fail_idx = failing_after_rise[0]
    big_fall_idxs = [first_fail_idx]
    for k in range(1, len(failing_after_rise)):
        if failing_after_rise[k] - failing_after_rise[k - 1] <= 3:
            big_fall_idxs.append(failing_after_rise[k])
        else:
            break
    T1_fall = time[segment_edges[big_fall_idxs[0]]]
    T2_fall = time[segment_edges[big_fall_idxs[-1] + 1]]
    T3 = T1_fall
else:
    big_fall_idxs = []
    T1_fall = np.nan
    T2_fall = np.nan
    T3 = np.nan

cell_capacity = 20.4
N = 96
nominal_voltage = 4.2
E2 = cell_capacity * 3600 * N * nominal_voltage * (SOC_peak - SOC_init) / 100 / 1000
print('E2=', E2)
print('T2', T2)
print('BigRiseAfterUpdata', big_rise_idx)
print('SOCPeak', SOC_peak)
print('SOCinit', SOC_init)

plt.figure('Robust SOC Change Detection', figsize=(14, 6.5))
plt.subplot(2, 1, 1)
plt.plot(time, SOC, color=[0.3, 0.3, 1], linewidth=1.2)
plt.title('SOC vs Time with Key Segments')
plt.xlabel('Time (s)')
plt.ylabel('SOC (%)')
plt.grid(True)
plt.legend([f'E2 needed energy to charge [kJ]: {E2}\n T2 timestamp of E2 position [s]:{T2}'], loc='best')

for i in range(n_segments):
    idx1 = segment_edges[i]
    idx2 = segment_edges[i+1]
    if is_rising[i]:
        plt.plot(time[idx1:idx2+1], SOC[idx1:idx2+1], 'r-', linewidth=2.0)

plt.subplot(2, 1, 2)
colors = ['red' if i == big_rise_idx else 'green' for i in range(n_segments)]
bars = plt.bar(range(n_segments), slopes, color=colors, width=0.8)
plt.title('Slopes vs Segment Number')
plt.xlabel('Segment Number')
plt.ylabel('Slope')
plt.grid(True)
plt.legend([bars[big_rise_idx]], [f'Big Rise Segment: {big_rise_idx}\n Selected Drive cycle file: {selectedFile} \n delta_init_SOC Max 1 or Slope based 0: {flip_DeltaSOC_Slope}'], loc='upper right')

plt.tight_layout()

plt.figure('Pelt segment Plot', figsize=(14, 6))
plt.plot(time, SOC, label='Original SOC', color='gray', alpha=0.4)
plt.plot(time, SOC_smooth, label='LOWESS Smoothed SOC', color='blue', linewidth=2)

colors = plt.cm.plasma(np.linspace(0, 1, len(segment_edges) - 1))

for i in range(len(segment_edges) - 1):
    start = segment_edges[i]
    end = segment_edges[i + 1]
    plt.plot(time[start:end], SOC_smooth[start:end],
             color=colors[i], linewidth=2.5,
             label=f'Segment {i+1}' if i < 10 else None)

for j, cp in enumerate(cp_linear[:-1]):
    plt.axvline(time[cp], color='red', linestyle='--', linewidth=1.2,
                label='Change Point' if j == 0 else None)

plt.xlabel('Time (s)')
plt.ylabel('SOC (%)')
plt.title('PELT Change Point Detection — Linear Model on LOWESS-Smoothed SOC')
plt.legend(loc='best')
plt.grid(True)
plt.tight_layout()
plt.show()

os.system('cls' if os.name == 'nt' else 'clear')
sys.exit()