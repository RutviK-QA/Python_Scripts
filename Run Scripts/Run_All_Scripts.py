import os
import subprocess
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils
utils.load_env_files()

# Root directory where all the folders are located
root_dir = r'C:\Users\RutviK\Python PlaywrightScripts'

# List of folders to process
folders_to_process = ['Auth', 'Contacts', 'General', 'Overview', 'Policies']

# Function to run all .py scripts in a given folder
def run_scripts_in_folder(folder_path):
    # Iterate through each file in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a .py file
        if filename.endswith('.py'):
            file_path = os.path.join(folder_path, filename)
            print(f"Running script: {file_path}")
            # Set the current working directory to the folder containing the script
            os.chdir(folder_path)
            # Run the script using subprocess
            result = subprocess.run(['python', file_path], cwd=folder_path)
            # Check if the script ran successfully
            if result.returncode != 0:
                print(f"Script {filename} failed with return code {result.returncode}")
            else:
                print(f"Script {filename} ran successfully")

# Iterate through each folder and run scripts
for folder_name in folders_to_process:
    folder_path = os.path.join(root_dir, folder_name)
    if os.path.isdir(folder_path):
        print(f"Executing scripts in folder: {folder_name}")
        run_scripts_in_folder(folder_path)
        print(f"Execution of scripts in folder {folder_name} completed.\n")

print("All scripts executed successfully.")
