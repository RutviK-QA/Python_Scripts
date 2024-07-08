import logging
import random
import time
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils
import re
import  string
import subprocess   
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

emails = [outlook_account, outlook_account2]    
selected_email = random.choice(emails)

def test_signup(page):

    logging.info("Navigating to signin page")
    page.goto(loginurl)
    page.wait_for_timeout(5000)

    logging.info("Clicking the Microsoft login button")
    page.click('.btn-microsoft')    

    logging.info(f"Filling in email: {selected_email}")
    page.fill('input[name="loginfmt"]', selected_email)
    page.press('input[name="loginfmt"]', 'Enter')
    page.press('input[name="loginfmt"]', 'Enter')

    logging.info("Filling in password")
    page.fill('[data-testid="i0118"]', outlook_password)
    page.press('input[name="passwd"]', 'Enter')

    logging.info("Clicking 'Don't show this again' checkbox")
    page.click('text="Don\'t show this again"')

    logging.info("Clicking 'Yes' button to accept")
    page.click('#acceptButton')

    logging.info("Test completed successfully")



def main(): 
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        test_signup(page)
        time.sleep(7)
        browser.close()
        
if __name__ == '__main__':
    try:
        main()
        utils.start_report(test_results, script_name)
    except Exception as e:
        utils.traceback_error_logging(script_name, e)
        utils.end_report(test_results, script_name)

