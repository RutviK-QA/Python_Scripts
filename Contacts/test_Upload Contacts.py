from playwright.sync_api import sync_playwright, Page
import time
import requests
import re
import os
import logging
import random
from dotenv import load_dotenv
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils

# Load environment variables
utils.load_env_files()
script_path, state_path = utils.paths()

# Retrieve environment variables
(password, loginurl, username, logs_folder, auth, google_account, 
 google_password, outlook_account, outlook_password, outlook_account2, 
 api_url, url_contacts, login_api, mailinator, token, signup) = utils.get_env_variables()

script_name = os.path.basename(__file__).split('.')[0]
utils.logging_setup(script_name)

api_pattern = re.compile(fr'^{re.escape(api_url)}')
api_urls = []
test_results = []

def upload_contact(page: Page) -> None:

    page.goto("https://staging.bluemind.app/contacts")
    page.wait_for_timeout(6000)
    page.get_by_role("button", name="Actions").click()
    page.get_by_role("menuitem", name="Upload").click()
    
    try:
        page.get_by_role("button", name="Download sample CSV").click()
    except Exception as e:
        logging.info(f"Error in file download: {e}")

    # Find the latest file to upload
    latest_file = utils.find_latest_contact_upload()
    
    try:
        file_input =  page.locator('input[type="file"]')
        file_input.set_input_files(latest_file)
    except Exception as e:
        logging.info(f"Error in file upload .{e}")

    page.wait_for_timeout(3000) 
    page.get_by_role("button", name="Next").click()

    page.get_by_role("button", name="Upload").click() 

    try:
        toast_msg = page.wait_for_selector("div[role='alert']", timeout=5000)
        assert "Contacts saved successfully." in toast_msg.inner_text()
        logging.info("Success message: Contacts saved successfully.")
    except:
        logging.info("No success message, check for failures!")

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        upload_contact(page)
        page.wait_for_timeout(8000)
        utils.stop_handler(page, api_urls, response_handler, request_handler)
        context.close()
        browser.close()
        
if __name__ == '__main__':
    # Ensure the state is recent by running the login script if necessary
    if not utils.is_recent_state(state_path):
        subprocess.run(['python', script_path])
    try:
        main()
        utils.start_report(test_results, script_name)
    except Exception as e:
        utils.traceback_error_logging(script_name, e)
        utils.end_report(test_results, script_name) 