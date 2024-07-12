import re
from playwright.sync_api import Page, expect, sync_playwright
import time
import logging
import os
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

def log_and_print(message: str):
    logging.info(message)
    print(message)

def overview_buttons(page: Page) -> None:
    
    # Open the website
    page.goto("https://staging.bluemind.app/overview")
    page.wait_for_timeout(5000)

    # Click on Leads
    page.get_by_text("0Leads").click()
    log_and_print("Clicked Leads.")
    page.wait_for_timeout(1000)
    
    # Click on Overview
    page.get_by_role("link", name="Overview", exact=True).click()
    log_and_print("Clicked Overview.")
    page.wait_for_timeout(1000)
    
    # Click on Prospects
    page.get_by_text("0Prospects").click()
    log_and_print("Clicked Prospects.")
    page.wait_for_timeout(1000)
    
    # Click on Overview
    page.get_by_role("link", name="Overview", exact=True).click()
    log_and_print("Clicked Overview.")
    page.wait_for_timeout(1000)
    
    # Click on Clients
    page.locator("div").filter(has_text=re.compile(r"^0Clients$")).get_by_role("heading").click()
    log_and_print("Clicked Clients.")
    page.wait_for_timeout(1000)
    
    # Click on Overview
    page.get_by_role("link", name="Overview", exact=True).click()
    log_and_print("Clicked Overview.")
    page.wait_for_timeout(1000)
    
    # Download SVG from Gender chart
    page.locator("div").filter(has_text=re.compile(r"^Download SVGDownload PNGDownload CSV$")).first.click()
    with page.expect_download() as download_info:
        page.locator("#apexchartsGender-chart").get_by_text("Download SVG").click()
    download = download_info.value
    log_and_print(f"Downloaded SVG from Gender chart: {download.path()}")
    page.wait_for_timeout(1000)

    # Download SVG from Age graph
    page.locator("#apexchartsAge-graph").get_by_title("Menu").click()
    with page.expect_download() as download1_info:
        page.locator("#apexchartsAge-graph").get_by_text("Download SVG").click()
    download1 = download1_info.value
    log_and_print(f"Downloaded SVG from Age graph: {download1.path()}")
    page.wait_for_timeout(1000)

    # Download PNG from Gender chart
    page.locator("div").filter(has_text=re.compile(r"^Download SVGDownload PNGDownload CSV$")).first.click()
    with page.expect_download() as download2_info:
        page.locator("#apexchartsGender-chart").get_by_text("Download PNG").click()
    download2 = download2_info.value
    log_and_print(f"Downloaded PNG from Gender chart: {download2.path()}")
    page.wait_for_timeout(1000)

    # Download CSV from Gender chart
    page.locator("#apexchartsGender-chart").get_by_title("Menu").click()
    with page.expect_download() as download3_info:
        page.locator("#apexchartsGender-chart").get_by_text("Download CSV").click()
    download3 = download3_info.value
    log_and_print(f"Downloaded CSV from Gender chart: {download3.path()}")
    page.wait_for_timeout(1000)

    # Download PNG from Age graph
    page.locator("#apexchartsAge-graph").get_by_title("Menu").click()
    with page.expect_download() as download4_info:
        page.locator("#apexchartsAge-graph").get_by_text("Download PNG").click()
    download4 = download4_info.value
    log_and_print(f"Downloaded PNG from Age graph: {download4.path()}")
    page.wait_for_timeout(1000)

    # Download CSV from Age graph
    page.locator("#apexchartsAge-graph").get_by_title("Menu").click()
    with page.expect_download() as download5_info:
        page.locator("#apexchartsAge-graph").get_by_text("Download CSV").click()
    download5 = download5_info.value
    log_and_print(f"Downloaded CSV from Age graph: {download5.path()}")

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        overview_buttons(page)
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
