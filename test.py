from dotenv import load_dotenv
import logging
from playwright.sync_api import Page, sync_playwright, expect
import os
from datetime import datetime, timedelta
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

load_dotenv(dotenv_path='variables/API.env')

leads=os.getenv('C_LEADS')
prospects=os.getenv('C_PROSPECTS')
clients=os.getenv('C_CLIENTS')

leads_all=os.getenv('LEADS_GET_ALL')
prospects_all=os.getenv('PROSPECTS_GET_ALL')
clients_all=os.getenv('CLIENTS_GET_ALL')

# Function to get count from the API response
def get_api_count(api_data, key):
    return api_data['data'][key]

# Function to get count from the HTML element
def get_element_count(page, title):
    selector = f".title:has-text('{title}') + .count"
    return page.inner_text(selector)


def test(page: Page) -> None:
    page.goto("https://staging.bluemind.app/calendar")

    tomorrow = datetime.today() + timedelta(days=1)
    formatted_date = tomorrow.strftime('%A, %B %d, %Y')
    page.get_by_label(formatted_date, exact=True).dblclick()

    page.get_by_role("combobox").first.click()
    utils.for_x_y(page, 1, 30)  

    page.get_by_role("combobox").nth(3).fill(utils.generate_alphanumeric(2)+("@rutvikqa.testinator.com") )




    logging.info("reached bottom")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        test(page)
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

