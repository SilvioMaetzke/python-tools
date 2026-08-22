# DBC_compare based on DBC reader V14 clean up GUI window
# V3 merge DBC Reader and DBC compare V2 in one big script
# V4 more complex add also from DBC reader the selecting of controller  and their communication asn json file and txt files
# V5 correct Controller plot figure issue
# V6 expand compare function
# V7 optimize compare pared to get save txt files
# V8 also add signal.comment in json files 
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

# Global variables to store the loaded DBC databases
db1 = None
db2 = None
controllers1 = []
controllers2 = []

# Initialize the variables as empty strings
controllers_all1 = ""
controllers_all2 = ""
messages_all1 = ""
messages_all2 = ""
signals_all1 = ""
signals_all2 = ""

# Function to load DBC file
def load_file1():
    global db1, controllers1
    file_path = filedialog.askopenfilename(filetypes=[("DBC files", "*.dbc")])
    file_var1.set(file_path)
    print(f"Loaded file 1: {file_path}")

    # Load the DBC file
    db1 = cantools.database.load_file(file_path)

    # Extract controllers from the BU_ line
    controllers1 = extract_controllers(file_path)

    # Update the controller selection dropdowns
    controller_combobox1_1['values'] = controllers1
    controller_combobox1_2['values'] = controllers1

def load_file2():
    global db2, controllers2
    file_path = filedialog.askopenfilename(filetypes=[("DBC files", "*.dbc")])
    file_var2.set(file_path)
    print(f"Loaded file 2: {file_path}")

    # Load the DBC file
    db2 = cantools.database.load_file(file_path)

    # Extract controllers from the BU_ line
    controllers2 = extract_controllers(file_path)

    # Update the controller selection dropdowns
    controller_combobox2_1['values'] = controllers2
    controller_combobox2_2['values'] = controllers2

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
def print_and_save_message_details(db, file_var, controllers):
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

    # Extract all signals from DBC
    signals_list = [signal.name for message in db.messages for signal in message.signals]

    # Convert lists to strings for saving to text files
    controllers_all = "\n".join(controllers)
    messages_all = "\n".join(messages_list)
    signals_all = "\n".join(signals_list)

    # Save controller to txt and all message to 2nd txt and all signals to 3rd txt
    save_to_txt(controllers_all, file_path, suffix='_controllers')
    save_to_txt(messages_all, file_path, suffix='_messages')
    save_to_txt(signals_all, file_path, suffix='_signals')

# Function to print and save message details for selected controllers
def print_and_save_selected_message_details(db, file_var, controllers):
    if db is None:
        print("No DBC file loaded.")
        return

    selected_controllers = [controller_var1_1.get(), controller_var1_2.get()]
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
def plot_block_diagram(db, file_var):
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

# Function to compare DBC files
def compare_dbc_files():
    if db1 is None or db2 is None:
        print("Both DBC files must be loaded for comparison.")
        return

    # Implement comparison logic here
    # Compare controllers
    missing_controllers1 = set(controllers2) - set(controllers1)
    missing_controllers2 = set(controllers1) - set(controllers2)

    # Example: Compare messages between db1 and db2
    messages1 = {message.name for message in db1.messages}
    messages2 = {message.name for message in db2.messages}

    common_messages = messages1.intersection(messages2)
    unique_messages1 = messages1 - messages2
    unique_messages2 = messages2 - messages1

    missing_messages1 = messages2 - messages1
    missing_messages2 = messages1 - messages2

    # Compare message details (signals)
    signals1 = {signal.name for message in db1.messages for signal in message.signals}
    signals2 = {signal.name for message in db2.messages for signal in message.signals}
    missing_signals1 = signals2 - signals1
    missing_signals2 = signals1 - signals2

    print("Common Messages:", common_messages)
    print("Unique Messages in File 1:", unique_messages1)
    print("Unique Messages in File 2:", unique_messages2)

    # Save detailed lists to text files
    file_path1 = file_var1.get()
    file_path2 = file_var2.get()
    save_to_txt("\n".join(missing_controllers1), file_path1, suffix='_missing_controllers1')
    save_to_txt("\n".join(missing_controllers2), file_path2, suffix='_missing_controllers2')
    save_to_txt("\n".join(missing_messages1), file_path1, suffix='_missing_messages1')
    save_to_txt("\n".join(missing_messages2), file_path2, suffix='_missing_messages2')
    save_to_txt("\n".join(missing_signals1), file_path1, suffix='_missing_signals1')
    save_to_txt("\n".join(missing_signals2), file_path2, suffix='_missing_signals2')

    # Display results
    result_text.set(f"Missing Controllers in File 1: {len(missing_controllers1)}\n"
                    f"Missing Controllers in File 2: {len(missing_controllers2)}\n"
                    f"Missing Messages in File 1: {len(missing_messages1)}\n"
                    f"Missing Messages in File 2: {len(missing_messages2)}\n"
                    f"Missing Signals in File 1: {len(missing_signals1)}\n"
                    f"Missing Signals in File 2: {len(missing_signals2)}")

