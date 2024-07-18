# utils.py
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytest
import string
import random
import logging
import time
import re
import requests
from collections import defaultdict
import time
import re
from bs4 import BeautifulSoup
import traceback
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page
from playwright.async_api import async_playwright, Page

# Function to retrieve environment variables
def get_env_variables():
    """Retrieve environment variables"""
    password = os.getenv('PASS')
    url_1 = os.getenv('URL')
    username = os.getenv('USER')
    logs_folder = os.getenv('LOGS')
    auth=os.getenv('AUTH')
    google_account= os.getenv('G_A')
    google_password= os.getenv('G_P')   
    outlook_account= os.getenv('O_A')
    outlook_password= os.getenv('O_P')
    outlook_account2= os.getenv('O_A2')
    api_url = os.getenv('URL_API')
    url_contacts = os.getenv('URL_CONTACTS')    
    login_api = os.getenv('LOGIN_API')
    mailinator= os.getenv('MAILINATOR')
    token= os.getenv('TOKEN')
    signup = os.getenv('SIGNUP_API')

    return (password, url_1, username, logs_folder, auth, google_account, google_password, 
        outlook_account, outlook_password, outlook_account2, api_url, url_contacts, login_api, mailinator, token, signup)

# Define the path to the login script and the state file
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '../Variables/Login session script.py')   
STATE_PATH = os.path.join(os.path.dirname(__file__), 'variables/playwright/.auth/state.json')

# Function to define the path to the login script and the state file
def paths():
    # Define the path to the login script and the state file
    script_path = os.path.join(os.path.dirname(__file__), '../Variables/Login session script.py')
    state_path = os.path.join(os.path.dirname(__file__), 'variables/playwright/.auth/state.json')
    return script_path, state_path

# Function to load environment variables from .env files
def load_env_files():
    """Load environment variables from .env files"""
    load_dotenv(dotenv_path='variables/Variables.env')
    load_dotenv(dotenv_path='variables/API_responses.env')
    load_dotenv(dotenv_path='variables/API.env')

# Function to press arrow down for random number of times
def for_x_y(page, x, y):
    x=int(x)
    y=int(y)    
    for _ in range(random.randint(x, y)):
        page.keyboard.press("ArrowDown")
    page.wait_for_timeout(500)
    page.keyboard.press("Enter")

# Function to press arrow up for random number of times
def anti_for_x_y(page, x, y):
    x=int(x)
    y=int(y)    
    for _ in range(random.randint(x, y)):
        page.keyboard.press("ArrowUp")
    page.wait_for_timeout(500)
    page.keyboard.press("Enter")

# Function to setup logging for the scripts
def logging_setup(script_name):
    logs_folder = get_env_variables()[3]
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    log_file_path = os.path.join(logs_folder, f'{script_name}.log')
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to check if the login state file is recent
def is_recent_state(path=STATE_PATH, hours=8):
    """Check if the login state file is recent"""
    if not os.path.exists(path):
        return False
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.now() - file_mod_time < timedelta(hours=hours)

# Funtion to tap a random view contact sidebar button
def tap_random_view_contact(page):
    view_contact_buttons = page.locator('[aria-label="View contact"]')
    count = view_contact_buttons.count()
    if count > 0:
        random_index = random.randint(0, count - 1)
        view_contact_buttons.nth(random_index).click()

        # Ensure we find the correct contact name element
        contact_name_element = page.locator('.bm-contact-name').first
        if contact_name_element.is_visible():
            contact_name = contact_name_element.inner_text()

            # Remove the last word from contact_name
            contact_name_words = contact_name.split()
            if len(contact_name_words) > 1:
                contact_name = ' '.join(contact_name_words[:-1])

            # Backspace twice
            contact_name = contact_name[:-2]

            # Log the modified contact_name
            logging.info(f"------------------->Viewing sidebar for contact name: {contact_name}")
    else:
        logging.info("No sidebar view contact buttons found") 

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

# Clear field input
def remove_field_input(page):
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")

