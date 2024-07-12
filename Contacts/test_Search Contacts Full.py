
#This script requires handling of company name after the bug is fixed

from playwright.sync_api import sync_playwright
import time
import os
import logging
import random
import json
from dotenv import load_dotenv
import re
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

def select_random_name(page):
    # Wait for elements to appear
    page.wait_for_selector('b.text-blue.text-underline')

    # Get all matching elements &  randomly select an element
    elements = page.locator('b.text-blue.text-underline').all()
    random_element = random.choice(elements)

    # Get inner text of the selected element
    inner_text = random_element.inner_text()
    real_name = inner_text

    # Randomize capitalization
    inner_text = ''.join(random.choice([c.lower(), c.upper()]) for c in inner_text)

    # Add random spaces before and after the text
    num_spaces_before = random.randint(0, 4)
    num_spaces_after = random.randint(0, 4)
    inner_text = ' ' * num_spaces_before + inner_text + ' ' * num_spaces_after
    return inner_text, real_name

api_pattern = re.compile(r'^https://staging-api\.bluemind\.app/api/client/get_all')

# Experimental
# Function to replace middle spaces with '+' and remove parentheses
def replace_middle_spaces(name):
    # Remove any parentheses
    name = name.replace('(', '').replace(')', '')
    # Use a regular expression to replace only spaces between non-space characters
    replaced_name = re.sub(r'(?<=\S) +(?=\S)', '+', name.strip())
    return replaced_name

# Works for sure
# def replace_middle_spaces(name):
#     # Use a regular expression to replace only spaces between non-space characters
#     replaced_name = re.sub(r'(?<=\S) +(?=\S)', '+', name.strip())
#     return replaced_name


# Func to handle intercepted requests
def handle_request(request):
    # Check if the intercepted request matches your API endpoint
    if request.method == 'GET' and api_pattern.match(request.url):
        return True
    else:
        return False

# Func to handle API resp and search actions
def verify_URLs(page, search_name, real_name):
    # Attach request event listener
    request_handler = lambda request: handle_request(request)
    
    page.wait_for_timeout(5000)
    # Fill search input and perform search
    page.on('request', request_handler)
    page.locator('[placeholder="Search"]').fill(search_name)
  
    # Wait for a single response event
    response_event = page.wait_for_event('response')

    # Handle the response event
    response = response_event
    page.remove_listener("request", request_handler)
    # CHeck the URL has name or not
    expected = replace_middle_spaces(real_name).lower()

    
    if api_pattern.match(response.url) and response.request.resource_type == 'fetch' or response.request.resource_type == 'xhr':
        if expected in response.url.lower():
            logging.info(f"API URL contains expected name: {expected}")
        else:
            logging.warning(f"API URL does not contain expected name: {expected}")
    else:
        logging.warning(f"API URL is a random one {response.url}")

    #Check the URL and its response
    try:
        if response:
            if response.status == 200 and response.request.resource_type == 'fetch' or response.request.resource_type == 'xhr':
                # Check if the response URL matches your API endpoint
                if api_pattern.match(response.url) and response.request.resource_type == 'fetch' or response.request.resource_type == 'xhr':
                    response_body =  response.text()
                    response_data = json.loads(response_body)

                    # Process the response and extract data from it to verify with the search input
                    if response_data['status'] == 'ok' and 'data' in response_data:
                        for client in response_data['data']:
                            first_name = client['ContactInfo']['first_name']
                            last_name = client['ContactInfo']['last_name']
                            company_name = client.get('company_name', '')  # Check if company_name exists

                            logging.info(f"First Name: {first_name}, Last Name: {last_name}, Company Name: {company_name}")
            else:
                logging.info(f"Intercepted request method: {response.request.method}")
                logging.info(f"Intercepted request url: {response.request.url}")
                logging.info(f"Intercepted request response status: {response.status}")

                response_body =  response.text()
                if response_body:
                    logging.info(f"Intercepted request response body: {response_body}")
                else:
                    logging.info("Empty response body")

        else:
            logging.warning("No response received within the expected time frame.")

    except json.JSONDecodeError as json_err:
        logging.error(f"Error decoding JSON response: {json_err}")
    except Exception as e:
        logging.error(f"Error handling intercepted response: {e}")
    page.wait_for_timeout(4000)
    page.get_by_placeholder("Search").fill("")
    page.wait_for_timeout(3000)

# Function to search and process API response
def search(page):
    # Navigate to the page and perform actions
    page.goto("https://staging.bluemind.app/contacts")
    page.wait_for_timeout(2000)

    # Select a random name and perform search
    search_name, real_name = select_random_name(page)
    logging.info(f"Randomized name for search: {search_name}")

    verify_URLs(page, search_name, real_name)
    page.get_by_text("Prospects").click()
    logging.info("Prospects comparison below")
    page.wait_for_timeout(4000)
    search_name1, real_name1 = select_random_name(page)
    verify_URLs(page, search_name1, real_name1)

    page.get_by_text("Clients").click()
    page.wait_for_timeout(4000)
    logging.info("Clients comparison below")
    search_name2, real_name2 = select_random_name(page)
    verify_URLs(page, search_name2, real_name2)


    page.get_by_text("All Contacts").click()
    page.wait_for_timeout(4000)
    logging.info("All Contacts comparison below")
    search_name3, real_name3 = select_random_name(page)
    verify_URLs(page, search_name3, real_name3)

    page.wait_for_timeout(4000)

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        search(page)
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
