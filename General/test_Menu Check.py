import time
import logging
from playwright.sync_api import sync_playwright, Page
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils
import re
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

def menu_check(page: Page) -> None:
    page.goto('https://staging.bluemind.app/overview')
    page.wait_for_timeout(5000)

    # Clicking sidebar toggle
    sidebar_toggle = page.wait_for_selector(".expand-sidebar-btn")
    sidebar_toggle.click()
    logging.info("Clicked sidebar toggle.")
    page.wait_for_timeout(1000)

    # Clicking sidebar options
    for option in ["Contacts", "Tasks", "Calendar", "Mail Box", "Compliance Overview"]:
        page.wait_for_selector(f"//a[normalize-space(.)='{option}']").click()
        logging.info(f"Clicked {option}.")
        page.wait_for_timeout(1000)
    
    # Clicking dropdown button
    page.wait_for_selector("#panel1a-header").click()
    logging.info("Clicked dropdown button.")
    page.wait_for_timeout(1000)

    # Clicking more options
    for option in ["Document Library", "Send Documents", "Products", "FNA", "Products"]:
        page.wait_for_selector(f"//a[normalize-space(.)='{option}']").click()
        logging.info(f"Clicked {option}.")
        page.wait_for_timeout(1000)

    # Clicking Investment Policy using JavaScript
    page.wait_for_selector('text="Investment Policy"', timeout=5000).click()

    logging.info("Clicked Investment Policy.")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        menu_check(page)
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
        utils.show_api_response(api_urls)