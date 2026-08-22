# GPX_analysisGui created by Silvio Maetzke IAV Inc.
# V1 browse for Gpx file and create 3 plots
# V2 browse button with GUI
# V3 progress bar in case takes time for laptop to load
# V4 adjusted GUI window size
# V5 title and description for each plot
# V6 read comments from header of GPX file and show them in GUI window
# V7 addded callback to make sure Gpx comments are getting displayed 
# V7 seems issue need new version, issue descripton: "The issue with the distance plot showing only 4 km despite a 9-hour trip could be due to the way distances are calculated in your script. The current implementation uses Euclidean distance, which may not be accurate for geographical coordinates. This can lead to incorrect distance calculations, especially over longer distances.
#To resolve this, consider using the Haversine formula or a similar method that accounts for the curvature of the Earth"
#V8 bugfix dstance caclulation 
import gpxpy
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from tkinter import Tk, StringVar
from tkinter import ttk
from tkinter.filedialog import askopenfilename
#V8 update distance
from math import radians, sin, cos, sqrt, atan2

# V6 Function to read comments from GPX file
def read_gpx_comments(file_path):
    comments = {}
    try:
        with open(file_path, 'r') as gpx_file:
            for line in gpx_file:
                if line.strip().startswith("<!--"):
                    # Extract key-value pairs from comments
                    parts = line.strip().replace("<!--", "").replace("-->", "").split("=")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        comments[key] = value
        print("Comments read:", comments)  # Debugging line
    except Exception as e:
        print(f"Error reading comments: {e}")
    return comments

# Function to parse GPX file and extract data
def parse_gpx_file(file_path):
    latitudes = []
    longitudes = []
    elevations = []
    times = []
    speeds = []

    try:
        with open(file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        total_points = sum(len(segment.points) for track in gpx.tracks for segment in track.segments)
        processed_points = 0

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    latitudes.append(point.latitude)
                    longitudes.append(point.longitude)
                    elevations.append(point.elevation)
                    if point.time:
                        times.append(point.time)
                    else:
                        times.append(datetime.min)  # Use a default time if None
                    speeds.append(point.speed if point.speed is not None else 0)

                    # Update progress bar
                    processed_points += 1
                    progress_bar['value'] = (processed_points / total_points) * 100
                    root.update_idletasks()
    except Exception as e:
        print(f"Error parsing GPX file: {e}")

    return latitudes, longitudes, elevations, times, speeds

# Function to calculate distance between points replace with V8 
#def calculate_distances(latitudes, longitudes):
 #   distances = [0]
   # for i in range(1, len(latitudes)):
        # Calculate distance using Haversine formula or similar
        # For simplicity, using Euclidean distance here
     #   dist = np.sqrt((latitudes[i] - latitudes[i-1])**2 + (longitudes[i] - longitudes[i-1])**2)
    #    distances.append(distances[-1] + dist)
   # return distances
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def calculate_distances(latitudes, longitudes):
    distances = [0]
    for i in range(1, len(latitudes)):
        dist = haversine(latitudes[i-1], longitudes[i-1], latitudes[i], longitudes[i])
        distances.append(distances[-1] + dist)
    return distances

#end V8 distance with Haversine formula

# Function to plot data
def plot_data(latitudes, longitudes, elevations, times, speeds):
    distances = calculate_distances(latitudes, longitudes)

    # Convert times to elapsed time in seconds
    start_time = times[0]
    elapsed_times = [(t - start_time).total_seconds() for t in times]

    # Plot 1: Map with start and end points
    plt.figure(figsize=(10, 6))
    plt.scatter(longitudes, latitudes, c='blue', label='Track Points')
    plt.scatter(longitudes[0], latitudes[0], c='green', label='Start', marker='o')
    plt.scatter(longitudes[-1], latitudes[-1], c='red', label='End', marker='x')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Track Map')
    plt.legend()
    plt.grid()

    # Plot 2: Altitude over time and distance
    fig, axs = plt.subplots(2, figsize=(10, 8))
    axs[0].plot(elapsed_times, elevations, label='Altitude over Time')
    axs[0].set_xlabel('Elapsed Time (s)')
    axs[0].set_ylabel('Altitude (m)')
    axs[0].set_title('Altitude change over time and over distance')
    axs[0].grid()

    axs[1].plot(distances, elevations, label='Altitude over Distance')
    axs[1].set_xlabel('Distance (km)')
    axs[1].set_ylabel('Altitude (m)')
    axs[1].grid()

    # Plot 3: Speed over time and distance
    fig, axs = plt.subplots(2, figsize=(10, 8))
    axs[0].plot(elapsed_times, speeds, label='Speed over Time')
    axs[0].set_xlabel('Elapsed Time (s)')
    axs[0].set_ylabel('Speed (m/s)')
    axs[0].set_title('Speed change over time and over distance')
    axs[0].grid()

    axs[1].plot(distances, speeds, label='Speed over Distance')
    axs[1].set_xlabel('Distance (km)')
    axs[1].set_ylabel('Speed (m/s)')
    axs[1].grid()

    plt.show()

# Function to load file and update GUI
def load_file():
    file_path = askopenfilename(filetypes=[("GPX files", "*.gpx")])
    file_var.set(file_path)
    if file_path:
        progress_bar['value'] = 0
        root.update_idletasks()  # Update the GUI to show progress
        comments = read_gpx_comments(file_path)
        latitudes, longitudes, elevations, times, speeds = parse_gpx_file(file_path)
        
        # Update the statistics label with comments before plotting
        comment_text = "\n".join([f"{key}: {value}" for key, value in comments.items()])
        stats_label.config(text=comment_text)
        root.update_idletasks()  # Ensure GUI updates
        
        plot_data(latitudes, longitudes, elevations, times, speeds)
        progress_bar['value'] = 100  # Fill the progress bar completely

# Main function to create GUI
def main():
    global file_var, progress_bar, root, stats_label
    root = Tk()
    root.title("Analysis GPX Data")

    # Set the initial size of the window (width x height)
    root.geometry("500x500")  # Adjust the width and height as needed

    file_var = StringVar()

    # Create a label with multi-line text
    label = ttk.Label(root, text="Analysis GPX Data V7\nby Silvio Maetzke IAV Inc.", font=("Arial", 8))
    label.pack(pady=20)

    # GUI layout
    ttk.Label(root, text="Select .GPX file:").pack(pady=5)
    ttk.Button(root, text="Browse", command=load_file).pack(pady=5)
    ttk.Label(root, textvariable=file_var, wraplength=400).pack(pady=5)

    # Progress bar
    progress_bar = ttk.Progressbar(root, mode='determinate', maximum=100)
    progress_bar.pack(pady=5, fill='x')

    # Statistics label
    stats_label = ttk.Label(root, text="", font=("Arial", 8), wraplength=400)
    stats_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()