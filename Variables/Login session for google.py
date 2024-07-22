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
def is_recent_google_state(path, hours=8):
    if not os.path.exists(path):
        return False
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.now() - file_mod_time < timedelta(hours=hours)

# Function to login and save the storage state
def login_and_save_state_google():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        
        # Perform login actions
        page.get_by_role("button", name="Login with Google").click()
        try:
            page.get_by_role("link", name="rutvik khorasiya rutvik@").click(timeout=3000)
        except:
            page.get_by_label("Email or phone").fill("rutvik@bluemind.app")
            page.get_by_label("Email or phone").press("Enter")
            page.get_by_label("Enter your password").fill("Rutvik2710$$")
            page.get_by_label("Enter your password").press("Enter")
            
        # Wait for login to complete
        page.wait_for_timeout(15000)
        
        # Ensure the directory exists
        ensure_directory_exists('variables/playwright/.auth')
        
        # Save storage state (cookies, local storage) to a file
        context.storage_state(path="variables/playwright/.auth/state-google.json")
        browser.close()

# Main execution block
if __name__ == '__main__':
    state_path = 'variables/playwright/.auth/state-google.json'
    
    # Step 1: Check if the state is recent
    if not is_recent_google_state(state_path):
        # Step 2: Login and save the state if it's not recent
        login_and_save_state_google()
        print("Created a new login session")
    else:
        print("Logging in using existing session.")