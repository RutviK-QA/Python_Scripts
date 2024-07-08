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

# Load environment variables
utils.load_env_files()
script_path, state_path = utils.paths()

# Retrieve environment variables
(password, loginurl, username, logs_folder, auth, google_account, 
 google_password, outlook_account, outlook_password, outlook_account2, 
 api_url, url_contacts, login_api, mailinator, token, signup) = utils.get_env_variables()

utils.logging_setup(script_name = os.path.basename(__file__).split('.')[0])

api_pattern= re.compile(r'^https://staging-api.bluemind.app/api/client/export_birthdays')  

script_name = os.path.basename(__file__).split('.')[0]
api_urls = []
test_results = []


# Function to search and process API response
def download_birthdays(page):
    page.goto("https://staging.bluemind.app/contacts")
    page.wait_for_timeout(5000)
    page.get_by_role("button", name="Actions").click()
    page.get_by_role("menuitem", name="Export Birthdays").click()

    request_handler = lambda request: utils.handle_request1(request, api_urls, api_pattern)
    page.on('request', request_handler)
    page.on('response', utils.handle_response_failure)

    month= ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    try:
        for m in month:
            
            page.wait_for_timeout(2000)
            page.get_by_label(m).click()

            try:
                page.get_by_role("button", name="Export Excel").click()
                page.wait_for_timeout(2000)
            except Exception as e:
                logging.error(e)

            if page.locator('div.MuiAlert-filledError span', has_text='No contacts have birthdays in the selected month.').is_visible():
                logging.info(f"No Birthdays (Excel) for month - {m}")  
                page.wait_for_timeout(1000)
                page.get_by_label("Close", exact=True).click()
            else:
                page.wait_for_timeout(1000)
                page.get_by_label("Close", exact=True).click()
                logging.info(f"Downloaded Excel file: {m}")

            try:
                page.get_by_role("button", name="Export PDF").click()
                page.wait_for_timeout(2000)
            except Exception as e:      
                logging.error(e)

            if page.locator('div.MuiAlert-filledError span', has_text='No contacts have birthdays in the selected month.').is_visible():
                logging.info(f"No Birthdays (PDF) for month - {m}")  
                page.wait_for_timeout(1000)
                page.get_by_label("Close", exact=True).click()
            else:
                page.wait_for_timeout(1000)
                page.get_by_label("Close", exact=True).click()
                logging.info(f"Downloaded PDF file: {m}")
 
    except Exception as e:
        logging.error(e)
    
    page.remove_listener("request", request_handler)
    page.remove_listener("response", utils.handle_response_failure)
    
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        download_birthdays(page)
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