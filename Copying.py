import tkinter as tk
from tkinter import filedialog
import os
import shutil
from tkinter import messagebox
import threading
import tkinter.ttk as ttk
import subprocess
import ctypes

# Create the main window
root = tk.Tk()
root.title("File Copy Utility")

# Set the window size
window_width = 800
window_height = 300
root.geometry(f"{window_width}x{window_height}")

# Configure the background color
root.configure(bg="black")

# Global variables to store the list of folders and programs, copied file paths, and program launch commands
folder_program_list = []
copied_files = []
program_list = [
    ("explorer.exe", "Explorer"),
    ("cmd.exe", "Command Prompt")
]

# Function to select folders and programs
def select_folders_programs():
    global folder_program_list

    # Open a file dialog to select folders and programs
    selected_files = filedialog.askopenfilenames(initialdir="/", title="Select Folders/Programs",
                                                 filetypes=(("All Files", "*.*"), ("Folders", "*/")))
    for file_path in selected_files:
        if os.path.isdir(file_path):
            folder_program_list.append((file_path, "Folder"))
            list_box.insert(tk.END, f"{file_path} (Folder)")
        else:
            folder_program_list.append((file_path, "Program"))
            list_box.insert(tk.END, f"{file_path} (Program)")

# Function to clear the list of selected folders and programs
def clear_list():
    global folder_program_list
    folder_program_list = []
    list_box.delete(0, tk.END)

# Function to copy folders and programs to another directory
def copy_to_directory():
    if not folder_program_list:
        messagebox.showinfo("Error", "No folders or programs selected!")
        return

    destination_directory = filedialog.askdirectory()

    def copy_files():
        global copied_files

        progress_bar['maximum'] = len(folder_program_list)
        progress_bar['value'] = 0

        for item in folder_program_list:
            source_path, item_type = item
            if item_type == "Folder":
                destination_path = os.path.join(destination_directory, os.path.basename(source_path))
                shutil.copytree(source_path, destination_path)
                copied_files.append(destination_path)
            else:
                shutil.copy(source_path, destination_directory)
                copied_files.append(os.path.join(destination_directory, os.path.basename(source_path)))
            progress_bar['value'] += 1

        messagebox.showinfo("Success", "Files copied successfully!")
        progress_bar['value'] = 0

        # Clear the list after copying is completed
        root.after(1000, clear_list)

    thread = threading.Thread(target=copy_files)
    thread.start()

# Function to undo the copied files
def undo_copy():
    global copied_files
    if not copied_files:
        messagebox.showinfo("Error", "No files to undo!")
        return

    for file_path in copied_files:
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)

    messagebox.showinfo("Success", "Files successfully undone!")
    copied_files = []

# Function to launch the selected program
def launch_program(program_path):
    try:
        subprocess.Popen([program_path])
    except OSError as e:
        if getattr(e, 'winerror', None) == 740:
            answer = messagebox.askquestion("Error", "Permission elevation required to start the program. Do you want to relaunch with admin privileges?")
            if answer == "yes":
                relaunch_program_with_admin_privileges(program_path)
        else:
            messagebox.showinfo("Error", f"Error launching program: {e}")

# Function to relaunch the program with administrative privileges using the UAC prompt
def relaunch_program_with_admin_privileges(program_path):
    # Create a temporary script to run the program with administrative privileges
    temp_script = os.path.join(os.environ['TEMP'], 'run_as_admin.py')
    with open(temp_script, 'w') as f:
        f.write(f'import subprocess\nsubprocess.Popen(["{program_path}"])')

    # Prompt the UAC dialog to run the temporary script with administrative privileges
    ctypes.windll.shell32.ShellExecuteW(None, "runas", 'python', temp_script, None, 1)

    # Delete the temporary script
    os.remove(temp_script)

# Function to add a program to the program list
def add_program():
    program_path = filedialog.askopenfilename(initialdir="/", title="Select Program",
                                              filetypes=(("Executable Files", "*.exe"), ("All Files", "*.*")))
    if program_path:
        program_name = os.path.basename(program_path)
        program_list.append((program_path, program_name))
        programs_box.insert(tk.END, program_name)

# Create the frame to hold buttons and progress indication
frame = tk.Frame(root, bg="black")
frame.pack(side=tk.LEFT, fill=tk.Y)

# Create the buttons
select_button = tk.Button(frame, text="Select Folders/Programs", bg="black", fg="white", command=select_folders_programs)
select_button.pack(side=tk.TOP, pady=10)

clear_button = tk.Button(frame, text="Clear List", bg="black", fg="white", command=clear_list)
clear_button.pack(side=tk.TOP, pady=10)

copy_button = tk.Button(frame, text="Copy to Directory", bg="black", fg="white", command=copy_to_directory)
copy_button.pack(side=tk.TOP, pady=10)

undo_button = tk.Button(frame, text="Undo Copy", bg="black", fg="white", command=undo_copy)
undo_button.pack(side=tk.TOP, pady=10)

add_program_button = tk.Button(frame, text="Add Program", bg="black", fg="white", command=add_program)
add_program_button.pack(side=tk.TOP, pady=10)

# Create the progress bar
progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
progress_bar.pack(side=tk.TOP, pady=10)

# Create the list box to display the selected folders and programs
list_box = tk.Listbox(root, bg="black", fg="white", width=70, height=15)
list_box.pack(side=tk.LEFT, padx=10, pady=10)

# Create the programs list box
programs_box = tk.Listbox(root, bg="black", fg="white", width=30, height=15)
programs_box.pack(side=tk.RIGHT, padx=10, pady=10)

# Insert the programs into the programs list box
for program in program_list:
    program_name = program[1]
    programs_box.insert(tk.END, program_name)

# Bind double-click event to launch the selected program
programs_box.bind("<Double-Button-1>", lambda event: launch_program(program_list[programs_box.curselection()[0]][0]))

# Bind right-click event to remove the selected program from the list
programs_box.bind("<Button-3>", lambda event: remove_program(programs_box.nearest(event.y)))

# Function to remove a program from the list
def remove_program(index):
    if index >= 0:
        program_name = program_list[index][1]
        program_list.pop(index)
        programs_box.delete(index)
        messagebox.showinfo("Success", f"Program '{program_name}' has been removed from the list.")

# Start the main event loop
root.mainloop()
