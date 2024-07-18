from dotenv import load_dotenv
import logging
import random
from playwright.sync_api import Page, sync_playwright, expect
import os
from datetime import datetime, timedelta
import string
import time
import re
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

# Variable to store the intercepted request & URL to intercept
intercepted_request = None
url_to_intercept= "https://staging-api.bluemind.app/api/merge-client-details"

# Handle request intercept
def handle_request(route, request):
    global intercepted_request
    if request.url == url_to_intercept and request.method == 'POST':
        intercepted_request = request
        route.fulfill(
            status=200,
            body='{"status": "ok", "data": null}',
            headers={'Content-Type': 'application/json'}
        )
    else:
        route.continue_()

def Contacts(page: Page) -> None:
    page.wait_for_timeout(5000)
    page.get_by_label("Select all rows").check()
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Actions").click()
    page.get_by_role("menuitem", name="Merge Contacts").click()
    page.wait_for_timeout(1000)  
    m = 9  # Replace with number of locators

    locators1 = [
        ".search-card-dt > svg > path"
    ] + [
        f"div:nth-child({i}) > .search-card > div:nth-child(3) > svg > path"
        for i in range(2, m + 1)
    ]
    # Select a random locator & click
    random_locator1 = random.choice(locators1)
    try:
        page.locator(random_locator1).first.click()
    except:
        page.locator(random_locator1).click()
    page.wait_for_timeout(1000)
    n = 8  # Replace with the number of locators

    locators = [
        ".search-card-dt > .MuiButtonBase-root > .PrivateSwitchBase-input"
    ] + [
        f"div:nth-child({i}) > .search-card > div:nth-child(3) > .MuiButtonBase-root > .PrivateSwitchBase-input"
        for i in range(2, n + 1)
    ]
    # Select a random locator & click
    random_locator = random.choice(locators)
    try:
        page.locator(random_locator).first.click()
    except:
        page.locator(random_locator).click()
        
    page.get_by_label("Search contact to Add").click()
    page.get_by_label("Search contact to Add").fill(utils.generate_random_alphabet(1))
    page.wait_for_timeout(2000)
    utils.for_x_y(page, 1, 30)
    page.wait_for_timeout(500)

    page.route('**', handle_request)
    page.get_by_role("button", name="Merge").click()
    page.wait_for_timeout(5000)

    # Verify the API call
    if intercepted_request:
        try:
            response = intercepted_request.response()
            status = response.status
            response_data = response.body().decode('utf-8')

            if status == 200:
                logging.info("Merge API successful")
            else:
                logging.info(f"Intercepted request method: {intercepted_request.method}")
                logging.info(f"Intercepted request post data: {intercepted_request.post_data()}")
                logging.info(f"Intercepted request url: {intercepted_request.url}")
                logging.info(f"Intercepted request response data: {response_data}")
        except Exception as e:
            logging.error(f"Error while verifying the intercepted request: {e}")
    else:
        logging.info("Merge API call not found")

def main(): 
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("https://staging.bluemind.app/contacts")
        response_handler, request_handler = utils.start_handler(page, api_urls)
        Contacts(page)
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