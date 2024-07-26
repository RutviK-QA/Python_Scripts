import re
import logging
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import os
import requests
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils
from collections import defaultdict


#Load vars
utils.load_env_files()
script_path, state_path = utils.paths()

#Retrieve variables
(password, loginurl, username, logs_folder, auth, google_account, 
 google_password, outlook_account, outlook_password, outlook_account2, 
 api_url, url_contacts, login_api, mailinator, token, signup) = utils.get_env_variables()

script_name = os.path.basename(__file__).split('.')[0]
utils.logging_setup(script_name)


api_pattern = re.compile(fr'^{re.escape(api_url)}')
api_urls = defaultdict(dict)
test_results = []

#Perform API test
# def perform_api_test():
#     payload = {
#         "email": "rutvik@rutvikqa.testinator.com",
#         "password": "Qa@12345678"
#     }
#     headers = {
#         "Origin": "https://staging.bluemind.app",
#         "Content-Type": "application/json"
#     }
#     try:
#         response = requests.post(login_api, json=payload, headers=headers)
#         response.raise_for_status()
#         data = response.json()
#         logging.info(f"API response: {data}")
#         return "API Test: PASS" if response.status_code == 200 else "API Test: FAIL"
#     except Exception as e:
#         logging.error(f"API test failed: {e}")
#         return "API Test: FAIL"

def login(page: Page) -> None:
    try:
        page.goto(loginurl)
        logging.info("Navigated to signin page")
        
        page.get_by_placeholder("Enter Email").click()
        page.get_by_placeholder("Enter Email").fill(username)
        page.get_by_placeholder("Enter Email").press("Tab")
        logging.info("Entered email")

        page.get_by_placeholder("Password").fill(password)
        page.get_by_placeholder("Password").press("Enter")
        logging.info("Entered password and submitted login form")

    except Exception as e:
        logging.info(f"Error in file upload .{e}")

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        response_handler, request_handler = utils.start_handler(page, api_urls)
        login(page)
        utils.stop_handler(page, api_urls, response_handler, request_handler)
        browser.close()


if __name__ == '__main__':
    try:
        main()
        utils.start_report(test_results, script_name)

    except Exception as e:
        utils.traceback_error_logging(script_name, e)
        utils.end_report(test_results, script_name)