# Def for Random characters ABC...
def generate_random_alphabet(length):
    characters = string.ascii_letters
    return ''.join(random.choice(characters) for _ in range(length))

# Def for Random characters 123ABC!@# and space
def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation + ' '
    return ''.join(random.choice(characters) for _ in range(length))

# Function to generate random numbers 123...
def generate_random_numbers(length):
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Function to generate ABC123...
def generate_alphanumeric(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Function to select random priority
def random_prio(page, exclude_priority: str):

    names = ["! Low", "! Medium", "! High"]
    # Exclude the specified priority
    names = [name for name in names if name != exclude_priority]
    
    if not names:
        logging.info("No priorities available to select from after exclusion.")
        return
    random_name = random.choice(names)
    page.get_by_role("menuitem", name=random_name).click()
    page.wait_for_timeout(2000) 

# Function to find random button
def find_random_button(page, role, name):
    # Try to find the elements matching the given role and name
    elements = page.get_by_role(role, name=name)
    total_elements = elements.count()

    if total_elements == 0:
        logging.info(f"No elements found with role '{role}' and name '{name}'")
        return None
    
    logging.info(f"Found {total_elements} elements with role '{role}' and name '{name}'")
    
    # If at least one element exists, return a random one
    try:
        # Generate a random index between 0 and total_elements - 1
        random_index = random.randint(0, total_elements - 1)
        if random_index == 0:
            random_element = elements.first
            logging.info(f"Selected element at position {random_index+1}")
        else:    
            random_element = elements.nth(random_index)
            logging.info(f"Selected element at position {random_index+1}")
        return random_element
    except Exception as e:
        logging.info(f"Error occurred: {e}")
        return None

# Function to add reminder
def add_reminder(page, random_choice):
    page.keyboard.press("Tab")
    page.get_by_role("button", name="Add Reminder").click()
    page.get_by_role("combobox").nth(2).click()
    for_x_y(page, "1", "2") 
    page.keyboard.press("Tab")
    if random_choice == "Yes":
        for _ in range(random.randint(1, 10)):
            page.keyboard.press("ArrowDown")
    else:
        for _ in range(random.randint(1, 100)):
            page.keyboard.press("ArrowUp")
    page.keyboard.press("Tab")
    for_x_y(page, "1", "4") 
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")

# Function to add to voice to text and save
def Voice_to_text(page):
    page.get_by_role("button", name="Start").click(timeout=2000)
    page.wait_for_timeout(3000)
    page.get_by_role("button", name="Stop").click(timeout=500)
    page.get_by_role("button", name="Reset").click(timeout=500)
    try:
        page.locator("textarea[name=\"notes\"]").fill(generate_random_string(100), timeout=1000)
    except:
        try:
            page.locator(".rich-text-editor-editor").fill(generate_random_string(100), timeout=1000)
        except:
            page.get_by_role("button", name="Reset").press("Shift+Tab")
            page.get_by_role("button", name="Start").press("Shift+Tab")
            page.keyboard.type(generate_random_string(100), delay=0)
    try:
        page.get_by_role("button", name="Save").click()
    except:
        try:
            page.get_by_role("button", name="Send").click(timeout=500)
        except:
            page.get_by_role("button", name="Update").click(timeout=500)
    logging.info("Saved after voice to text success")

# Function to select random priority
def select_random_priority(page):
    choices = ["Low", "Medium", "High"]
    random.shuffle(choices)  # Shuffle the list to randomize the order

    for random_choice in choices:
        try:
            random_priority = find_random_button(page, "button", f"! {random_choice}")
            if random_priority:
                return random_priority, random_choice
        except Exception as e:
            logging.info(f"Error occurred while finding random button for '{random_choice}': {e}")

    logging.info("Failed to find any elements for all priorities")
    return None, None  # Handle the case where no elements were found


# Function to fetch required API requests
def handle_request2(self, request, api_urls):
    if request.method in ["PUT", "POST", "GET", "DELETE"] and request.resource_type in ["fetch", "xhr"]:
        logging.info(f"Request URL: {request.url}")
        api_urls.append(request.url)

# Pattern matching for single / multiple API requests
def handle_request1(self, request, api_urls, api_patterns):
    # Ensure api_patterns is a list
    if not isinstance(api_patterns, list):
        api_patterns = [api_patterns]
    
    for pattern in api_patterns:
        if pattern.match(request.url):
            api_urls.append({'URL': request.url})


# Function to handle failed requests if fails
def handle_response_failure(self, response):
    if response.status != 200:
        logging.info(f"Request failed: {response.url} - Status: {response.status}")
        
# Function to handle failed requests for matching api urls if fails
def handle_response_failure1(self, response, api_urls, api_pattern):

    if api_pattern.match(response.url) and response.status != 200:
        for api_url in api_urls:
            if api_url['url'] == response.url:
                api_url['response'] = response
                break
        logging.error(f"Request failed: {response.url} - Status: {response.status}")

# # Function to handle request and log URL
# def handle_request(request, api_urls):
#     api_url = os.getenv('URL_API')
#     api_pattern = re.compile(fr'^{re.escape(api_url)}')
#     if request.method in ["PUT", "POST", "GET", "DELETE"] and request.resource_type in ["fetch", "xhr"] and api_pattern.match(request.url):
#         # logging.info(f"Request URL: {request.url}")
#         payload = request.post_data if request.method in ["PUT", "POST"] else None
#         api_urls.append({'url': request.url, 'response': None, 'payload': payload})

# # Function to handle response, log status and data
# def handle_response(response, api_urls):
#     api_url = os.getenv('URL_API')
#     api_pattern = re.compile(fr'^{re.escape(api_url)}')
#     if response.request.method in ["PUT", "POST", "GET", "DELETE"] and response.request.resource_type in ["fetch", "xhr"] and api_pattern.match(response.url):
#         for api_url in api_urls:
#             if api_url['url'] == response.url:
#                 api_url['response'] = response
#                 break
#         # logging.info(f"Response URL: {response.url} - Status: {response.status} Response Data: {response.json() if 'application/json' in response.headers['content-type'] else response.text()}")

# # Function to show API response
# def show_api_response(api_urls):
#     for url_info in api_urls:

#         response_status = url_info['response'].status if url_info['response'] else 'No response'
#         response_data = (url_info['response'].json() if url_info['response'] and 'application/json' in url_info['response'].headers['content-type'] 
#                          else (url_info['response'].text() if url_info['response'] else 'No response data'))
#         request_payload = url_info.get('payload', 'No payload')

#         if url_info['response'] and url_info['response'].ok:
#             logging.info(f"URL: {url_info['url']}, Status: {response_status}\n")
#         elif url_info['response'] and not url_info['response'].ok:
#             logging.info(f"URL: {url_info['url']}, Status: {response_status}, Payload: {request_payload}, Data: {response_data}\n")
#         else:
#             logging.info(f"URL: {url_info['url']}, Status: {response_status}, Payload: {request_payload}, Data: {response_data}\n")

# Function to handle request and log URL
def handle_request(request, api_urls):
    api_url = os.getenv('URL_API')
    api_pattern = re.compile(fr'^{re.escape(api_url)}')
    if request.method in ["PUT", "POST", "GET", "DELETE"] and request.resource_type in ["fetch", "xhr"] and api_pattern.match(request.url):
        payload = request.post_data if request.method in ["PUT", "POST"] else None
        request_key = (request.url, request.method, payload)
        if request_key not in api_urls:
            api_urls[request_key] = {'response': None, 'payload': payload}

# Function to handle response, log status and data
def handle_response(response, api_urls):
    api_url = os.getenv('URL_API')
    api_pattern = re.compile(fr'^{re.escape(api_url)}')
    request_key = (response.url, response.request.method, response.request.post_data if response.request.method in ["PUT", "POST"] else None)
    if response.request.method in ["PUT", "POST", "GET", "DELETE"] and response.request.resource_type in ["fetch", "xhr"] and api_pattern.match(response.url):
        if request_key in api_urls:
            api_urls[request_key]['response'] = response

# Function to show API response
def show_api_response(api_urls):
    for key, info in api_urls.items():
        url, method, payload = key
        response = info['response']
        response_status = response.status if response else 'No response'
        response_data = (response.json() if response and 'application/json' in response.headers['content-type'] 
                         else (response.text() if response else 'No response data'))
        if response and response.ok:
            logging.info(f"URL: {url}, Method: {method}, Status: {response_status}\n")
        elif response and not response.ok:
            logging.info(f"URL: {url}, Method: {method}, Status: {response_status}, \n-------------------> Payload: {payload}, \n-------------------> Data: {response_data}\n") 
        else:
            logging.info(f"URL: {url}, Method: {method}, Status: {response_status}, \n-------------------> Payload: {payload}, \n-------------------> Data: {response_data}\n") 



def start_handler(page, api_urls):
    response_handler = lambda response: handle_response(response, api_urls)
    request_handler = lambda request: handle_request(request, api_urls)
    page.on('request', request_handler)
    page.on('response', response_handler)
    return response_handler, request_handler

def stop_handler(page, api_urls, response_handler, request_handler):
    page.wait_for_timeout(8000)
    page.remove_listener("request", request_handler)
    page.remove_listener("response", response_handler)
    show_api_response(api_urls)

def scroll_to_find(page):
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.evaluate("window.scrollTo(0, 0)")

# Function to find latest file from type defined and 5mb max size
def find_latest_upload(file_type, max_size_mb=5):
    directory = r'C:\Users\Rutvik\Downloads'
    # List all files in the directory
    files = os.listdir(directory)
    # Filter files to only include files with the specified type
    filtered_files = [file for file in files if file.endswith(f'.{file_type}')]
    # Sort files by creation time (descending)
    filtered_files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)), reverse=True)
    
    # Check each file in descending order of creation time
    for file in filtered_files:
        file_path = os.path.join(directory, file)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb <= max_size_mb:
            return file_path
    # Return None if no file is found that meets the criteria
    return None

