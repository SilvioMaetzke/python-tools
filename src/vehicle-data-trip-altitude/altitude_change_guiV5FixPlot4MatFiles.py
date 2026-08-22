# created by Silvio Maetzke
# altitude_changeGui.py to load data from different file conventions
# for speed, slope additionla acceleration and SOC 
#V2 with selecting speed either default [m/s] or [km/h] or [mph] And selecting [deg] or [rad} for slope signal
#V3 example .dat file seems to have not valid UTF-8 encoding format , though made it more robust
#V4 additional file form .mat from Matlab data files
#V5 fix plot feature in case of mat file needed time stamp from mat file
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from asammdf import MDF
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import loadmat  #V4 needed for mat files

# Create the main application window
root = tk.Tk()
root.title("Altitude Change Calculator")

# Create a label with multi-line text
label = tk.Label(root, text="Altitude Change Calculator V5\ncreated by Silvio Maetzke", font=("Arial", 8))
label.pack(pady=20)

file_var = tk.StringVar()
acc_signal_var = tk.StringVar()
speed_signal_var = tk.StringVar()
slope_signal_var = tk.StringVar()
soc_signal_var = tk.StringVar()
speed_unit_var = tk.StringVar(value="m/s")  #V2 Default unit
slope_unit_var = tk.StringVar(value="deg")  #V2 Default to degrees


signal_names = []
mdf = None
# Function to load .mf4, .dat, or .mat file and populate dropdowns
def load_file():
    global mdf
    file_path = filedialog.askopenfilename(initialdir=".", filetypes=[("Data files", "*.mf4 *.dat *.mat")])
    if not file_path:
        return
    file_var.set(file_path)
    ext = file_path.split('.')[-1].lower()

    try:
        signal_names.clear()
        # Use asammdf to read .mf4 and .dat files
        if ext in ['mf4', 'dat']:
            mdf = MDF(file_path)
            signal_names.extend(list(mdf.channels_db.keys()))
        # Use scipy.io.loadmat to read .mat files
        elif ext == 'mat':
            mat_data = loadmat(file_path)
            
            signal_names.extend(list(mat_data.keys()))
            # Assuming the signals are stored in a specific key, e.g., 'signals'
            # You may need to adjust this based on your .mat file structure
           # if 'signals' in mat_data:
            #    signal_names.extend(mat_data['signals'].dtype.names)
            #else:
             #   messagebox.showerror("Error", "No signals found in .mat file")
              #  return
        else:
            messagebox.showerror("Error", f"Unsupported file type: .{ext}")
            return

        # Limitation or filter for right signals based on naming
        acc_keywords = ['Accel', 'acc', '_a_', '_dn_', 'acceleration']
        acc_candidates = [s for s in signal_names if any(k in s.lower() for k in acc_keywords)]
        speed_keywords = ['speed', 'spd', '_v_', '_n_', 'vehicle_speed']
        speed_candidates = [s for s in signal_names if any(k in s.lower() for k in speed_keywords)]
        slope_keywords = ['PLTR', 'angle', '_phi_', 'slope']
        slope_candidates = [s for s in signal_names if any(k in s.lower() for k in slope_keywords)]
        soc_keywords = ['SOC', 'soc', '_p_', 'Power', 'Batt']
        soc_candidates = [s for s in signal_names if any(k in s.lower() for k in soc_keywords)]

        acc_dropdown['values'] = acc_candidates
        speed_dropdown['values'] = speed_candidates
        slope_dropdown['values'] = slope_candidates
        soc_dropdown['values'] = soc_candidates

        if signal_names:
            acc_signal_var.set(signal_names[0])
            speed_signal_var.set(signal_names[0])
            slope_signal_var.set(signal_names[0])
            soc_signal_var.set(signal_names[0])

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {e}")
# v2 speed unit select
# Conversion function
def convert_speed_to_mps(speed_data, unit):
    if unit == "km/h":
        return speed_data * (1000 / 3600)
    elif unit == "mph":
        return speed_data * 0.44704
    return speed_data
#end V2 speed unit selected

#V2 slope unit select
def convert_slope_to_radians(slope_data, unit):
    if unit == "deg":
        return np.radians(slope_data)
    return slope_data  # Already in radians
# end V2 slope unit slect

def compute_altitude_change():
    try:
        if isinstance(mdf, MDF):
            # Handling .mf4 and .dat files
            speed_signal = mdf.get(speed_signal_var.get())
            slope_signal = mdf.get(slope_signal_var.get())

            speed_time = speed_signal.timestamps
            speed_data = speed_signal.samples

            slope_time = slope_signal.timestamps
            slope_data = slope_signal.samples
        else:
            # Handling .mat files
            mat_data = loadmat(file_var.get())
            # Adjust the keys based on your .mat file structure
            speed_data = mat_data[speed_signal_var.get()].flatten()
            slope_data = mat_data[slope_signal_var.get()].flatten()
            # Assuming time data is stored under a specific key, e.g., 'time'
            if 'time' in mat_data:
                speed_time = mat_data['time'].flatten()
                slope_time = mat_data['time'].flatten()
            else:
                # If no time data is available, use indices as time
                speed_time = np.arange(len(speed_data))
                slope_time = np.arange(len(slope_data))

        # Interpolate slope to match speed timestamps
        slope_interp = np.interp(speed_time, slope_time, slope_data)

        # Convert slope angle to radians if needed (assume degrees)
        #slope_radians = np.radians(slope_interp) #removed in V2 use below  slope_unit_var.get
        
        #V2 adjust speed_data unit 
        speed_data = convert_speed_to_mps(speed_data, speed_unit_var.get())
        slope_radians = convert_slope_to_radians(slope_interp, slope_unit_var.get())

        #end V2 adjunst speed_data unit
        # Compute vertical speed
        vertical_speed = speed_data * np.sin(slope_radians)

        # Integrate using trapezoidal rule
        altitude = np.cumsum(np.concatenate([[0], np.diff(speed_time) * vertical_speed[1:]]))

        # Plot altitude profile
        plt.figure(figsize=(10, 5))
        plt.plot(speed_time, altitude, label="Altitude Change")
        plt.title("Altitude Profile Over Time")
        plt.xlabel("Time [s]")
        plt.ylabel("Altitude Change [m]")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to compute altitude change: {e}")

