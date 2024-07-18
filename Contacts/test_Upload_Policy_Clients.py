from playwright.sync_api import sync_playwright, Playwright, Error
from datetime import datetime, timedelta
import time
import os
import logging
import random
import json
from dotenv import load_dotenv
import re
import  string
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils
from collections import defaultdict

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
api_urls = defaultdict(dict)
test_results = []

# Function to search and process API response
def download_birthdays(page):
    page.goto(url_contacts)
    page.wait_for_timeout(4000)
    page.get_by_text("Clients").click()
    page.wait_for_timeout(2000)
    page.get_by_role("button", name="Actions").click()
    page.get_by_role("menuitem", name="Policy Upload").click()
    logging.info("Policy Upload clicked")

    try:
        try:
            page.get_by_role("button", name="Download sample CSV").click()
            logging.info("Download sample CSV clicked")
        except Exception as e:
            logging.info(f"Error in file download: {e}")

        page.get_by_label("Insurance company *").click()
        page.wait_for_timeout(300)
        utils.for_x_y(page, "1", "20")
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Preview Sample CSV").click()

        # Find the latest file (n) in the directory
        latest_file = utils.find_latest_policy()
        
        try:
            file_input =  page.locator('input[type="file"]')
            file_input.set_input_files(latest_file)
            logging.info("File inserted")
        except Exception as e:
            logging.info(f"Error in insert .{e}")

        page.wait_for_timeout(6000)
        page.get_by_role("button", name="Next").click()

        page.get_by_role("button", name="Upload").click()
        logging.info("Upload button clicked")
        page.wait_for_timeout(4000)
        page.get_by_role("button", name="Close").click()
        logging.info("success")

    except Exception as e:
        utils.show_api_response(api_urls)
        logging.info(f"Error in file upload .{e}")

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        download_birthdays(page)
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