# Upload Random Files
def upload_random_files(max_files):
    # file_types = ["pdf", "xlsx", "har", "jpg", "png", "csv", "svg", "jfif", "webm", "mp4", "mp3"]
    file_types= ["xlsx"]
    selected_files = []
    
    # Shuffle the list of file types
    random.shuffle(file_types)
    
    for _ in range(max_files):
        if not file_types:
            break
        
        type1 = file_types.pop()
        latest_file = find_latest_upload(type1)
        
        if latest_file:
            selected_files.append(latest_file)
    
    return selected_files

# Function to find latest INSURANCE policy file
def find_latest_policy():
    directory = r'C:\Users\Rutvik\Downloads'
    # List all files in the directory
    files = os.listdir(directory)
    # Filter files to only include text files with 'contact-policy' in the name
    policy_files = [file for file in files if file.endswith('.xlsx') and ('contact-policy' in file)]
    # Sort files by creation time (descending)
    policy_files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)), reverse=True)
    # Return the latest file (n) if found
    if policy_files:
        return os.path.join(directory, policy_files[0])
    else:
        return None

# Function to find the latest contact upload file
def find_latest_contact_upload():

    directory = r'C:\Users\Rutvik\Downloads'
    # List all files in the directory
    files = os.listdir(directory)
    # Filter files to only include text files with 'xlsx' & 'sample contacts' in the name 
    policy_files = [file for file in files if file.endswith('.xlsx') and ('Sample-Contacts' in file)]
    # Sort files by creation time (descending)
    policy_files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)), reverse=True)
    # Return the latest file (n) if found
    if policy_files:
        return os.path.join(directory, policy_files[0])
    else:
        return None


