# DBC_reader
# created by SIlvio Maetzke IAV automotive Engineering Inc.
# idea to read in DBC files and create block s as overview of involved controller
#V2 read  DBC file with help of cantools import
#v3 granulgather used controller names 
#V4 try info message and nodsignals with node
#V5 from V4 printed overvieww create a big json file
# V6 select controller and visualize signals between
#V7 select 2 controller but only show the messages V6 was to much signals in visualization
#V8 save 3 json files controller meassage, and message detail with signals
#V9 working better figures and plots
#V10 fix executable be able to plot figures 
#V11 4th json file for the message detail between selected 2 controllers
# To achieve the creation of four JSON files, including the detailed message information for all controllers and a separate file for the selected controllers, we can adjust the code as follows:
# Controllers JSON: Contains the list of controllers extracted from the DBC file.
# Messages JSON: Contains the list of message names from the DBC file.
# Message Details JSON: Contains detailed information about all messages and signals.
# Selected Controllers Message Details JSON: Contains detailed information about messages and signals for the selected controllers.
#V12 add save in txt file information of selected controller 
#V13 add also save as text for all controller information one txt for controler 2nd for messages 3 all signals
# V14 clean up GUI window
# V15 added in json file  DBC signal.comment to have all commetn for the signals available 
import matplotlib
matplotlib.use('TkAgg')  # Set the backend to TkAgg for interactive plotting

import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
import json
import os
import cantools

# Clear Console Output
os.system('cls')
# Clear previous plots
plt.clf()  # Clear the current figure
plt.cla()  # Clear the current axes
plt.close()  # Close the current figure

# Global variable to store the loaded DBC database
db = None
controllers = []

# Initialize the variables as empty strings
controllers_all = ""
messages_all = ""
signals_all = ""

# Function to load DBC file
def load_file():
    global db, controllers
    file_path = filedialog.askopenfilename(filetypes=[("DBC files", "*.dbc")])
    file_var.set(file_path)
    print(f"Loaded file: {file_path}")

    # Load the DBC file
    db = cantools.database.load_file(file_path)

    # Extract controllers from the BU_ line
    controllers = extract_controllers(file_path)

    # Update the controller selection dropdowns
    controller_combobox1['values'] = controllers
    controller_combobox2['values'] = controllers

# Function to save data to JSON
def save_to_json(data, file_path, suffix=''):
    json_file_path = os.path.splitext(file_path)[0] + suffix + '.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {json_file_path}")

# Function to save data to a text file
def save_to_txt(data, file_path, suffix=''):
    txt_file_path = os.path.splitext(file_path)[0] + suffix + '.txt'
    with open(txt_file_path, 'w') as txt_file:
        txt_file.write(data)
    print(f"Data saved to {txt_file_path}")

# Function to extract controllers from the BU_ line
def extract_controllers(file_path):
    controllers = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('BU_'):
                controllers = line.split()[1:]  # Skip 'BU_' and get controller names
                break
    return controllers

# Function to print and save message and signal details
def print_and_save_message_details():
    if db is None:
        print("No DBC file loaded.")
        return

    print("Checking messages in the DBC file...")
    if not db.messages:
        print("No messages found in the DBC file.")
        return

    message_details = []
    print("Printing message details:")
    for message in db.messages:
        print(f"Message ID: {message.frame_id}, Name: {message.name}, Length: {message.length}, Sender: {message.senders}")
        
        message_info = {
            "Message ID": message.frame_id,
            "Name": message.name,
            "Length": message.length,
            "Sender": message.senders,
            "Signals": []
        }

        # Iterate over signals within the message
        for signal in message.signals:
            print(f"  Signal Name: {signal.name}, Comment:{signal.comment}, Start Bit: {signal.start}, Length: {signal.length}, Receivers: {signal.receivers}")
            
            signal_info = {
                "Signal Name": signal.name,
                "Comment": signal.comment,
                "Start Bit": signal.start,
                "Length": signal.length,
                "Receivers": signal.receivers
            }
            message_info["Signals"].append(signal_info)

        message_details.append(message_info)

    # Save message details to JSON
    file_path = file_var.get()
    save_to_json({"Message Details": message_details}, file_path, suffix='_message_details')
    # Save controllers to JSON
    save_to_json({'controllers': controllers}, file_path, suffix='_controllers')
    
    # Extract messages from the DBC file
    messages_list = [message.name for message in db.messages]

    # Save messages to JSON
    save_to_json({'messages': messages_list}, file_path, suffix='_messages')

    #V13 extract all signals from DBC
    signals_list = [signal.name for message in db.messages for signal in message.signals]

    # Convert lists to strings for saving to text files
    controllers_all = "\n".join(controllers)
    messages_all = "\n".join(messages_list)
    signals_all = "\n".join(signals_list)

    #V13 save controller to txt and all message to 2nd txt and all signals to 3rd txt
    save_to_txt(controllers_all, file_path, suffix='_controllers')
    save_to_txt(messages_all, file_path, suffix='_messages')
    save_to_txt(signals_all, file_path, suffix='_signals')

