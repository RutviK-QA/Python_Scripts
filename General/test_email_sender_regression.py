from dotenv import load_dotenv
from playwright.async_api import Page, async_playwright, expect, Playwright
import asyncio
import os
from datetime import datetime, timedelta
import re
import logging
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
date_1 = tomorrow.strftime('%A, %B %d, %Y')
date_2 = tomorrow.strftime('%A, %B %d,')

async def disable_others(page):
    await page.locator("button:nth-child(7)").first.click()
    await page.get_by_label("Anniversary").uncheck()
    await page.get_by_label("Birthday", exact=True).uncheck()
    await page.get_by_label("Sales").uncheck()
    await page.get_by_label("Follow Ups").uncheck()
    await page.get_by_label("Events").uncheck()
    try:
        await page.get_by_label("rutvik@bluemind.app").uncheck(timeout=500)
    except:
        pass
    try:
        await page.get_by_label("rutvikqatest@gmail.com").uncheck(timeout=500)
    except:
        pass
    try:
        await page.get_by_label("rutvikqatester@gmail.com").uncheck(timeout=500)
    except:
        pass
    try:
        await page.get_by_label("rutvikqatest@outlook.com").uncheck(timeout=500)
    except:
        pass
    try:    
        await page.get_by_label("rutvikqatester@outlook.com").uncheck(timeout=500)
    except:
        pass
    await page.locator("button:nth-child(7)").first.click()


async def repeat_mailbox(page):
    await page.get_by_role("button", name="Compose").click()
    await page.get_by_text("Cc", exact=True).click()
    await page.get_by_text("Bcc").click()

    y=utils.generate_alphanumeric(3)
    y=y.lower()
    await page.get_by_placeholder("Type an email address and").first.fill(y+"@rutvikqa.testinator.com")
    await page.wait_for_timeout(500)
    yy=utils.generate_alphanumeric(3)
    yy=yy.lower()
    await page.get_by_placeholder("Type an email address and").nth(1).fill(yy+"@rutvikqa.testinator.com", timeout=2000)
    await page.wait_for_timeout(500)
    yyy=utils.generate_alphanumeric(3)
    yyy=yyy.lower()
    await page.get_by_placeholder("Type an email address and").nth(1).fill(yyy+"@rutvikqa.testinator.com", timeout=2000)

    x = [y, yy, yyy]

    await page.get_by_role("textbox").fill(utils.generate_alphanumeric(5))
    await page.keyboard.press("Tab")
    await page.keyboard.type(utils.generate_alphanumeric(2)) 
    await page.get_by_role("button", name="Send").click()
    await page.wait_for_timeout(3000)

    try:
        await expect(page.get_by_text("Message sent successfully!")).to_be_visible(timeout=3000)
        logging.info("Mailbox mail sent")
    except:
        logging.info("Mailbox mail send didnt work")

    return x

async def repeat_calendar(page):

    # appointment_exists = await page.query_selector("div.e-appointment-wrapper > div.e-appointment") is not None

    # if appointment_exists:
    #     await page.get_by_label(date_1, exact=True).dblclick(timeout=2000)
    # else:
    #     try:
    await page.get_by_label(date_2).dblclick(timeout=2000)
        # except:
        #     await page.get_by_label(date_1, exact=True).dblclick(timeout=2000)
 
    await page.locator("input[name=\"title\"]").fill(utils.generate_alphanumeric(3))

    await page.get_by_role("combobox").first.click()
    await page.wait_for_timeout(1000)
    await utils.for_x_y_async(page, 1, 30)  

    x=utils.generate_alphanumeric(3)
    x=x.lower()
    await page.get_by_role("combobox").nth(3).fill(x+("@rutvikqa.testinator.com"))
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

    await utils.Voice_to_text_async(page)
    return [x]

async def test_calendar(page):

    await page.goto("https://staging.bluemind.app/calendar")
    await page.wait_for_timeout(5000)
    await disable_others(page)

    while True:

        x=await repeat_calendar(page)
        await utils.fetch_and_check_sender_email(mailinator, google_account, google_account2, x)

async def test_mailbox(page):
    await page.goto("https://staging.bluemind.app/mail-box")

    while True:

        x=await repeat_mailbox(page)
        await utils.fetch_and_check_sender_email(mailinator, google_account, google_account2, x)


async def run_tests_in_two_windows() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        #  2 contexts of the browser
        context1 = await browser.new_context(storage_state="variables/playwright/.auth/state.json")
        context2 = await browser.new_context(storage_state="variables/playwright/.auth/state-google.json")
        
        # 4 pages, 2 browsers with 2 page each
        page1 = await context1.new_page()
        # page2 = await context2.new_page()
        # page3 = await context2.new_page()
        # page4 = await context1.new_page()

        # Run parrallel
        await asyncio.gather(
            test_calendar(page1),
            # test_calendar(page2),
            # test_mailbox(page3),
            # test_mailbox(page4)
        )

        await context1.close()
        await context2.close()
        await browser.close()

if __name__ == '__main__':

    # Ensure the states are recent by running the login scripts if necessary
    if not utils.is_recent_state(state_path) or not utils.is_recent_google_state(state_path_google):
        subprocess.run(['python', script_path], check=True)
        subprocess.run(['python', script_path_google], check=True)   

    try:
        asyncio.run(run_tests_in_two_windows())
        utils.start_report(test_results, script_name)
    except Exception as e:
        utils.traceback_error_logging(script_name, e)
        utils.end_report(test_results, script_name)



