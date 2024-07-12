from dotenv import load_dotenv
import logging
import requests
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


def Contacts(page: Page) -> None:
    page.goto("https://staging.bluemind.app/contacts")
    page.wait_for_timeout(5000)
    if page.get_by_placeholder("Enter Email").is_visible():
        page.get_by_placeholder("Enter Email").fill(username)
        logging.info("Entered email")
        page.get_by_placeholder("Password").fill(password)
        page.get_by_placeholder("Password").press("Enter")
        logging.info("Logged In")
        page.goto("https://staging.bluemind.app/contacts")
        
    else:
        pass
    page.wait_for_timeout(5000)
    
    # Click Lead priority filters and reset
    try:
        page.get_by_text("High", exact=True).click()
        page.get_by_text("Medium").click()
        page.get_by_test_id("RefreshIcon").nth(1).click()
    except Exception as e:
        logging.error(f"Error clicking lead priority filters: {e}")

    try:
        page.get_by_text("This week").click()
        page.get_by_text("This month").click()
        page.get_by_test_id("RefreshIcon").nth(1).click()
    except Exception as e:
        logging.error(f"Error clicking lead filters: {e}")

    try:
        page.get_by_text("New", exact=True).first.click()
        page.get_by_text("Contacted").first.click()
        page.get_by_text("No Response").first.click()
        page.get_by_text("Nurture").first.click()
        page.get_by_test_id("RefreshIcon").click()
    except Exception as e:
        logging.error(f"Error clicking status filters: {e}")
    logging.info("Leads Passed")

    page.wait_for_timeout(5000)

    # Click on "Prospects" element
    try:
        page.get_by_text("Prospects").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Prospects' element: {e}")

    try:
        page.get_by_text("This week").click()
        page.wait_for_timeout(5000)
        page.get_by_text("This month").click()
        page.wait_for_timeout(5000)
        page.get_by_test_id("RefreshIcon").nth(1).click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking week and month elements: {e}")

    try:
        page.get_by_text("High", exact=True).click()
        page.wait_for_timeout(5000)
        page.get_by_text("Medium").click()
        page.wait_for_timeout(5000)
        page.get_by_test_id("RefreshIcon").nth(1).click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking high and medium elements: {e}")

    try:
        page.locator('.title:has-text("New")').click()
        page.wait_for_timeout(5000)
        page.get_by_text("Follow Up").click()
        page.wait_for_timeout(5000)
        page.get_by_text("Sales").click()
        page.wait_for_timeout(5000)
        page.get_by_text("Fact Finding").click()
        page.wait_for_timeout(5000)
        page.get_by_text("Planning").click()
        page.wait_for_timeout(5000)
        page.get_by_text("Proposal Sent").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking New/Follow up/Sales/etc elements: {e}")
    logging.info("Prosp Passed")


    # Click on "Clients" element
    try:
        page.get_by_text("Clients").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Clients' element: {e}")

    try:
        page.get_by_text("This week").click()
        page.wait_for_timeout(5000)

    except Exception as e:
        logging.error(f"Error clicking 'This week' element: {e}")

    try:
        page.get_by_text("This month").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'This month' element: {e}")

    try:
        page.get_by_test_id("RefreshIcon").nth(1).click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Refresh' icon: {e}")

    for letter in ["A", "C", "B", "D"]:
        try:
            page.get_by_text(letter, exact=True).click()
            page.wait_for_timeout(5000)
        except Exception as e:
            logging.error(f"Error clicking element '{letter}': {e}")
    logging.info("Clients Passed")

    page.wait_for_timeout(5000)

    # test all contacts buttons
    try:
        page.get_by_text("All Contacts").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Refresh' icon: {e}")
    
    try:
        page.get_by_text("This week").click()
        page.wait_for_timeout(5000)
        page.get_by_text("This month").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Refresh' icon: {e}")

    try:
        page.get_by_text("This week").click()
        page.wait_for_timeout(5000)
        page.get_by_text("This month").click()
        page.wait_for_timeout(5000)
        page.get_by_test_id("RefreshIcon").nth(1).click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Refresh' icon: {e}")

    try:
        page.get_by_text("High", exact=True).first.click()
        page.wait_for_timeout(5000)
        page.get_by_text("Medium").first.click()
        page.wait_for_timeout(5000)
        page.get_by_test_id("RefreshIcon").nth(1).click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Refresh' icon: {e}")

    try:
        page.get_by_text("High", exact=True).nth(1).click()
        page.wait_for_timeout(5000)
        page.get_by_text("Medium").nth(1).click()
        page.wait_for_timeout(5000)
        page.get_by_test_id("RefreshIcon").nth(1).click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Refresh' icon: {e}")
    
    try:
        page.get_by_text("High", exact=True).nth(2).click()
        page.wait_for_timeout(5000)
        page.get_by_text("Medium").nth(2).click()
        page.wait_for_timeout(5000)
        page.get_by_test_id("RefreshIcon").nth(1).click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking 'Refresh' icon: {e}")

    try:
        page.get_by_text("Follow up").click()
        page.wait_for_timeout(5000)
        page.get_by_text("Call log").click()
        page.wait_for_timeout(5000)
        page.get_by_text("Appointment").click()
        page.wait_for_timeout(5000)
        page.locator("div").filter(has_text=re.compile(r"^FNA$")).click()
        page.wait_for_timeout(5000)
        page.get_by_test_id("RefreshIcon").click()
        page.wait_for_timeout(5000)
    except Exception as e:
        logging.error(f"Error clicking Followup/calllog/etc: {e}")
    logging.info("All Contacts Passed")

    headers = { 
        "Authorization": auth,
        "Origin": "https://staging.bluemind.app",
        "Content-Type": "application/json"
    }

    # #Call apis
    api_response_leads = requests.get(leads, headers=headers)
    api_response_prospects = requests.get(prospects, headers=headers)
    api_response_clients = requests.get(prospects, headers=headers)
    api_leads_all=requests.get(leads_all, headers=headers)
    api_clients_all=requests.get(clients_all, headers=headers)
    api_prospects_all=requests.get(prospects_all, headers=headers)


    #print errors or success (get all count)
    try:  
        if api_response_leads.status_code != 200:
            logging.info(f"Response Status Code: {api_response_leads.status_code}")
            logging.info(f"Response Content: {api_response_leads.text}")    
        if api_response_prospects.status_code != 200:
            logging.info(f"Response Status Code: {api_response_prospects.status_code}")
            logging.info(f"Response Content: {api_response_prospects.text}")
        if api_response_clients.status_code != 200:
            logging.info(f"Response Status Code: {api_response_clients.status_code}")
            logging.info(f"Response Content: {api_response_clients.text}")
    except:
        logging.info('ALL COUNT APIs PASSED')

    #print errors or success (get all clients)
    try:
        if api_prospects_all.status_code != 200:
            logging.info(f"Response Status Code: {api_prospects_all.status_code}")
            logging.info(f"Response Content: {api_prospects_all.text}")    
        if api_leads_all.status_code != 200:
            logging.info(f"Response Status Code: {api_leads_all.status_code}")
            logging.info(f"Response Content: {api_leads_all.text}")
        if api_clients_all.status_code != 200:
            logging.info(f"Response Status Code: {api_clients_all.status_code}")
            logging.info(f"Response Content: {api_clients_all.text}")
    except:
        logging.info('ALL CLIENT GET ALL APIs HAVE PASSED')

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

