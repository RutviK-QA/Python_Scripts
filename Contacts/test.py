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
 api_url, url_contacts, login_api, mailinator, token, signup, origin_url) = utils.get_env_variables()

script_name = os.path.basename(__file__).split('.')[0]
utils.logging_setup(script_name)

api_pattern = re.compile(fr'^{re.escape(api_url)}')
api_urls = defaultdict(dict)
test_results = []
exceptions = []

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


async def get_percentage(element1, abc):
    text_content = await element1.inner_text()
    percentage = text_content.split()[0] 
    logging.info(f"Progress Area: {abc}, Percentage: {percentage}")

async def overview(page):
    await asyncio.sleep(6)
    # await page.wait_for_selector('text="All Contacts"', state='visible', timeout=15000) 
    await page.get_by_text("All Contacts").click(timeout=15000)    
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
    await asyncio.sleep(6)
    # Find all divs with both checkbox-item and text-blue classes
    divs = await page.query_selector_all('div.checkbox-item.text-blue')

    # Get the number of matching elements
    count2 = len(divs)
    logging.info(f"Count of divs with checkbox-item and text-blue: {count}")

    div_locator = page.locator('div.MuiTypography-root.MuiTypography-caption.css-157rtdk')
    
    # Get the text content of the div
    text_content = await div_locator.inner_text()
    
    # Extract the numeric part from the text (assuming the text is in the format '25%')
    percentage = ''.join(filter(str.isdigit, text_content))

    if percentage == "25" and count2 == 1:
        pass
    elif percentage == "50" and count2 == 2:
        pass
    elif percentage == "75" and count2 == 3:
        pass
    elif percentage == "100" and count2 == 4:
        pass
    else:
        logging.info(f"Failure in Compliance Progress: Percentage: {percentage}, Count: {count}")
    abc = ["personal", "financial", "legal"]   
    for x in abc:
        element1 = page.locator(f'span.font-600.text-blue[aria-label="{x}-progress-count"]')
        await get_percentage(element1, x)

    await assert_overview_fields(page)
    logging.info("Overview fields verified")

    async def download_1st(page):
        await download1(page)    
        await page.locator("div.apexcharts-menu-item.exportSVG").first.click() 
        await download1(page)
        await page.locator("div.apexcharts-menu-item.exportPNG").first.click()
        await download1(page)
        await page.locator("div.apexcharts-menu-item.exportCSV").first.click()
    
    async def download_2nd(page):
        await download2(page)
        await page.locator("div.apexcharts-menu-item.exportSVG").nth(1).click() 
        await download2(page)
        await page.locator("div.apexcharts-menu-item.exportPNG").nth(1).click()
        await download2(page)
        await page.locator("div.apexcharts-menu-item.exportCSV").nth(1).click()
    
    async def download1(page):
        await page.locator("div").filter(has_text=re.compile(r"^Download SVGDownload PNGDownload CSV$")).first.click()
    async def download2(page):
        await page.locator("div").filter(has_text=re.compile(r"^Download SVGDownload PNGDownload CSV$")).nth(2).click()

    await download_1st(page)
    await download_2nd(page)
    logging.info("Downloads completed")

async def run() -> None:
    async with async_playwright() as p:
        browser1 = await p.chromium.launch(headless=False)
        context1 = await browser1.new_context(storage_state="variables/playwright/.auth/state.json")
        await utils.grant_permissions(context1, origin_url)
        context1.set_default_timeout(10000)
        contexts = [context1]

        await utils.start_trace(contexts)
        page1 = await context1.new_page()
        await page1.set_viewport_size({"width": 1920, "height": 1080})
        await page1.goto("https://staging.bluemind.app/contacts")
        response_handler, request_handler = await utils.start_handler_async(page1, api_urls)
       
        try:
            await asyncio.gather(
                overview(page1)
            )
        except Exception as e:
            exceptions.append(e)
            await utils.stop_trace(script_name, contexts)

        await utils.stop_handler_async(page1, api_urls, response_handler, request_handler)
        await context1.tracing.stop()
        await context1.close() 
        await browser1.close()  
    return exceptions

if __name__ == '__main__':
    if not utils.is_recent_state(state_path):
        subprocess.run(['python', script_path], check=True)
    try:
        asyncio.run(run())
    except Exception as e:
        exceptions.append(e)  
    finally:
        if exceptions:
            utils.traceback_error_logging_exp(script_name, exceptions)
            utils.end_report(test_results, script_name)
        else:
            utils.start_report(test_results, script_name)

