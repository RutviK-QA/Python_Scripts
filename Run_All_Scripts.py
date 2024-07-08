import os
import subprocess

# Define the root directory where Folder 1 is located
root_dir = 'c:\Users\RutviK\Python PlaywrightScripts'

# Iterate through each folder (Folder 2, 3, 4)
for folder_name in ['Auth', 'Contacts', 'General', 'Overview', 'Policies']:
    folder_path = os.path.join(root_dir, folder_name)

    # Check if the path is a directory
    if os.path.isdir(folder_path):
        print(f"Executing scripts in {folder_name}...")

        # Iterate through Python files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if the file is a Python script (.py)
            if filename.endswith('.py'):
                print(f"Running script: {filename}")
                subprocess.run(['python', file_path], cwd=folder_path)

                # Optionally, wait or perform cleanup between script runs
                # time.sleep(1)  # Example: Wait for 1 second between scripts

        print(f"Execution of scripts in {folder_name} completed.\n")

print("All scripts executed successfully.")
