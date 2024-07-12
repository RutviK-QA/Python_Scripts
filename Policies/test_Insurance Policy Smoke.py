import re
import time 
from dotenv import load_dotenv
import logging
import requests
from playwright.sync_api import Page, sync_playwright, expect
import os
from datetime import datetime, timedelta
import random
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

def random_letter(length):
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=length))

def random_number():
    return random.randint(0, 9999999999)


def Insurance_test(page: Page) -> None:
    page.goto(url_contacts)
    page.wait_for_timeout(5000)
    
    # Go to the Products page
    page.get_by_role("link", name="Products").click()
    
    # Add Policy Details
    page.get_by_role("button", name="Add Policy Details").click()
    
    # Select Insurance Company
    page.get_by_label("Insurance company *").click()
    page.wait_for_timeout(2000)
    utils.for_x_y(page, 1, 10)
    logging.info("selected insurance company")
    # Fill Policy Number

    page.get_by_label("Policy number *").fill(utils.generate_random_string(7))
    logging.info("added policy number")

    # Check Joint/Single randomly
    is_joint = random.choice([True, False])
    if is_joint:
        page.get_by_label("Joint").check()
    else:
        page.get_by_label("Single").check()
    page.wait_for_timeout(2000)
    logging.info("Joint/Single tapped")

    # Randomise between selecting Yes and No
    selected_yes = random.choice([True, False])
    if selected_yes:
        page.get_by_label("Yes", exact=True).check()
    else:
        page.get_by_label("No", exact=True).check()
    # Perform actions based on Joint/Single and Yes/No selections
    if not is_joint:
        if selected_yes:
            # Single and Yes
            page.get_by_label("Search Client").fill(random_letter(1))
            page.wait_for_timeout(2000)
            utils.for_x_y(page, 1, 30) 
            
        else:
            # Single and No
            page.locator("#policy-owner-form").get_by_label("Search Client").fill(random_letter(1))
            page.wait_for_timeout(2000)
            utils.for_x_y(page, 1, 30)
            
            page.get_by_label("Search Client").fill(random_letter(1))
            page.wait_for_timeout(2000)
            utils.for_x_y(page, 1, 30)
    else:
        if selected_yes:
            # Joint and Yes
            page.get_by_label("Search Client").first.fill(random_letter(1))
            page.wait_for_timeout(2000)
            utils.for_x_y(page, 1, 30)
            page.get_by_label("Search Client").fill(random_letter(1))
            page.wait_for_timeout(2000)
            utils.for_x_y(page, 1, 30)

        else:
            # Joint and No
            page.get_by_label("Search Client").first.fill(random_letter(1))
            page.wait_for_timeout(2000)        
            utils.for_x_y(page, 1, 30)
            
            page.locator("#policy-owner-form").get_by_label("Search Client").fill(random_letter(1))
            page.wait_for_timeout(2000)        
            utils.for_x_y(page, 1, 30)

            page.get_by_label("Search Client").fill(random_letter(1))
            page.wait_for_timeout(2000)   
            utils.for_x_y(page, 1, 30)

    logging.info("Selected Contacts")

    # Insured 1
    
    page.get_by_label("Product type").click()
    utils.for_x_y(page, 1, 30)
    logging.info("Selected Prod type")

    page.get_by_text("$Total Coverage").locator("#maxValueFaceAmount").fill(str(random_number()))
    page.get_by_text("$Premium").locator("#maxValueFaceAmount").fill(str(random_number()))
    page.get_by_label(random.choice(["Annualized", "Monthly", "Annually"])).click()
    logging.info("Selected until status")

    page.get_by_label("Status").click()
    utils.for_x_y(page, 1, 50)
    page.get_by_label("Status").click()
    utils.for_x_y(page, 1, 50)
    selected_value = page.get_by_label("Status").input_value
    logging.info(f"Selected value: {selected_value}")

    # Handle actions based on the selected value
    try:
        page.get_by_label("Plan type").click()
        utils.for_x_y(page, 1, 20)
    except Exception as e: 
        logging.error(f"Error selecting plan type: {e}")



    try:
        page.get_by_label("Plan name").fill(utils.generate_random_string(10))
    except Exception as e:
        logging.error(f"cant click plan name:, {e}")
    
    try:
        page.locator("div").filter(has_text=re.compile(r"^Riders$")).nth(3).click()
        utils.for_x_y(page, 1, 20)
    except Exception as e:
        logging.error(f"cant click riders:, {e}")

    # List of fields to fill
    fields_to_fill = ["Elimination Period", "Benefit Period", "Occupation Class"]
    for field in fields_to_fill:
        try:
            page.get_by_label(field).fill(utils.generate_random_string(10))
        except Exception as e: 
            logging.info(f"Failed to fill {field}: {e}")

    try:
        page.locator(".MuiInputAdornment-root > .MuiButtonBase-root").click()
        page.wait_for_timeout(500)
        page.get_by_role("gridcell", name="1", exact=True).click()
    except Exception as e:
        logging.error(f"Cant click 1:, {e}")

    try:
        page.locator(".MuiInputAdornment-root > .MuiButtonBase-root").first.click()
        page.wait_for_timeout(500)
        page.get_by_role("gridcell", name="1", exact=True).click()
    except Exception as e:
        logging.error(f"cant click .first:, {e}")

    # Fill reasons
    reason_fields = ["Reason for postponed", "Reason for decline", "Reason for rated temporarily"]
    for field in reason_fields:
        try:
            page.get_by_label(field).fill(utils.generate_random_string(10))
        except Exception as e:
            logging.error(f"Failed to fill {field}: {e}")

    try:
        page.get_by_label("% of rating").fill(random.randint(0, 100))
    except Exception as e:
        logging.error(f"cant click rating:, {e}")

    # Locator indices for dates
    date_indices = [8, 9, 11, 12, 13]
    for index in date_indices:
        try:
            page.locator(f"div:nth-child({index}) > .bm-task-due-date > .custom-date-picker > .MuiFormControl-root > .MuiInputBase-root").click()
            page.wait_for_timeout(500)
            page.get_by_role("gridcell", name="1", exact=True).click()
        except Exception as e:
            logging.error(f"Failed to click {index}: {e}")



    #Insurance Note
    # Fill the rdw-editor element with random string
    page.get_by_label("rdw-editor").fill(utils.generate_random_string(100))

    # Click the Save Note button
    page.get_by_role("button", name="Save Note").click()
    page.get_by_label("Delete note").first.click()

    # Fill the rdw-editor element with another random string
    page.get_by_label("rdw-editor").fill(utils.generate_random_string(100))

    # Click the Save Note button again
    page.get_by_role("button", name="Save Note").click()

    # Click the Delete note button by selecting the row based on the previously retrieved note_text

    # Click the Edit note button
    page.get_by_label("Edit note").click()

    # Fill the rdw-editor element with a shorter random string
    page.get_by_label("rdw-editor").fill(utils.generate_random_string(20))

    # Click the Update Note button
    page.get_by_role("button", name="Update Note").click()
    logging.info("Saved Final Note")

    # Click the Save Policy button
    page.get_by_role("button", name="Save Policy").click()

    logging.info("Saved Policy")

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        Insurance_test(page)
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