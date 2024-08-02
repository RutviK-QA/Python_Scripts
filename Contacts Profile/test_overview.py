from dotenv import load_dotenv
import logging
from playwright.async_api import Page, async_playwright, expect, Playwright
import asyncio
import os
import random
from datetime import datetime
import re
import time
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

async def get_percentage(element1, abc):
    text_content = element1.inner_text()
    percentage = text_content.split()[0] 
    logging.info(f"Progress Area: {abc}, Percentage: {percentage}")

async def assert_overview_fields(page):
    await expect(page.get_by_role("heading", name="Protection", exact=True)).to_be_visible()
    await expect(page.get_by_role("heading", name="Total Coverage")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Total Coverage$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Total Monthly Payment").first).to_be_visible()
    await expect(page.locator("ul").filter(has_text="Total Coverage$0Total Monthly").get_by_role("paragraph").nth(1)).to_be_visible()
    await expect(page.get_by_role("heading", name="TFSA")).to_be_visible()
    await expect(page.locator("li").filter(has_text="TFSA$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="RRSP")).to_be_visible()
    await expect(page.locator("li").filter(has_text="RRSP$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="RESP")).to_be_visible()
    await expect(page.locator("li").filter(has_text="RESP$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Total Market Value")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Total Market Value$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Total PAC Monthly")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Total PAC Monthly$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Total Protection")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Total Protection$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Total Monthly Payment").nth(1)).to_be_visible()
    await expect(page.locator("ul").filter(has_text="Total Protection$0Total").get_by_role("paragraph").nth(1)).to_be_visible()
    await expect(page.get_by_role("heading", name="Total Investments")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Total Investments$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Annual Income")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Annual Income$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Expenses")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Expenses$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Other Income")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Other Income$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Net Cashflow")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Net Cashflow$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Rental Income")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Rental Income $").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Liquid Assets")).to_be_visible()
    await expect(page.get_by_role("heading", name="Fixed Assets")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Liquid Assets$").get_by_role("paragraph")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Fixed Assets$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Liabilities")).to_be_visible()
    await expect(page.get_by_role("heading", name="Net Networth")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Net Networth$").get_by_role("paragraph")).to_be_visible()
    await expect(page.locator("li").filter(has_text="Liabilities$").get_by_role("paragraph")).to_be_visible()
    await expect(page.get_by_role("heading", name="Protection", exact=True)).to_be_visible()
    await expect(page.get_by_text("Current Active Policies")).to_be_visible()
    await expect(page.get_by_role("heading", name="Wealth")).to_be_visible()
    await expect(page.get_by_text("Current Investments/Savings")).to_be_visible()
    await expect(page.get_by_role("heading", name="Monthly Contribution Summary")).to_be_visible()
    await expect(page.get_by_role("heading", name="Cashflow", exact=True)).to_be_visible()
    await expect(page.get_by_role("heading", name="Networth", exact=True)).to_be_visible()


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
        logging.info("No elements found with the specified class.")
        return None

    
    # Choose a random element
    index = random.randint(0, count - 1)
    chosen_element = locator.nth(index)
    element_content = await chosen_element.text_content()
    logging.info(f"Clicked on name: {element_content}")
    
    # Perform any action needed on the chosen element, e.g., click
    await chosen_element.click()

    await page.locator("div").filter(has_text=re.compile(r"^Overview$")).click()

    #   New Note
    await page.get_by_role("button", name="New Note").click()
    toss1=utils.coin_toss()
    if toss1 == "Heads":
        await page.get_by_role("combobox").click()
        await utils.for_x_y_async(page, 1, 20)
    else:
        await page.get_by_role("combobox").fill(utils.generate_random_string(10))
        await page.keyboard.press("Enter")

    selected_files = utils.upload_random_files(m=1)
    
    for file in selected_files:
        page.locator("input[type=\"file\"]").set_input_files(file)
    
    await utils.Voice_to_text_async(page)


    await expect(page.locator("text=Note saved successfully!")).to_be_visible()
    
    element= await utils.get_random_locator(page.get_by_label("overview-notes").get_by_role("img"))
    if element != None: 
        await expect(element).to_be_visible()
        await element.click()
    else:
        pass

    await page.wait_for_load_state('networkidle')
    await page.get_by_label("close").click()
    
    locator = await utils.get_random_locator(page.get_by_label("Edit Note"))
    await locator.click()
    
    #   New Task
    await page.get_by_label("New Task").click()
    a=await utils.priority_random_async()

    await page.get_by_label(f"{a} *").check()

    await page.locator("input[name=\"title\"]").click()
    await utils.for_x_y_async

    await page.get_by_role("textbox").first.click()
    await utils.click_calendar_async

    await page.get_by_role("combobox").nth(1).click()
    await utils.for_x_y_async

    await utils.add_reminder_async(page)
    await utils.Voice_to_text_async(page)

    element= await utils.get_random_locator(page.get_by_text("Follow Ups"))
    if element != None: 
        await expect(element).to_be_visible(timeout=5000)   
    else:
        try:
            await expect(page.get_by_text("Sales").first).to_be_visible(timeout=1000)
        except:
            try:
                await expect(page.get_by_text("Events").first).to_be_visible(timeout=1000)
            except:
                try:
                    await expect(page.get_by_text("Birthday").first).to_be_visible(timeout=1000)
                except:
                    await expect(page.get_by_text("Anniversary").first).to_be_visible(timeout=1000)

    div_locator = page.locator('div.checkbox-item.text-blue')
    
    # Get the number of matching elements
    count = await div_locator.count()
    
    texts = []
    
    # Iterate over each element to get the 'aria-label' attribute
    for i in range(count):
        div_element = div_locator.nth(i)
        # Locate the <p> element within the current div
        p_element = div_element.locator('p.mb-0.ml-2')
        # Get the text content of the <p> element
        text_content = await p_element.inner_text()
        texts.append(text_content)
    count = len(texts)

    div_locator = page.locator('div.MuiTypography-root.MuiTypography-caption.css-157rtdk')
    
    # Get the text content of the div
    text_content = await div_locator.inner_text()
    
    # Extract the numeric part from the text (assuming the text is in the format '25%')
    percentage = ''.join(filter(str.isdigit, text_content))

    if percentage == "25" and count == 1:
        pass
    elif percentage == "50" and count == 2:
        pass
    elif percentage == "75" and count == 3:
        pass
    elif percentage == "100" and count == 4:
        pass
    else:
        logging.info(f"Failure in Compliance Progress: Percentage: {percentage}, Count: {count}")
    abc = ["personal", "financial", "legal"]   
    for _ in abc:
        element1 = page.locator(f'span.font-600.text-blue[aria-label="{abc}-progress-count"]')
        await get_percentage(element1, abc)

    await assert_overview_fields(page)


async def run() -> None:
    async with async_playwright() as p:
        browser1 = await p.chromium.launch(headless=True)
        context1 = await browser1.new_context(storage_state="variables/playwright/.auth/state.json")
        await context1.grant_permissions(["microphone"], origin="https://staging.bluemind.app")
        contexts = [context1]

        await utils.start_trace(contexts)
        try: 
            page1 = await context1.new_page()
            await page1.set_viewport_size({"width": 1920, "height": 1080})
            response_handler, request_handler = await utils.start_handler_async(page1, api_urls)
            asyncio.gather(
                click_dynamic_text(page1)
            )
            await utils.stop_handler_async(page1, api_urls, response_handler, request_handler)
        
        except: # Save trace if failure
            await utils.stop_trace(script_name, contexts)
        
        finally:
            # Stop tracing without saving if no failure
            if not context1.tracing.stopped:
                await context1.tracing.stop()
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