# Function to find latest INVESTMENT policy file
def find_latest_invest_policy():
    directory = r'C:\Users\Rutvik\Downloads'
    # List all files in the directory
    files = os.listdir(directory)
    # Filter files to only include text files with 'investment-policy' in the name
    policy_files = [file for file in files if file.endswith('.xlsx') and ('investment-policy' in file)]
    # Sort files by creation time (descending)
    policy_files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)), reverse=True)
    # Return the latest file (n) if found
    if policy_files:
        return os.path.join(directory, policy_files[0])
    else:
        return None

# Function to click on calendar and its items
def click_calendar(page):
    tomorrow = datetime.today() + timedelta(days=1)
    day_str = tomorrow.strftime('%d')
    page.wait_for_timeout(1000) 
    try:
        page.get_by_role("gridcell", name=day_str, exact=True).click(timeout=2000)
    except:
            try:
                page.get_by_role("gridcell", name=day_str).click(timeout=2000)
            except:
                page.get_by_label("Next month").click()
                page.wait_for_timeout(500)
                page.get_by_role("gridcell", name="1", exact=True).click() 
                page.wait_for_timeout(500)

# Phone Number
def phone_number():
    random_digits = ''.join(random.choices(string.digits, k=10))
    fill = f"+1 ({random_digits[:3]}) {random_digits[3:6]}-{random_digits[6:]}"
    return fill

