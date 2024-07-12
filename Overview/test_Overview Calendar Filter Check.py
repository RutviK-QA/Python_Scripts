import re
import time 
import logging
import requests
from playwright.sync_api import Page, sync_playwright
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
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

def overview_filters(page: Page) -> None:
    page.goto("https://staging.bluemind.app/overview")
    page.wait_for_timeout(5000)
    today_1 = datetime.now()
    tomorrow_1 = today_1 + timedelta(days=1)

    # Format dates as strings with month without leading zero
    today_click = today_1.strftime("%B %d,")
    today_click = today_click.replace(" 0", " ")
    tomorrow_click = tomorrow_1.strftime("%B %d,")
    tomorrow_click = tomorrow_click.replace(" 0", " ")

    # Click on date buttons
    page.get_by_role("button", name=tomorrow_click).dblclick()
    page.wait_for_timeout(5000)
    page.get_by_role("button", name="Clear").click()
    page.get_by_role("button", name=today_click).dblclick()
    page.wait_for_timeout(5000)
    page.get_by_role("button", name="Clear").click()
    logging.info("Filters applied and cleared 2x")    
    
    # Calculate today's date and tomorrow's date in UTC
    today = datetime.utcnow()
    tomorrow = today + timedelta(days=1)
    
    # Format dates in GMT timezone
    today_str = today.strftime("%Y-%m-%dT18:30:00.000Z")
    tomorrow_str = tomorrow.strftime("%Y-%m-%dT18:29:59.999Z")

    # Adjust date ranges for today's API URL
    today_start_dt = (today - timedelta(days=1)).strftime("%Y-%m-%dT18:30:00.000Z")
    today_end = today_str



    # API URLs with adjusted date ranges
    today_api_url1 = f"https://staging-api.bluemind.app/api/client_tasks/upcoming_birth_anniversary?type=Active&sortBy=due_date&dateRange[]={today_start_dt}&dateRange[]={today_end}"
    tomorrow_api_url1 = f"https://staging-api.bluemind.app/api/client_tasks/upcoming_birth_anniversary?type=Active&sortBy=due_date&dateRange[]={today_str}&dateRange[]={tomorrow_str}"

    # API URLs with the adjusted date ranges
    today_api_url = f"https://staging-api.bluemind.app/api/client_tasks/get_all?type=Active&sortBy=due_date&dateRange[]={today_start_dt}&dateRange[]={today_end}"
    tomorrow_api_url = f"https://staging-api.bluemind.app/api/client_tasks/get_all?type=Active&sortBy=due_date&dateRange[]={today_str}&dateRange[]={tomorrow_str}"
    
    headers = {
        "Authorization": auth
        , "Access-Control-Allow-Origin": "https://staging.bluemind.app" 
    }

    def validate_data1(response_data, start_dt, end_dt, task_day):
        if not response_data.get('data'):
            logging.info("No data found in response for %s", task_day)
            return
        
        start_dt = datetime.strptime(start_dt, "%Y-%m-%dT%H:%M:%S.%fZ")
        end_dt = datetime.strptime(end_dt, "%Y-%m-%dT%H:%M:%S.%fZ")

        for entry in response_data.get('data', []):
            due_date = datetime.strptime(entry['due_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if start_dt <= due_date < end_dt:
                logging.info("Correct Data for %s in DOB API: %s", task_day, entry['task_id'])
            else:
                logging.error("Bug Found in DOB API: %s, due_date: %s, for %s", entry['task_id'], entry['due_date'], task_day)

    def validate_data(response_data, start_dt, end_dt, task_day):
        if not response_data.get('data'):
            logging.info("No data found in response for %s", task_day)
            return
        start_dt = datetime.strptime(start_dt, "%Y-%m-%dT%H:%M:%S.%fZ")
        end_dt = datetime.strptime(end_dt, "%Y-%m-%dT%H:%M:%S.%fZ")

        for entry in response_data.get('data', []):
            due_date = datetime.strptime(entry['due_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            entry_type = entry.get('type')
            
            if entry_type in ["Anniversary", "Birthday"]:
                continue  # Skip logging for entries with types "Anniversary" and "Birthday"

            if start_dt <= due_date < end_dt:
                logging.info("Correct Data for %s in Tasks API: %s", task_day, entry['task_id'])
            else:
                logging.error("Bug Found in Tasks API: %s, due_date: %s, for %s", entry['task_id'], entry['due_date'], task_day)



    # Make API call for today's data
    logging.info("Making API call for today's DOB tasks:")
    today_response1 = requests.get(today_api_url1, headers=headers)
    if today_response1.status_code == 200:
        today_data1 = today_response1.json()
        logging.info("DOB Today's API response: %s", today_data1)
        validate_data1(today_data1, today_start_dt, today_end, "Today")
    else:
        logging.error("Failed to fetch DOB today's API data. Status code: %s", today_response1.status_code)

    # Make API call for tomorrow's data
    logging.info("Making API call for tomorrow's DOB tasks:")
    tomorrow_response1 = requests.get(tomorrow_api_url1, headers=headers)
    if tomorrow_response1.status_code == 200:
        tomorrow_data1 = tomorrow_response1.json()
        logging.info("DOB Tomorrow's API response: %s", tomorrow_data1)
        validate_data1(tomorrow_data1, today_str, tomorrow_str, "Tomorrow")
    else:
        logging.error("Failed to fetch DOB tomorrow's API data. Status code: %s", tomorrow_response1.status_code)



    # Make API call for today's data
    logging.info("Making API call for today's tasks:")
    today_response = requests.get(today_api_url, headers=headers)
    if today_response.status_code == 200:
        today_data = today_response.json()
        logging.info("Task Today's API response: %s", today_data)       
        validate_data(today_data, today_start_dt, today_end, "Today")
    else:
        logging.error("Failed to fetch tasks for today. Status code: %s", today_response.status_code)

    # Make API call for tomorrow's data
    logging.info("Making API call for tomorrow's tasks:")
    tomorrow_response = requests.get(tomorrow_api_url, headers=headers)
    if tomorrow_response.status_code == 200:
        tomorrow_data = tomorrow_response.json()
        logging.info("Tasks Tomorrow's API response: %s", tomorrow_data)
        validate_data(tomorrow_data, today_str, tomorrow_str, "Tomorrow")
    else:
        logging.error("Failed to fetch tasks for tomorrow. Status code: %s", tomorrow_response.status_code)

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        overview_filters(page)
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


































# import re
# import time 
# import logging
# import requests
# from playwright.sync_api import Page, sync_playwright
# import os
# from datetime import datetime, timedelta

# # Configure logging to a file
# logs_folder = "C:/Users/Rutvik/Python PlaywrightScripts/Logs"
# if not os.path.exists(logs_folder):
#     os.makedirs(logs_folder)
# log_file_path = os.path.join(logs_folder, 'overview_filters.txt')
# logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# def overview_filters(page: Page) -> None:
#     page.goto("https://staging.bluemind.app/signin")
#     page.get_by_placeholder("Enter Email").fill("rutvik@rutvikqa.testinator.com")
#     logging.info("Entered email")
#     page.get_by_placeholder("Password").fill("Qa@12345678")
#     page.get_by_placeholder("Password").press("Enter")
#     logging.info("Logged In")

#     # Calculate today's date and tomorrow's date in UTC
#     today = datetime.utcnow()
#     tomorrow = today + timedelta(days=1)
    
#     # Format dates in GMT timezone
#     today_str = today.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
#     tomorrow_str = tomorrow.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

#     # Adjust date ranges for today's API URL
#     today_start_dt = (today - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
#     today_end = today_str

#     # API URLs with adjusted date ranges
#     today_api_url1 = f"https://staging-api.bluemind.app/api/client_tasks/upcoming_birth_anniversary/210?type=Active&sortBy=due_date&dateRange[]={today_start_dt}&dateRange[]={today_end}"
#     tomorrow_api_url1 = f"https://staging-api.bluemind.app/api/client_tasks/upcoming_birth_anniversary/210?type=Active&sortBy=due_date&dateRange[]={today_str}&dateRange[]={tomorrow_str}"

#     # Headers for API request (using a placeholder for the token)
#     headers = {
#         "Authorization": "eyJraWQiOiJRWW9ucnZjeEo2Sm1BT29xS0xXVENjUU5QeE1cL2hNMXhyMjlzbllJMXNFOD0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJiODM5ZDUxYy0wMDAzLTQzODktOTU2OS01NTRlYzc4MWYyNDAiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmNhLWNlbnRyYWwtMS5hbWF6b25hd3MuY29tXC9jYS1jZW50cmFsLTFfTDVkdERTQTNvIiwiY29nbml0bzp1c2VybmFtZSI6ImI4MzlkNTFjLTAwMDMtNDM4OS05NTY5LTU1NGVjNzgxZjI0MCIsImdpdmVuX25hbWUiOiJSIiwib3JpZ2luX2p0aSI6IjlmYTc0YTllLTdlYjctNGRiYy1iMmYyLWFmZTNmYWY0OGY5YSIsImF1ZCI6IjdkMm9mYXFvNXQyZXV0MzNnNmFiYTAxbW5yIiwiZXZlbnRfaWQiOiI3ZDcyMTBiMi0yZTE3LTQwYWUtOWRlZS1hNDJmMmRiNTBkYmYiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxNjk2MTYwMywiZXhwIjoxNzE2OTkwNDAzLCJpYXQiOjE3MTY5NjE2MDMsImZhbWlseV9uYW1lIjoiSyIsImp0aSI6ImM1ZDI1NTQwLTAxYjUtNDYxYi1hZmI4LWNjMDE1ZWEzNjk5YiIsImVtYWlsIjoicnV0dmlrQHJ1dHZpa3FhLnRlc3RpbmF0b3IuY29tIn0.nlLeKQuYa86deuSEE7hcLvKmGp_nriazjY8XasYaHg2U7qrHNUvUMBECcMYqwLfHYhDlPjcVtBKUtdP0Dh2l48LSjyYYxjqugc2DPl3xCU64baanmQTqUY_d1tnVk8DjNfgpZziRqszGVb7kgAVEYAEa0z43UQCJMTeDqJhEbT-I4MOzRvOAv3VSlv_ZUtgRo78ubYuRj1QqvPu40sQXT6pIcDyxzmj6gBRjj0phyeoYiW1KjVDboMskhYLOnIKFZwIKlDG24Re63pnWaFx_qLByRpTJBvYTbE2KVfvm4yLNv-f3F_WWQsscyyyKDTVlbHHICUjPVqjAsZtULlOPPg"
#     }

#     def validate_data1(response_data, start_dt, end_dt, task_day):
#         if not response_data.get('data'):
#             logging.info("No data found in response for %s", task_day)
#             return
        
#         start_dt = datetime.strptime(start_dt, "%Y-%m-%dT%H:%M:%S.%fZ")
#         end_dt = datetime.strptime(end_dt, "%Y-%m-%dT%H:%M:%S.%fZ")

#         for entry in response_data.get('data', []):
#             due_date = datetime.strptime(entry['due_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
#             if start_dt <= due_date < end_dt:
#                 logging.info("Correct Data for %s in DOB API: %s", task_day, entry['task_id'])
#             else:
#                 logging.error("Bug Found in DOB API: %s, due_date: %s, for %s", entry['task_id'], entry['due_date'], task_day)





#     # Make API call for today's data
#     logging.info("Making API call for today's DOB tasks:")
#     today_response1 = requests.get(today_api_url1, headers=headers)
#     if today_response1.status_code == 200:
#         today_data1 = today_response1.json()
#         logging.info("DOB Today's API response: %s", today_data1)
#         validate_data1(today_data1, today_start_dt, today_end, "Today")
#     else:
#         logging.error("Failed to fetch DOB today's API data. Status code: %s", today_response1.status_code)






#     # Make API call for tomorrow's data
#     logging.info("Making API call for tomorrow's DOB tasks:")
#     tomorrow_response1 = requests.get(tomorrow_api_url1, headers=headers)
#     if tomorrow_response1.status_code == 200:
#         tomorrow_data1 = tomorrow_response1.json()
#         logging.info("DOB Tomorrow's API response: %s", tomorrow_data1)
#         validate_data1(tomorrow_data1, today_str, tomorrow_str, "Tomorrow")
#     else:
#         logging.error("Failed to fetch DOB tomorrow's API data. Status code: %s", tomorrow_response1.status_code)
    



# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     page = browser.new_page()
#     overview_filters(page)
