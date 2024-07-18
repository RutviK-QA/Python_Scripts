import time
import logging
import random
import string
from playwright.sync_api import sync_playwright, Page
import os
from datetime import datetime
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils
import re
import subprocess
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

def plus_button(page: Page) -> None:

    page.goto("https://staging.bluemind.app/overview")
    page.wait_for_timeout(5000)

    # Generate random first and last names
    first_name = utils.generate_alphanumeric(2)
    last_name = utils.generate_alphanumeric(2)

    #Add contact
    page.click(".reveal-menu-button")
    page.wait_for_timeout(500)
    page.click('text="Add Contact"')
    page.fill('input[name="first_name"]', first_name)
    page.fill('input[name="last_name"]', last_name)
    page.wait_for_selector('.MuiGrid2-root:nth-child(2) .MuiFormControlLabel-root:nth-child(2) > .MuiTypography-root').click()
        # Fill today's date in bday field
    page.click('.MuiInputBase-inputAdornedEnd')
    page.wait_for_timeout(1000)
    current_day = datetime.now().day  # Fix the datetime import here
    page.get_by_role("gridcell", name=str(current_day), exact=True).click()
    page.click('.MuiButton-containedPrimary')
    logging.info("Saved Contact.")
    page.wait_for_timeout(3000)

    # Add task
    page.click(".reveal-menu-button")
    page.wait_for_timeout(1000)
    page.click('text="Add Task"')
    page.wait_for_timeout(1000)
    page.click('[role="combobox"]') 
    page.wait_for_timeout(500)
    page.click(f'text="{first_name} {last_name}"')
    page.wait_for_timeout(1000)
    page.click('.MuiGrid-root:nth-child(3) .MuiFormControlLabel-root:nth-child(2) .PrivateSwitchBase-input') 
    page.fill('input[name="title"]', "Test Subject")
    page.fill('textarea[name="notes"]', f"{first_name} {last_name}")
    page.wait_for_timeout(500)
    # Click on the input field
    page.locator(".MuiInputAdornment-root > .MuiButtonBase-root").click()
    # Calculate the next day
    current_day = page.evaluate('new Date().getDate()') + 1
    # Wait for the button to be clickable
    day_button = page.wait_for_selector(f'//button[contains(@class, "MuiButtonBase-root") and contains(@class, "MuiPickersDay-root") and contains(@class, "MuiPickersDay-dayWithMargin") and text()="{current_day}"]')
    # Hover over the button
    day_button.hover()
    # Click on the button for the next day
    day_button.click()
    page.click('.MuiButton-containedSizeMedium')
    page.click('.MuiButton-containedSizeSmall')
    logging.info("Saved Task.")
    page.wait_for_timeout(3000)
    
    # Add note
    page.click(".reveal-menu-button")
    page.click('text="Add Note"')
    page.click('.MuiAutocomplete-inputRoot input')
    page.fill('.MuiAutocomplete-inputRoot input', f"{first_name} {last_name}")
    page.click('.MuiAutocomplete-option')
    page.keyboard.press('Tab')
    page.keyboard.press('ArrowDown')
    page.keyboard.press('ArrowDown')
    page.keyboard.press('Enter')
    page.keyboard.press('Tab')
    page.type('.rich-text-editor-editor', f"{first_name} {last_name}")
    page.click('.MuiButton-textSizeSmall')
    logging.info("Saved Note.")
    page.wait_for_timeout(3000)
    # Record a Meeting
    page.click(".reveal-menu-button")
    page.click('text="Record a Meeting"')
    page.click('.MuiAutocomplete-inputRoot input')
    page.fill('.MuiAutocomplete-inputRoot input', f"{first_name} {last_name}")
    page.click('.MuiAutocomplete-option')
    page.keyboard.press('Tab')
    page.type('.rich-text-editor-editor', f"{first_name} {last_name}")
    page.click('.MuiButton-textSizeSmall')
    logging.info("Saved Meeting Note.")

def main(): 

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        plus_button(page)
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