# Function to plot selected signals
def plot_signals():
    try:
        if isinstance(mdf, MDF):
            # Handling .mf4 and .dat files
            acc_signal = mdf.get(acc_signal_var.get())
            speed_signal = mdf.get(speed_signal_var.get())
            slope_signal = mdf.get(slope_signal_var.get())
            soc_signal = mdf.get(soc_signal_var.get())

            acc_time = acc_signal.timestamps
            acc_data = acc_signal.samples

            speed_time = speed_signal.timestamps
            speed_data = speed_signal.samples

            slope_time = slope_signal.timestamps
            slope_data = slope_signal.samples

            soc_time = soc_signal.timestamps
            soc_data = soc_signal.samples
        else:
            # Handling .mat files
            mat_data = loadmat(file_var.get())
            # Adjust the keys based on your .mat file structure
            acc_data = mat_data[acc_signal_var.get()].flatten()
            speed_data = mat_data[speed_signal_var.get()].flatten()
            slope_data = mat_data[slope_signal_var.get()].flatten()
            soc_data = mat_data[soc_signal_var.get()].flatten()
            # Assuming time data is stored under a specific key, e.g., 'time'
            if 'time' in mat_data:
                acc_time = mat_data['time'].flatten()
                speed_time = mat_data['time'].flatten()
                slope_time = mat_data['time'].flatten()
                soc_time = mat_data['time'].flatten()
            else:
                # If no time data is available, use indices as time
                acc_time = np.arange(len(acc_data))
                speed_time = np.arange(len(speed_data))
                slope_time = np.arange(len(slope_data))
                soc_time = np.arange(len(soc_data))
        
# create 4 subplots   
        plt.figure(figsize=(12, 8))

        plt.subplot(4, 1, 1)
        plt.plot(acc_time, acc_data, label="Acceleration")
        plt.title("Acceleration Signal")
        plt.xlabel("Time [s]")
        plt.ylabel("Acceleration")
        plt.grid(True)

        plt.subplot(4, 1, 2)
        plt.plot(speed_time, speed_data, label="Speed", color='orange')
        plt.title("Speed Signal")
        plt.xlabel("Time [s]")
        plt.ylabel("Speed")
        plt.grid(True)

        plt.subplot(4, 1, 3)
        plt.plot(slope_time, slope_data, label="Slope Angle", color='green')
        plt.title("Slope Angle Signal")
        plt.xlabel("Time [s]")
        plt.ylabel("Angle [rad or deg]")
        plt.grid(True)

        plt.subplot(4, 1, 4)
        plt.plot(soc_time, soc_data, label="SOC", color='purple')
        plt.title("SOC Signal")
        plt.xlabel("Time [s]")
        plt.ylabel("State of Charge")
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to plot signals: {e}")
#end plot selected signals

# GUI layout
ttk.Label(root, text="Select .mf4 or .dat or .mat file:").pack(pady=5)
ttk.Button(root, text="Browse", command=load_file).pack(pady=5)
ttk.Label(root, textvariable=file_var, wraplength=400).pack(pady=5)

ttk.Label(root, text="Select Acceleration Signal:").pack(pady=2)
acc_dropdown = ttk.Combobox(root, textvariable=acc_signal_var, width=50)
acc_dropdown.pack(pady=2)

ttk.Label(root, text="Select Speed Signal:").pack(pady=2)
speed_dropdown = ttk.Combobox(root, textvariable=speed_signal_var, width=50)
speed_dropdown.pack(pady=2)

ttk.Label(root, text="Select Speed Unit:").pack(pady=2)
speed_unit_dropdown = ttk.Combobox(root, textvariable=speed_unit_var, values=["m/s", "km/h", "mph"], width=10)
speed_unit_dropdown.pack(pady=2)

ttk.Label(root, text="Select Slope Angle Signal:").pack(pady=2)
slope_dropdown = ttk.Combobox(root, textvariable=slope_signal_var, width=50)
slope_dropdown.pack(pady=2)

ttk.Label(root, text="Select Slope Angle Unit:").pack(pady=2)
slope_unit_dropdown = ttk.Combobox(root, textvariable=slope_unit_var, values=["deg", "rad"], width=10)
slope_unit_dropdown.pack(pady=2)

ttk.Label(root, text="Select SOC Signal:").pack(pady=2)
soc_dropdown = ttk.Combobox(root, textvariable=soc_signal_var, width=50)
soc_dropdown.pack(pady=2)

ttk.Button(root, text="Plot Signals", command=plot_signals).pack(pady=5)
ttk.Button(root, text="Compute Altitude Change", command=compute_altitude_change).pack(pady=10)

root.mainloop()
