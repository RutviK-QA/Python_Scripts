import os
import subprocess

root_dir = 'c:\Users\RutviK\Python PlaywrightScripts'

# Iterate through each folders in playwright scripts 
for folder_name in ['Auth', 'Contacts', 'General', 'Overview', 'Policies']:
    folder_path = os.path.join(root_dir, folder_name)

    if os.path.isdir(folder_path):
        print(f"Executing scripts in {folder_name}...")

        # Iterate through Python files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if the file is a .py file
            if filename.endswith('.py'):
                print(f"Running script: {filename}")
                subprocess.run(['python', file_path], cwd=folder_path)

        print(f"Execution of scripts in {folder_name} completed.\n")

print("All scripts executed successfully.")