# Function to print and save message details for selected controllers
def print_and_save_selected_message_details():
    if db is None:
        print("No DBC file loaded.")
        return

    selected_controllers = [controller_var1.get(), controller_var2.get()]
    if not all(selected_controllers):
        print("Please select two controllers.")
        return

    message_details = []
    messages_txt = ""
    signals_txt = ""
    print("Printing message details for selected controllers:")
    for message in db.messages:
        if any(sender in selected_controllers for sender in message.senders):
            message_info = {
                "Message ID": message.frame_id,
                "Name": message.name,
                "Length": message.length,
                "Sender": message.senders,
                "Signals": []
            }
            messages_txt += f"Message ID: {message.frame_id}, Name: {message.name}, Length: {message.length}, Sender: {message.senders}\n"

            # Iterate over signals within the message
            for signal in message.signals:
                if any(receiver in selected_controllers for receiver in signal.receivers):
                    signal_info = {
                        "Signal Name": signal.name,
                        "Comment": signal.comment,
                        "Start Bit": signal.start,
                        "Length": signal.length,
                        "Receivers": signal.receivers
                    }
                    message_info["Signals"].append(signal_info)
                    signals_txt += f"Signal Name: {signal.name},Comment:{signal.comment}, Start Bit: {signal.start}, Length: {signal.length}, Receivers: {signal.receivers}\n"

            message_details.append(message_info)

    # Save detailed message information to JSON for selected controllers
    file_path = file_var.get()
    save_to_json({'Selected Message Details': message_details}, file_path, suffix='_selected_message_details')

    # Save messages and signals to text files
    save_to_txt(messages_txt, file_path, suffix='_selected_messages')
    save_to_txt(signals_txt, file_path, suffix='_selected_signals')

# Function to plot block diagram
def plot_block_diagram():
    if db is None:
        print("No DBC file loaded.")
        return

    file_path = file_var.get()
    if not file_path:
        print("No file selected.")
        return

    # Extract controllers from the BU_ line
    controllers = extract_controllers(file_path)

    # Plotting logic
    fig, ax = plt.subplots()
    ax.set_title('Controller overview')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(controllers) * 8)

    # Plot blocks for each controller
    for i, controller in enumerate(controllers):
        ax.text(1, i * 7 + 5, controller, fontsize=9, bbox=dict(facecolor='cyan', alpha=0.5, pad=2))

    plt.show()

# Function to visualize messages between selected controllers
def visualize_messages():
    if db is None:
        print("No DBC file loaded.")
        return

    selected_controllers = [controller_var1.get(), controller_var2.get()]
    if not all(selected_controllers):
        print("Please select two controllers.")
        return

    # Filter messages involving the selected controllers
    relevant_messages = []
    for message in db.messages:
        if any(sender in selected_controllers for sender in message.senders):
            relevant_messages.append(message)

    # Plotting logic
    fig, ax = plt.subplots()
    ax.set_title(f'Messages between {selected_controllers[0]} and {selected_controllers[1]}')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(relevant_messages) * 9)

    # Plot messages for each relevant message
    for i, message in enumerate(relevant_messages):
        ax.text(1, i * 8 + 5, f'{message.name}', fontsize=8, bbox=dict(facecolor='cyan', alpha=0.5, pad=2))

    plt.show()

# Function to plot signals for selected controllers
def plot_signals():
    if db is None:
        print("No DBC file loaded.")
        return

    selected_controllers = [controller_var1.get(), controller_var2.get()]
    if not all(selected_controllers):
        print("Please select two controllers.")
        return

    # Filter signals involving the selected controllers
    relevant_signals = []
    for message in db.messages:
        for signal in message.signals:
            if any(receiver in selected_controllers for receiver in signal.receivers):
                relevant_signals.append(signal)

    # Plotting logic
    fig, ax = plt.subplots()
    ax.set_title(f'Signals for {selected_controllers[0]} and {selected_controllers[1]}')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(relevant_signals) * 9)

    # Plot signals for each relevant signal
    for i, signal in enumerate(relevant_signals):
        ax.text(1, i * 8 + 5, f'{signal.name}', fontsize=8, bbox=dict(facecolor='cyan', alpha=0.5, pad=2))

    plt.show()

# Set up the GUI
root = tk.Tk()
root.title("DBC File Reader and Block Diagram Plotter")

# Create a label with multi-line text
label = tk.Label(root, text="DBC File analysis V15\n save json files for controller and messages.details (signals)  \n additionally also txt files for validation\ncreated by Silvio Maetzke", font=("Arial", 8))
label.pack(pady=20)

file_var = tk.StringVar()
ttk.Label(root, text="Select DBC file:").pack(pady=5)
ttk.Button(root, text="Browse", command=load_file).pack(pady=5)
ttk.Label(root, textvariable=file_var, wraplength=400).pack(pady=5)

ttk.Button(root, text="Plot Controller Diagram", command=plot_block_diagram).pack(pady=20)
ttk.Button(root, text="Print and Save Message Details", command=print_and_save_message_details).pack(pady=20)

# Controller selection
controller_var1 = tk.StringVar()
controller_var2 = tk.StringVar()
ttk.Label(root, text="Select Controller 1:").pack(pady=5)
controller_combobox1 = ttk.Combobox(root, textvariable=controller_var1)
controller_combobox1.pack(pady=5)
ttk.Label(root, text="Select Controller 2:").pack(pady=5)
controller_combobox2 = ttk.Combobox(root, textvariable=controller_var2)
controller_combobox2.pack(pady=5)

ttk.Button(root, text="Visualize Messages", command=visualize_messages).pack(pady=20)
ttk.Button(root, text="Plot Signals", command=plot_signals).pack(pady=20)
ttk.Button(root, text="Save Selected Message Details", command=print_and_save_selected_message_details).pack(pady=20)

root.mainloop()