from dotenv import load_dotenv
import logging
import random
import requests
from playwright.sync_api import Page, sync_playwright, expect
import os
from datetime import datetime, timedelta
import re
import time
import string
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

# intercept api calls
def intercept_api_calls(page: Page):
    def log_post_request(route, request):
        if request.method == 'POST':
            logging.info(f"POST request intercepted: {request.url}")

        def on_response(response):
            if response.status != 200:
                logging.error(f"POST request to {request.url} failed with status code {response.status}")

        route.continue_()

        # Attach on_response callback to handle response
        route.on("response", on_response)

    page.route('**', log_post_request)

# def for contact clicks
def contact_pop_up(page, label):
    try:
        page.locator(".custom-select__input-container").first.click()
        for _ in range(1, 30):  # Press the down arrow random amount of times not exceeding 30
            page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        
        page.locator("input[name=\"first_name\"]").fill(utils.generate_alphanumeric(10))
        page.locator("input[name=\"last_name\"]").fill(utils.generate_alphanumeric(10))

        if page.get_by_label("Business").is_checked():
            try:
                page.locator("input[name=\"job_title\"]").fill(utils.generate_alphanumeric(10))
            except Exception as e:
                logging.error(f"Error filling job title input: {str(e)}")
        else:
            logging.info("Business label not checked, clicking combobox.")
            page.get_by_role("combobox").nth(1).click()
            for _ in range(1, 30):  # Press the down arrow random amount of times not exceeding 30
                page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")

        page.locator("input[name=\"email\"]").fill(utils.generate_alphanumeric(4) + "@rutvikqa.testinator.com")

        random_digits = ''.join(random.choices(string.digits, k=10))
        page.locator("#profile-form div").filter(has_text=re.compile(r"^Phone$")).first.click()
        page.locator("input[type='tel']:not([disabled])").first.fill(f"+1 ({random_digits[:3]}) {random_digits[3:6]}-{random_digits[6:]}")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        
        if label == "Client":
            page.keyboard.press("Tab")
        else:
            pass

        for _ in range(1, 25):  # Press the down arrow random amount of times not exceeding 30
            page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        page.keyboard.type(utils.generate_random_string(20))
        page.wait_for_timeout(1000)
        try:
            random.choice([page.get_by_label("Medium"), page.get_by_label("Low", exact=True), page.get_by_label("High")]).check()
        except:
            pass
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Save and + New Contact").click()
        page.wait_for_timeout(1000)
        intercept_api_calls(page)
        page.wait_for_timeout(1000)

    except Exception as ex:
        logging.error(f"Error in contact_pop_up: {str(ex)}")

def birthday_1(page):
    page.wait_for_timeout(1000)
    try:
        page.wait_for_timeout(1000)
        page.locator(".MuiGrid2-root > div:nth-child(12) > div:nth-child(2)").click()
    except:
        page.get_by_role("button").nth(1).click()
    page.wait_for_timeout(1000)
    page.get_by_label("calendar view is open, switch").click()
    page.wait_for_timeout(1000)
    page.get_by_role("radio", name="2000").click()
    page.wait_for_timeout(1000)
    page.get_by_label("October").click()
    page.wait_for_timeout(1000)
    page.get_by_role("gridcell", name="27").click()


def birthday_2(page):
    try:
        page.wait_for_timeout(2000)
        page.locator(".MuiGrid2-root > div:nth-child(13) > div:nth-child(2)").click()
    except:
        page.get_by_role("button").nth(1).click()
    page.wait_for_timeout(1000)
    page.get_by_label("calendar view is open, switch").click()
    page.wait_for_timeout(1000)
    page.get_by_role("radio", name="2000").click()
    page.wait_for_timeout(1000)
    page.get_by_label("October").click()
    page.wait_for_timeout(1000)
    page.get_by_role("gridcell", name="27").click()


def business(page):
    page.get_by_label("Business").check()

def company(page):
    page.locator("input[name=\"company_name\"]").fill(utils.generate_random_string(10))

def city_16(page):
    page.locator("div:nth-child(16)").click()                
    page.keyboard.type(utils.generate_random_string(10))
    
def city_17(page):
    page.locator("div:nth-child(17)").click()                
    page.keyboard.type(utils.generate_random_string(10))

def city_15(page):
    page.locator("div:nth-child(15)").click()                
    page.keyboard.type(utils.generate_random_string(10))

def zip(page):
    original_code = "s2s2s2"
    page.locator("input[name=\"zip_code\"]").fill(original_code)


def Contacts(page: Page) -> None:
    page.goto("https://staging.bluemind.app/contacts")
    # test all contacts buttons
    try:
        page.wait_for_timeout(8000)
        page.get_by_text("All Contacts").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Refresh' icon: {e}")
    
    # click new contact button
    page.get_by_role("button", name="New Contact").click()
    
    labels = ["Lead", "Prospect", "Client", "Contact"]

    # for each type of contact, save a contact
    for label in labels:
        if label == "Lead":
            if random.choice([True, False]):
                logging.info("Clicked Lead business")
                business(page)
                page.wait_for_timeout(1000)
                company(page)
                city_16(page)
                contact_pop_up(page, label)
            else:
                logging.info("Clicked Lead individual")
                page.wait_for_timeout(1000)
                city_15(page)
                contact_pop_up(page, label)

        elif label == "Prospect":
            if random.choice([True, False]):
                page.get_by_label("Prospect").check()
                business(page)
                page.wait_for_timeout(1000)
                logging.info("Clicked Prospect business")
                city_17(page)
                company(page)
                birthday_2(page)
                page.wait_for_timeout(1000)
                contact_pop_up(page, label)
            else:
                logging.info("Clicked Prospect individual")
                page.get_by_label("Prospect").check()
                page.wait_for_timeout(1000)
                city_16(page)
                page.wait_for_timeout(1000)
                birthday_1(page)
                page.wait_for_timeout(1000)

                contact_pop_up(page, label)

        elif label == "Client":
            if random.choice([True, False]):
                page.get_by_label("Client", exact=True).check()
                business(page)
                logging.info("Clicked Client business")
                page.wait_for_timeout(1000)
                city_17(page)
                company(page)
                birthday_2(page)
                zip(page)
                page.wait_for_timeout(1000)

                contact_pop_up(page, label)
            else:
                logging.info("Clicked Client Individual")
                page.get_by_label("Client", exact=True).check()
                page.wait_for_timeout(1000)
                city_16(page)
                birthday_1(page)
                zip(page)
                page.wait_for_timeout(1000)

                contact_pop_up(page, label)

        elif label == "Contact":
            if random.choice([True, False]):
                page.get_by_label("Contact", exact=True).check()
                business(page)
                page.wait_for_timeout(1000)
                logging.info("Clicked Contact business")
                city_17(page)
                company(page)
                birthday_2(page)     
                page.wait_for_timeout(1000)
      
                contact_pop_up(page, label)
            else:
                page.get_by_label("Contact", exact=True).check()
                logging.info("Clicked Contact individual")
                page.wait_for_timeout(1000)
                city_16(page)
                birthday_1(page)
                page.wait_for_timeout(1000)

                contact_pop_up(page, label)
    
    page.get_by_label("close", exact=True).click()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        Contacts(page)
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