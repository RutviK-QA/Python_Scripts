from dotenv import load_dotenv
import logging
from playwright.async_api import Page, async_playwright, expect, Playwright
import asyncio
import os
from datetime import datetime, timedelta
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

google_account2 = "rutvikqatest@gmail.com"

script_name = os.path.basename(__file__).split('.')[0]
utils.logging_setup(script_name)

api_pattern = re.compile(fr'^{re.escape(api_url)}')
api_urls = defaultdict(dict)
test_results = []

tomorrow = datetime.today() + timedelta(days=1)
formatted_date = tomorrow.strftime('%A, %B %d, %Y')

async def repeat(page):
    await page.get_by_label(formatted_date, exact=True).dblclick()

    page.get_by_role("combobox").first.click()
    utils.for_x_y(page, 1, 30)  

    await page.get_by_role("combobox").nth(3).fill(utils.generate_alphanumeric(2)+("@rutvikqa.testinator.com") )
    await page.keyboard.press("Enter")

    a=utils.coin_toss()
    b=utils.coin_toss()
    c=utils.coin_toss()
    
    if a == "Heads":
        await page.locator("input[name=\"isMeeting\"]").check()
    if b == "Heads":
        await page.locator("input[name=\"all_day\"]").check()
    if c == "Heads":
        await page.locator("input[name=\"repeat\"]").check()

    utils.Voice_to_text(page)

async def test(page):

    await page.goto("https://staging.bluemind.app/calendar")

    while True:

        await repeat(page)

        await utils.fetch_and_check_sender_email(mailinator, google_account, google_account2)  
        
        await page.wait_for_timeout(3000)





async def run_tests_in_two_windows(mailinator_url: str, google_account: str, google_account2: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        # Create two browser contexts
        context1 = await browser.new_context(storage_state="variables/playwright/.auth/state.json")
        context2 = await browser.new_context(storage_state="variables/playwright/.auth/state.json")

        # Open pages in both contexts
        page1 = await context1.new_page()
        page2 = await context2.new_page()

        # Run the test function in parallel for both pages
        await asyncio.gather(
            test(page1),
            test(page2)
        )

        # Close contexts and browser
        await context1.close()
        await context2.close()
        await browser.close()

# Use below in above to code it properly

# async def main():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         context = await browser.new_context(storage_state="variables/playwright/.auth/state.json")
#         page = await context.new_page()
#         await page.set_viewport_size({"width": 1920, "height": 1080})
#         response_handler, request_handler = utils.start_handler(page, api_urls)
#         await test(page)
#         utils.stop_handler(page, api_urls, response_handler, request_handler)
#         await context.close()
#         await browser.close()

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


