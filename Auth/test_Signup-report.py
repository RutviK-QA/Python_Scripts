import asyncio
from playwright.async_api import async_playwright, Page
import random
import string
import time
import requests
from bs4 import BeautifulSoup
import logging
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils 
import re
from collections import defaultdict
import subprocess

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

async def execute_main_script(page):
    url = signup

    # async with async_playwright() as p:
      
    #     browser = await p.chromium.launch(headless=True)
    #     page = await browser.new_page()
    await page.goto(url)
    await page.wait_for_timeout(500)

    logging.info("Finding company input field...")
    await page.fill('input[name="company"]', "abctest")

    logging.info("Finding job title input field...")
    await page.fill('input[name="job_title"]', "4g")

    logging.info("Finding phone number input field...")
    await page.fill('input.form-control', "+1 (123) 456-789")

    logging.info("Finding employee field...")
    await page.click('#sctEmployee')
    await page.keyboard.press("ArrowDown")
    await page.keyboard.press("Enter")

    logging.info("Finding Next button...")
    await page.click('button.login-btn.bluemind-theme-btn')

    logging.info("Waiting for the first name field to be visible...")
    await page.fill('input[name="txtFirstName"]', "rk")

    logging.info("Waiting for the last name field to be visible...")
    await page.fill('input[name="txtLastName"]', "rk")

    random_chars = ''.join(random.choices(string.ascii_lowercase, k=4))
    email_address = f"{random_chars}@rutvikqa.testinator.com"
    # email_address = "rutvik@rutvikqa.testinator.com"
    logging.info(f"Email address: {email_address}")
    try:
        await page.fill('input[name="txtEmail"]', email_address)
        logging.info("Email address entered successfully.")
    except Exception as e:
        logging.info(f"Failed to enter email address: {str(e)}")

    await page.fill('input[name="txtPassword"]', password)
    await page.fill('input[name="txtConfirmPassword"]', password)

    await page.click('.MuiCheckbox-root > .PrivateSwitchBase-input')

    await page.click("//button[contains(text(),'Create Account')]")
    await asyncio.sleep(1)
    # Click "Proceed To Checkout" button
    await page.click('#submit-btn')
    # Add a delay before attempting to verify email link
    await asyncio.sleep(3)

    await utils.fetch_and_click_verification_link(mailinator, token)

    await page.click('#billing_address-line1')
    await page.type('#billing_address-line1', 'a')
    await page.wait_for_timeout(5000)
    await page.keyboard.press("ArrowDown")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(500)

    await page.click('#card-number')
    await page.wait_for_timeout(500)

    await page.click('#cb-test-card-0')
    await page.wait_for_timeout(500)

    await page.click('#submit-btn')
    logging.info("Clicked 'Submit' button.")
    # await page.wait_for_timeout(10000)

    await page.click("//span[contains(@class, 'text-blue') and contains(@class, 'text-underline') and contains(@class, 'font-weight-bold')]")
    # await page.wait_for_timeout(10000)

    await page.fill('#label-email', email_address)
    await page.fill('#label-password', password)
    await page.click("//button[contains(text(),'Log In')]")
    logging.info("Clicked 'Log In' button.")
    await page.wait_for_url("**/overview")
    logging.info("Successfully logged in.")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = await context.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        await execute_main_script(page)
        utils.stop_handler(page, api_urls, response_handler, request_handler)
        await context.close()
        await browser.close()

if __name__ == '__main__':
    # Ensure the state is recent by running the login script if necessary
    if not utils.is_recent_state(state_path):
        subprocess.run(['python', script_path])
    try:
        asyncio.run(main())
        utils.start_report(test_results, script_name)
    except Exception as e:
        utils.traceback_error_logging(script_name, e)
        utils.end_report(test_results, script_name)





# async def main(page):
#     response_handler, request_handler = utils.start_handler(page, api_urls)
#     await execute_main_script()
#     utils.stop_handler(page, api_urls, response_handler, request_handler)
#     await utils.fetch_and_click_verification_link(mailinator, token)

# async def run():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()
#         await main(page)
#         await browser.close()

# if __name__ == '__main__':
#     try:
#         asyncio.run(run())
#         utils.start_report(test_results, script_name)
#     except Exception as e:
#         utils.traceback_error_logging(script_name, e)
#         utils.end_report(test_results, script_name)


# Experimental


# async def fetch_and_click_verification_link():
#     url = "https://api.mailinator.com/api/v2/domains/private/inboxes?{token}"

#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         top_two_messages = data['msgs'][:2]

#         for message in top_two_messages:
#             subject = message.get('subject', '')
#             if subject == "Welcome to BlueMind":
#                 continue

#             message_id = message['id']
#             message_url = f"https://api.mailinator.com/api/v2/domains/private/messages/{message_id}?{token}"  
#             message_response = requests.get(message_url)

#             if message_response.status_code == 200:
#                 message_data = message_response.json()
#                 message_html = message_data['parts'][0]['body']
#                 soup = BeautifulSoup(message_html, 'html.parser')
#                 verify_link = soup.find('a', text='Verify Account')

#                 if verify_link:
#                     verify_url = verify_link['href']

#                     async with async_playwright() as p:
#                         browser = await p.chromium.launch(headless=True)
#                         page = await browser.new_page()
#                         await page.goto(verify_url)
#                         await page.wait_for_load_state('load')
#                         await browser.close()
#                     break
#                 else:
#                     write_to_report("No 'Verify Account' link found in the email.")
#                     break
#         else:
#             write_to_report("No relevant emails found with verification links.")
#     else:
#         write_to_report(f"Failed to fetch message summaries: {response.status_code}")
