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

def Contacts(page: Page) -> None:
    page.wait_for_timeout(1000)
    page.get_by_label("Manage communication accounts").click()
    page.wait_for_timeout(1000)

    # If rutvik@bluemind is found and is not primary, sign out
    o14=r"^Make Primaryrutvik@bluemind\.app$"
    if page.locator("div").filter(has_text=re.compile(fr"{o14}")).get_by_label("Sign out").is_visible():
        page.locator("div").filter(has_text=re.compile(fr"{o14}")).get_by_label("Sign out").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
        logging.info("Signed out of Google (non primary)")
    else:
        # If rutvik@bluemind is found and is primary, then sign out
        o15=r"^rutvik@bluemind\.appPrimarySign Out$"
        if page.locator("div").filter(has_text=re.compile(fr"{o15}")).get_by_role("button").is_visible():
            page.locator("div").filter(has_text=re.compile(fr"{o15}")).get_by_role("button").click()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="Sign Out").click()
            logging.info("Signed out of Google (primary)")
        else:
            pass
            # logging.info("No Primary Google account found"

    # If rutvikqatest@outlook is found and is not primary, sign out
    o12=r"^Make Primaryrutvikqatest@outlook\.com$"
    if page.locator("div").filter(has_text=re.compile(fr"{o12}")).get_by_label("Sign out").is_visible(): 
        page.locator("div").filter(has_text=re.compile(fr"{o12}")).get_by_label("Sign out").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
    else:        
        # If rutvikqatest@outlook is found and is primary, sign out
        o13=r"^rutvikqatest@outlook\.comPrimarySign Out$"
        if page.locator("div").filter(has_text=re.compile(fr"{o13}")).get_by_role("button").is_visible():
            page.locator("div").filter(has_text=re.compile(fr"{o13}")).get_by_role("button").click() 
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="Sign Out").click()
        else:
            pass

    # Once dealing with the above code that deals with only 1 account, now deal with 2nd account no matter what account it is
    try:
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Sign Out").click()
        page.wait_for_timeout(1000)
        logging.info("Signed out of 2nd account")
    except:
        pass

    # # Random choice to either remove or keep one of the reconnect accounts
    # random_n= random.choice([4,2])
    # reconnect_decision = random.choice([True, False])
    # if reconnect_decision == False:
    #     try:
    #         page.get_by_role("button").nth(random_n).click()
    #         page.wait_for_timeout(1000)
    #         page.get_by_role("button", name="Sign Out").click()
    #     except Exception as e: 
    #         logging.error(f"By tapping n={random_n}, error occured: {str(e)}")

    # if rutvik@bluemind is in reconnect, then reconnect
    if  page.locator("div").filter(has_text=re.compile(r"^rutvik@bluemind\.app$")).get_by_label("Reconnect").is_visible():   
        with page.expect_popup() as popup:
            page.locator("div").filter(has_text=re.compile(r"^rutvik@bluemind\.app$")).get_by_label("Reconnect").click()
        popup = popup.value
        utils.google(popup, google_account, google_password)
        logging.info("Reconnected to Google")
    else:
        with page.expect_popup() as popup:
            page.get_by_label("Reconnect").click()
        popup = popup.value
        utils.google(popup, google_account, google_password)
        logging.info("Reconnected to Google")
   
   # If outlook is still in reconnect, then reconnect
    if page.locator("div").filter(has_text=re.compile(r"^rutvikqatest@outlook\.com$")).get_by_label("Reconnect").is_visible(): 
        page.locator("div").filter(has_text=re.compile(r"^rutvikqatest@outlook\.com$")).get_by_label("Reconnect").click()
        utils.outlook(page, outlook_account, outlook_password)
        logging.info("Reconnected to Outlook")

    else:
        with page.expect_popup() as popup:
            page.get_by_label("Reconnect").click()
        popup = popup.value
        utils.outlook(page, outlook_account, outlook_password)
        logging.info("Reconnected to Outlook")
    
    # If gmail is not connected, then connect gmail
    if page.get_by_role("button", name="Connect Gmail").is_visible():   
        with page.expect_popup() as popup_info:
            page.get_by_role("button", name="Connect Gmail").click()
        popup = popup_info.value
        utils.google(popup, google_account, google_password)
        logging.info("Connected to Google")
        page.wait_for_timeout(5000)
    else:
        pass
    
    # If outlook is not connected, then connect outlook
    if page.get_by_role("button", name="Connect Outlook").is_visible():
        utils.outlook(page, outlook_account, outlook_password)
        logging.info("Connected to Outlook")

    else:
        pass

    page.wait_for_timeout(2000)

    # Change primary account
    page.locator('div.account-email:has(p.select-primary-pill:has-text("Make it primary")) h4').hover()
    try:
        page.locator('p.select-primary-pill:has-text("Make it primary")').click()
        logging.info("Switched primary account")
    except Exception as e:
        logging.error(f"Error occured in switching primary account: {str(e)}")

    page.wait_for_timeout(2000)

    # After all these, decide to log out or not for both accounts
    decision = random.choice([True, False])
    logging.info(f"Decision to log out: {decision}")

    if decision:
        #Try to find the primary and sign out of it
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

        # Signs out of the 2nd account if the decision is True
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