# Set up the GUI
root = tk.Tk()
root.title("Reader&Compare of 2 DBC Files")

# Create a label with multi-line text
label = tk.Label(root, text="DBC File analysis and compare V8\n save json files for controller and messages.details (signals)  \n additionally also txt files for validation\n compare 2 dbc and save for each the delta to other dbc\ncreated by Silvio Maetzke", font=("Arial", 8))
label.pack(pady=20)

frame = ttk.Frame(root)
frame.pack(pady=10)

# File 1 Section
file_var1 = tk.StringVar()
file_frame1 = ttk.LabelFrame(frame, text="DBC File 1")
file_frame1.grid(row=0, column=0, padx=10, pady=10)

ttk.Label(file_frame1, text="Select DBC file 1:").pack(pady=5)
ttk.Button(file_frame1, text="Browse", command=load_file1).pack(pady=5)
ttk.Label(file_frame1, textvariable=file_var1, wraplength=400).pack(pady=5)

ttk.Button(file_frame1, text="Plot Controller Diagram", command=lambda: plot_block_diagram(db1, file_var1)).pack(pady=5)
ttk.Button(file_frame1, text="Print and Save Message Details", command=lambda: print_and_save_message_details(db1, file_var1, controllers1)).pack(pady=5)

# Controller selection for File 1
controller_var1_1 = tk.StringVar()
controller_var1_2 = tk.StringVar()
ttk.Label(file_frame1, text="Select Controller 1:").pack(pady=5)
controller_combobox1_1 = ttk.Combobox(file_frame1, textvariable=controller_var1_1)
controller_combobox1_1.pack(pady=5)
ttk.Label(file_frame1, text="Select Controller 2:").pack(pady=5)
controller_combobox1_2 = ttk.Combobox(file_frame1, textvariable=controller_var1_2)
controller_combobox1_2.pack(pady=5)

ttk.Button(file_frame1, text="Save Selected Message Details", command=lambda: print_and_save_selected_message_details(db1, file_var1, controllers1)).pack(pady=5)

# File 2 Section
file_var2 = tk.StringVar()
file_frame2 = ttk.LabelFrame(frame, text="DBC File 2")
file_frame2.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(file_frame2, text="Select DBC file 2:").pack(pady=5)
ttk.Button(file_frame2, text="Browse", command=load_file2).pack(pady=5)
ttk.Label(file_frame2, textvariable=file_var2, wraplength=400).pack(pady=5)

ttk.Button(file_frame2, text="Plot Controller Diagram", command=lambda: plot_block_diagram(db2, file_var2)).pack(pady=5)
ttk.Button(file_frame2, text="Print and Save Message Details", command=lambda: print_and_save_message_details(db2, file_var2, controllers2)).pack(pady=5)

# Controller selection for File 2
controller_var2_1 = tk.StringVar()
controller_var2_2 = tk.StringVar()
ttk.Label(file_frame2, text="Select Controller 1:").pack(pady=5)
controller_combobox2_1 = ttk.Combobox(file_frame2, textvariable=controller_var2_1)
controller_combobox2_1.pack(pady=5)
ttk.Label(file_frame2, text="Select Controller 2:").pack(pady=5)
controller_combobox2_2 = ttk.Combobox(file_frame2, textvariable=controller_var2_2)
controller_combobox2_2.pack(pady=5)

ttk.Button(file_frame2, text="Save Selected Message Details", command=lambda: print_and_save_selected_message_details(db2, file_var2, controllers2)).pack(pady=5)

# Compare Section
#ttk.Button(root, text="Compare DBC Files", command=compare_dbc_files).pack(pady=20)
#V6 change to show in GUI also compare info like missing controller
#++++++V6+++
# Section for comparison results
frame3 = ttk.Frame(root)
frame3.pack(side=tk.LEFT, padx=20, pady=20)

result_text = tk.StringVar()
ttk.Button(frame3, text="Compare DBC Files", command=compare_dbc_files).pack(pady=20)
ttk.Label(frame3, textvariable=result_text, wraplength=400).pack(pady=20)

#------V6---

root.mainloop()