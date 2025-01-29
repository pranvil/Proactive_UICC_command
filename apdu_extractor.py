import tkinter as tk
from tkinter import filedialog
import re

def extract_apdu_messages(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    extracted_messages = []
    current_message = []
    extracting = False
    termination_condition = None

    for line in lines:
        stripped_line = line.strip()
        if "APDU_tx 0: 80" in stripped_line:
            extracting = True
            termination_condition = "APDU_rx:len"
            current_message.append(''.join(stripped_line.split()[2:]))
        elif "U_rx 0: D0" in stripped_line:
            extracting = True
            termination_condition = "APDU_rx 0:"
            current_message.append(''.join(stripped_line.split()[2:]))
        elif extracting and termination_condition in stripped_line:
            extracting = False
            extracted_messages.append("".join(current_message))
            current_message = []
        elif extracting:
            # Use regex to remove prefixes like "APDU_rx X:" and "APDU_tx X:" where X can be one or more digits
            cleaned_line = re.sub(r'APDU_[rt]x \d+:', '', stripped_line).replace(" ", "")
            current_message.append(cleaned_line)

    return extracted_messages

def select_file_and_extract():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select MTK raw APDU data file", filetypes=[("Text files", "*.txt")])
    
    if file_path:
        messages = extract_apdu_messages(file_path)
        if messages:
            with open("extracted_messages.txt", "w") as output_file:
                for message in messages:
                    output_file.write(f"{message}\n")
            print("Messages saved to extracted_messages.txt")
        else:
            print("No messages extracted.")
    else:
        print("No file selected.") 