# Coin Toss Random Yes/No
def coin_toss():
    return random.choice(["Heads", "Tails"])

# Random Priority
def priority_random(): 
    choices = ["Low", "Medium", "High"]
    a = random.choice(choices)  
    return a

# Random Category
def category_random():
    choices = ["Follow Ups", "Sales", "Events"]
    a = random.choice(choices)  
    return a

# Report PASS
def start_report(test_results, script_name):
    # Append script result with current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_results.append(f"{current_time} - {script_name}: PASS")  

    # # Generating report content
    # report_content = "\n".join(test_results)

    # # Writing report content to a log file
    # with open("test_report.txt", "a") as f:
    #     f.write(report_content + "\n")
    
    # Generating report content
    report_content = "\n".join(test_results)

    # Determine the path to the report file in the "Run Scripts" folder
    run_scripts_folder = r'C:\Users\RutviK\Python PlaywrightScripts\Run Scripts'
    report_file = os.path.join(run_scripts_folder, "test_report.txt")

    # Writing report content to the log file
    with open(report_file, "a") as f:
        f.write(report_content + "\n")

# Traceback error logging
def traceback_error_logging(script_name, e):
    tb = e.__traceback__
    full_traceback = traceback.extract_tb(tb)
    for filename, lineno, funcname, line in full_traceback:
        logging.info(f"File '{filename}', line {lineno}, in {funcname}: {line.strip()}")
    logging.info(f"Error in {script_name}: {e}")

# Report FAIL
def end_report(test_results, script_name):
    # Append script result with current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_results.append(f"{current_time} - {script_name}: FAIL")  

    # Generating report content
    report_content = "\n".join(test_results)

    # Determine the path to the report file in the "Run Scripts" folder
    run_scripts_folder = r'C:\Users\RutviK\Python PlaywrightScripts\Run Scripts'
    report_file = os.path.join(run_scripts_folder, "test_report.txt")

    # Writing report content to the log file
    with open(report_file, "a") as f:
        f.write(report_content + "\n")



# Fetch OTP from mailinator
def fetch_otp(mailinator, token):
    
    response = requests.get(mailinator)
    if response.status_code == 200:
        data = response.json()
        latest_message = data['msgs'][0]
        message_id = latest_message['id']
        message_url = f"https://api.mailinator.com/api/v2/domains/private/messages/{message_id}?{token}"
        message_response = requests.get(message_url)
        if message_response.status_code == 200:
            message_data = message_response.json()
            message_body = message_data['parts'][0]['body']
            otp_match = re.search(r"\b\d{6}\b", message_body)
            if otp_match:
                return otp_match.group()
            else:
                print("Failed to fetch OTP.")
                return None
        else:
            print(f"Failed to fetch message details: {message_response.status_code}")
            return None
    else:
        print(f"Failed to fetch message summaries: {response.status_code}")
        return None



