import logging
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv(dotenv_path='variables/Variables.env')
load_dotenv(dotenv_path='variables/API.env')

password = os.getenv('PASS')
url = os.getenv('URL')
username = os.getenv('USER')

# Ensure directory exists
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Check if the login state file is recent
def is_recent_state(path, hours=8):
    if not os.path.exists(path):
        return False
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.now() - file_mod_time < timedelta(hours=hours)

# Function to login and save the storage state
def login_and_save_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)

        # TEMPORARY
        # username= "rutvikh5kk@rutvikqa.testinator.com"
        
        # Perform login actions
        page.get_by_placeholder("Enter Email").fill(username)
        page.get_by_placeholder("Password").fill(password)
        page.get_by_placeholder("Password").press("Enter")



        # Wait for login to complete
        page.wait_for_timeout(6000)
        
        try:
            assert not page.get_by_role("alert").is_visible(timeout=10000)
        except:
            print("Login script failure due to login credentials")
            
        # Ensure the directory exists
        ensure_directory_exists('variables/playwright/.auth')
        
        # Save storage state (cookies, local storage) to a file
        context.storage_state(path="variables/playwright/.auth/state.json")
        browser.close()

# Main execution block
if __name__ == '__main__':
    state_path = 'variables/playwright/.auth/state.json'
    
    # Step 1: Check if the state is recent
    if not is_recent_state(state_path):
        # Step 2: Login and save the state if it's not recent
        login_and_save_state()
        logging.info("Created a new login session")
    else:
        logging.info("Logging in using existing session.")

# def check_login_state():
#     # Define the path to the login script and the state file
#     script_path = os.path.join(os.path.dirname(__file__), '../Variables/Login session script.py')
#     state_path = os.path.join(os.path.dirname(__file__), 'variables/playwright/.auth/state.json')

#     # Ensure the login state file is recent
#     def is_recent_state(path, hours=8):
#         if not os.path.exists(path):
#             return False
#         file_mod_time = datetime.fromtimestamp(os.path.getmtime(path))
#         return datetime.now() - file_mod_time < timedelta(hours=hours)
    


#-------------------- Login script without existing file check to create a forced new state of login --------------------#


# import os

# import time
# from playwright.sync_api import sync_playwright
# from dotenv import load_dotenv

# load_dotenv(dotenv_path='variables/Variables.env')
# load_dotenv(dotenv_path='variables/API.env')

# password = os.getenv('PASS')
# url = os.getenv('URL')
# username = os.getenv('USER')



# # Ensure directory exists
# def ensure_directory_exists(path):
#     if not os.path.exists(path):
#         os.makedirs(path)

# # Function to login and save the storage state
# def login_and_save_state():
#     with sync_playwright() as p:
#         browser = p.chromium.launch()
#         context = browser.new_context()
#         page = context.new_page()
#         page.goto(url)
        
#         # Perform login actions
#         page.get_by_placeholder("Enter Email").fill(username)
#         page.get_by_placeholder("Password").fill(password)
#         page.get_by_placeholder("Password").press("Enter")
        
#         # Wait for login to complete
#         time.sleep(5)
        
#         # Ensure the directory exists
#         ensure_directory_exists('variables/playwright/.auth')
        
#         # Save storage state (cookies, local storage) to a file
#         context.storage_state(path="variables/playwright/.auth/state.json")
#         browser.close()

# # Main execution block
# if __name__ == '__main__':
#     # Step 1: Login and save the state
#     login_and_save_state()