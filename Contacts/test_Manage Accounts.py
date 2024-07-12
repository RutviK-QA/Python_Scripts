from dotenv import load_dotenv
import logging
import random
from playwright.sync_api import Page, sync_playwright, expect
import os
from datetime import datetime, timedelta
import re
import time
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

def Contacts(page: Page) -> None:
    page.wait_for_timeout(1000)
    page.get_by_label("Manage communication accounts").click()
    page.wait_for_timeout(1000)

    o15=r"^rutvik@bluemind\.appPrimarySign Out$"
    if page.locator("div").filter(has_text=re.compile(fr"{o15}")).get_by_role("button").is_visible():
        page.locator("div").filter(has_text=re.compile(fr"{o15}")).get_by_role("button").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
    else:
        logging.info("No Primary Google account found")
    
    o14=r"^rutvik@bluemind\.appMake it primarySign Out$"
    if page.locator("div").filter(has_text=re.compile(fr"{o14}")).get_by_role("button").is_visible():
        page.locator("div").filter(has_text=re.compile(fr"{o14}")).get_by_role("button").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
    else:
        logging.info("No non primary Google account found")

    o13=r"^rutvikqatest@outlook\.comPrimarySign Out$"
    if page.locator("div").filter(has_text=re.compile(fr"{o13}")).get_by_role("button").is_visible():
        page.locator("div").filter(has_text=re.compile(fr"{o13}")).get_by_role("button").click() 
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
    else:    
        logging.info("No Primary Outlook account found")
    
    o12=r"^rutvikqatest@outlook\.comMake it primarySign Out$"
    if page.locator("div").filter(has_text=re.compile(fr"{o12}")).get_by_role("button").is_visible(): 
        page.locator("div").filter(has_text=re.compile(fr"{o12}")).get_by_role("button").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
    else:        
        logging.info("No non primary Outlook account found")

    try:
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
        page.wait_for_timeout(1000)
        logging.info("Signed out of 2nd account")
    except:
        pass


    if  page.get_by_text("rutvik@bluemind.appReconnect").is_visible():   
        with page.expect_popup() as popup:
            page.get_by_role("button", name="Reconnect").click()
        popup = popup.value
        utils.google(popup, google_account, google_password)
        logging.info("Reconnected to Google")

    elif  page.get_by_text("rutvik@bluemind.appReconnect").first.is_visible():   
        with page.expect_popup() as popup:
            page.get_by_role("button", name="Reconnect").first.click()
        popup = popup.value
        utils.google(popup, google_account, google_password)
        logging.info("Reconnected to Google")

    elif  page.get_by_text("rutvik@bluemind.appReconnect").nth(1).is_visible():   
        with page.expect_popup() as popup:
            page.get_by_role("button", name="Reconnect").nth(1).click()
        popup = popup.value
        utils.google(popup, google_account, google_password)
        logging.info("Reconnected to Google")
    
    random_n= random.choice([4,2])
    reconnect_decision = random.choice([True, False])
    if reconnect_decision: 
        try:
            page.get_by_role("button").nth(random_n).click()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="Sign Out").click()
        except Exception as e: 
            logging.error(f"By tapping n={random_n}, error occured: {str(e)}")
   
    if page.get_by_text("rutvikqatest@outlook.comReconnect").is_visible():
        try:
            page.get_by_role("button", name="Reconnect").click()
            utils.outlook(page, outlook_account, outlook_password)
            logging.info("Reconnected to Outlook")
        except Exception as e:
            logging.error(f"By tapping G Reconnect, error occured: {str(e)}")
    elif page.get_by_text("rutvikqatest@outlook.comReconnect").first.is_visible():
        try:
            page.get_by_role("button", name="Reconnect").first.click()
            utils.outlook(page, outlook_account, outlook_password)
            logging.info("Reconnected to Outlook")
        except: 
            pass
            
    elif page.get_by_text("rutvikqatest@outlook.comReconnect").nth(1).is_visible():
        try:
            page.get_by_role("button", name="Reconnect").nth(1).click()
            utils.outlook(page, outlook_account, outlook_password)
            logging.info("Reconnected to Outlook")
        except Exception as e:  
            logging.error(f"By tapping O Reconnect, error occured: {str(e)}")
    
        
    if page.get_by_role("button", name="Connect Gmail").is_visible():   
        with page.expect_popup() as popup_info:
            page.get_by_role("button", name="Connect Gmail").click()
        popup = popup_info.value
        utils.google(popup, google_account, google_password)
        logging.info("Connected to Google")
        page.wait_for_timeout(5000)
    else:
        pass
    
    if page.get_by_role("button", name="Connect Outlook").is_visible():
        utils.outlook(page, outlook_account, outlook_password)
        logging.info("Connected to Outlook")

    else:
        pass

    page.wait_for_timeout(2000)
    page.locator('div.account-email:has(p.select-primary-pill:has-text("Make it primary")) h4').hover()
    try:
        page.locator('p.select-primary-pill:has-text("Make it primary")').click()
        logging.info("Switched primary account")
    except Exception as e:
        logging.error(f"Error occured in switching primary account: {str(e)}")

    page.wait_for_timeout(2000)
    decision = random.choice([True, False])
    logging.info(f"Decision to log out: {decision}")

    if decision:
        try:
            page.locator("div").filter(has_text=re.compile(r"^rutvikqatest@outlook\.comPrimarySign Out$")).get_by_role("button").click()
        except Exception as e:
            page.locator("div").filter(has_text=re.compile(r"^rutvik@bluemind\.appPrimarySign Out$")).get_by_role("button").click()
            logging.error(f"Error occured in signing out of primary account: {str(e)}")
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
        page.wait_for_timeout(1000)

        second_decision = random.choice([True, False])
        logging.info(f"Decision to log out of 2nd account: {second_decision}")

        if second_decision:
            page.get_by_role("button", name="Sign Out").click()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="Sign Out").click()
            page.wait_for_timeout(1000)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.goto("https://staging.bluemind.app/contacts")
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