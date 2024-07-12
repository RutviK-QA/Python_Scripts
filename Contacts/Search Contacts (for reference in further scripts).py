from playwright.sync_api import sync_playwright
import time
import os
import logging
import random
import json
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv(dotenv_path='variables/Variables.env')
load_dotenv(dotenv_path='variables/API_responses.env')

password = os.getenv('PASS')
url = os.getenv('URL')
username = os.getenv('USER')
logs_folder = os.getenv('LOGS')

# Setup logging
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)
log_file_path = os.path.join(logs_folder, 'Search_Contacts.txt')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')


# Function to select a random name for search
def select_random_name(page):
    # Wait for elements to appear (using your specific selector)
    page.wait_for_selector('b.text-blue.text-underline')

    # Get all matching elements
    elements = page.locator('b.text-blue.text-underline').all()

    # Randomly select an element
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
google_analytics_pattern = re.compile(r'https://analytics\.google\.com/g/collect')

def replace_middle_spaces(name):
    # Use a regular expression to replace only spaces between non-space characters
    replaced_name = re.sub(r'(?<=\S) +(?=\S)', '+', name.strip())
    return replaced_name


# Function to handle intercepted requests
def handle_request(request):
    # Check if the intercepted request matches your API endpoint
    if request.method == 'GET' and api_pattern.match(request.url):
        return True
    else:
        return False

# Function to search and process API response
def search(page):
    # Navigate to the page and perform actions
    page.goto("https://staging.bluemind.app/contacts")
    time.sleep(2)

    # Perform login actions if required
    if page.locator('[placeholder="Enter Email"]').is_visible():
        page.locator('[placeholder="Enter Email"]').fill(username)
        logging.info("Entered email")
        page.locator('[placeholder="Password"]').fill(password)
        page.keyboard.press("Enter")
        logging.info("Logged In")
        page.wait_for_navigation()
    else:
        pass

    # Select a random name and perform search
    search_name, real_name = select_random_name(page)
    logging.info(f"Randomized name for search: {search_name}")

    # Attach request event listener
    request_handler = lambda request: handle_request(request)
    
    page.wait_for_load_state('networkidle')
    time.sleep(5)
    # Fill search input and perform search
    page.on('request', request_handler)
    page.locator('[placeholder="Search"]').fill(search_name)
    time.sleep(3)  # Adjust as necessary for page to load and API to respond

    # Wait for a single response event
    response_event = page.wait_for_event('response')

    # Handle the response event
    response = response_event
    page.remove_listener("request", request_handler)

    #CHeck the URL has name or not
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

                    # Process the response data accordingly
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

    time.sleep(4)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})
    search(page)
    browser.close()