# Verification Mailinator
async def fetch_and_click_verification_link(mailinator_url, token):

    response = requests.get(mailinator_url)
    if response.status_code == 200:
        data = response.json()
        top_two_messages = data['msgs'][:2]

        for message in top_two_messages:
            subject = message.get('subject', '')
            if subject == "Welcome to BlueMind":
                continue

            message_id = message['id']
            message_url = f"https://api.mailinator.com/api/v2/domains/private/messages/{message_id}?{token}"
            message_response = requests.get(message_url)

            if message_response.status_code == 200:
                message_data = message_response.json()
                message_html = message_data['parts'][0]['body']
                soup = BeautifulSoup(message_html, 'html.parser')
                verify_link = soup.find('a', string='Verify Account')

                if verify_link:
                    verify_url = verify_link['href']

                    async with async_playwright() as p:
                        browser = await p.chromium.launch(headless=True)
                        page = await browser.new_page()
                        await page.goto(verify_url)
                        page.wait_for_timeout(5000)
                        await browser.close()
                    break
                else:
                    logging.info("No 'Verify Account' link found in the email.")
                    break
        else:
            logging.info("No relevant emails found with verification links.")
    else:
        logging.info(f"Failed to fetch message summaries: {response.status_code}")

#outlook singin
def outlook(page, outlook_account, outlook_password):
    page.wait_for_timeout(1000)
    page.get_by_label("Enter your email, phone, or").fill(outlook_account)
    page.wait_for_timeout(1000)
    page.get_by_label("Enter your email, phone, or").press("Enter")
    page.wait_for_timeout(1000)
    page.get_by_test_id("i0118").fill(outlook_password)
    page.wait_for_timeout(1000)
    page.get_by_test_id("i0118").press("Enter")
    page.wait_for_timeout(1000)
    page.get_by_label("Stay signed in?").click()
    page.wait_for_timeout(5000)

# Google singin
def google(popup, google_account, google_password):
    popup.fill('input[type="email"]', google_account)  
    popup.locator('#identifierNext >> button').click()
    popup.fill('#password >> input[type="password"]', google_password)
    popup.locator('button >> nth=1').click()
    popup.get_by_role("button", name="Continue").click()
    try:
        popup.get_by_role("button", name="Continue").click()
    except:
        popup.get_by_text("Select all").click()
        popup.wait_for_timeout(1000)
        popup.get_by_role("button", name="Continue").click()

# Intercept API and replace requests
#intercepted_request = None
#url_to_intercept= "https://staging-api.bluemind.app/api/..."
def intercept_api_requests(route, request, url_to_intercept):
    global intercepted_request
    if request.url == url_to_intercept and request.method == 'POST':
        intercepted_request = request
        route.fulfill(
            # Replace intercepted request with the below response
            status=200,
            body='{"status": "ok", "data": null}',
            headers={'Content-Type': 'application/json'}
        )
    else:
        route.continue_()

# Move to ( Move contact to lead, prospect, client randomly) Curated for contacts side bar
def move_to_random(page):

    page.get_by_role("button", name="Move To").click()
    options = ["Prospect", "Client", "Lead"]
    available_options = []

    # Check visibility of each option and collect visible ones
    for option in options:
        try:
            role_menuitem = page.get_by_role("menuitem", name=option)
            if role_menuitem.is_visible():
                available_options.append(option)
        except:
            pass

    # If there are visible options, randomly click on one
    if available_options:
        random_option = random.choice(available_options)
        page.get_by_role("menuitem", name=random_option).click()
        logging.info(f"Clicked on '{random_option}' in move to contact")
    else:
        print("No visible options found")
    x=coin_toss() 
    if x == "Heads":
        page.get_by_role("button", name="Yes, Move it!").click()
        page.wait_for_timeout(3000) 
        if page.get_by_role("alert").is_visible():
            try:
                assert page.get_by_text("Contact moved successfully!").is_visible()
                logging.info("Contact moved successfully!")
                page.get_by_label("Close").click()

            except:
                logging.info(f"Failed to move contact to {random_option}")
                page.get_by_label("Close").click()
        else:
            logging.info(f"No alert msgs on moving contact to {random_option}") 
    else:
        page.get_by_role("button", name="No").click()
        logging.info(f"Decided not to move contact to {random_option} through toss")
