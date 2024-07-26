from dotenv import load_dotenv
import logging
from playwright.async_api import Page, async_playwright, expect, Playwright
import asyncio
import os
import random
from datetime import datetime
import re
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils
from collections import defaultdict

# Load environment variables
utils.load_env_files()
script_path, state_path = utils.paths()
script_path_google, state_path_google = utils.paths_google()

# Retrieve environment variables
(password, loginurl, username, logs_folder, auth, google_account, 
 google_password, outlook_account, outlook_password, outlook_account2, 
 api_url, url_contacts, login_api, mailinator, token, signup) = utils.get_env_variables()

script_name = os.path.basename(__file__).split('.')[0]
utils.logging_setup(script_name)

api_pattern = re.compile(fr'^{re.escape(api_url)}')
api_urls = defaultdict(dict)
test_results = []


async def click_dynamic_text(page):
    await page.goto("https://staging.bluemind.app/contacts")
    await page.get_by_text("All Contacts").click()
    
    # Use a locator to find elements
    locator = page.locator('div.d-flex.align-items-center.profile-details b.text-blue.text-underline')
    
    # Wait for at least one element to be visible
    await asyncio.sleep(5)

    # Get the count of elements
    count = await locator.count()
    if count == 0:
        # logging.info("No elements found with the specified class.")
        return None
    
    # Log details of all found elements
    # for i in range(count):
    #     text_content = await locator.nth(i).text_content()
        # logging.info(f"Found element with text: {text_content}")
    
    # Choose a random element
    index = random.randint(0, count - 1)
    chosen_element = locator.nth(index)
    element_content = await chosen_element.text_content()
    logging.info(f"Clicked on name: {element_content}")
    
    # Perform any action needed on the chosen element, e.g., click
    await chosen_element.click()

    await page.locator("div").filter(has_text=re.compile(r"^Overview$")).click()

    await page.get_by_role("button", name="New Note").click()
    toss1=utils.coin_toss()
    if toss1 == "Heads":
        await page.get_by_role("combobox").click()
        await utils.for_x_y_async(page, 1, 20)
    else:
        await page.get_by_role("combobox").fill(utils.generate_random_string(10))
        await page.keyboard.press("Enter")

    await utils.Voice_to_text_async(page)
    await expect(page.locator("text=Note saved successfully!")).to_be_visible()

async def run() -> None:
    async with async_playwright() as p:
        browser1 = await p.chromium.launch(headless=True)
        context1 = await browser1.new_context(storage_state="variables/playwright/.auth/state.json")
        await context1.grant_permissions(["microphone"], origin="https://staging.bluemind.app")
        page1 = await context1.new_page()
        await page1.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = await utils.start_handler_async(page1, api_urls)

        asyncio.gather(
            click_dynamic_text(page1)
        )
        
        await utils.stop_handler_async(page1, api_urls, response_handler, request_handler)
        await context1.close()
        await browser1.close()

if __name__ == '__main__':

    # Ensure the states are recent by running the login scripts if necessary
    if not utils.is_recent_state(state_path):
        subprocess.run(['python', script_path], check=True)
    try:
        asyncio.run(run())
        utils.start_report(test_results, script_name)
    except Exception as e:
        utils.traceback_error_logging(script_name, e)
        utils.end_report(test_results, script_name)
        pass

