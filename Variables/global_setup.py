# global_setup.py

import os
import json
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv(dotenv_path='variables/Variables.env')
auth = os.getenv('AUTH')
password = os.getenv('PASS')
url = os.getenv('URL')
username = os.getenv('USER')
cookies_path = 'variables/Cookies.json'

def globalSetup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Load cookies if available
            load_cookies(page, cookies_path)
        except FileNotFoundError:
            # Navigate to login page
            page.goto(url)
            page.get_by_placeholder("Enter Email").fill(username)
            page.get_by_placeholder("Password").fill(password)
            page.get_by_placeholder("Password").press("Enter")
            logging.info("Logged In but bypassed session login")

            # Handle Google authentication popup
            page.get_by_label("Manage communication accounts").click()
            with page.expect_popup() as popup_info:
                page.get_by_role("button", name="Connect Gmail").click()
            popup = popup_info.value

            if popup:
                # Fill in Google authentication form
                popup.fill('input[type="email"]', username)
                popup.locator('#identifierNext >> button').click()
                popup.fill('#password >> input[type="password"]', password)
                popup.locator('button >> nth=1').click()

                # Wait for authentication to complete
                page.wait_for_navigation()
                page.context().storage_state(path="./setup/storage-state.json")

                # Save cookies for future use
                cookies = page.context().cookies()
                with open(cookies_path, 'w') as f:
                    json.dump(cookies, f)
            else:
                logging.warning("Google authentication popup not found.")

        finally:
            browser.close()

def load_cookies(page, path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            cookies = json.load(f)
        page.context.add_cookies(cookies)

if __name__ == "__main__":
    globalSetup()