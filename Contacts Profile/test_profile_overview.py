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
variable = utils.variable
from collections import defaultdict

utils.logging_setup()
api_urls = defaultdict(dict)
test_results = []
exceptions = []

async def get_percentage(element1, abc):
    text_content = await element1.inner_text()
    percentage = text_content.split()[0] 
    logging.info(f"Progress Area: {abc}, Percentage: {percentage}")

async def assert_overview_fields(page):
    try:
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
    except:
        logging.info("Overview fields verification failed")

async def overview(page):
    
    await asyncio.sleep(6)
    await page.get_by_text("All Contacts").click(timeout=15000)     

    locator = page.locator('div.d-flex.align-items-center.profile-details b.text-blue.text-underline')
    await asyncio.sleep(5)

    # check if any list item are found
    count = await locator.count()
    if count == 0:
        logging.info("No elements found with the specified class.")
        return None
    
    # a random element chosen
    index = random.randint(0, count - 1)
    chosen_element = locator.nth(index)
    element_content = await chosen_element.text_content()
    logging.info(f"Clicked on name: {element_content}")
    
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

    selected_files = utils.upload_random_files(max_files=1)
    
    for file in selected_files:
        await page.locator("input[type=\"file\"]").set_input_files(file)
    
    await utils.Voice_to_text_async(page)


    await expect(page.locator("text=Note saved successfully!")).to_be_visible()
    
    element= await utils.get_random_locator(page.get_by_label("overview-notes").get_by_role("img"))
    if element != None: 
        await expect(element).to_be_visible()
        await element.click()
    else:
        pass
    await page.wait_for_timeout(5000)
    await page.get_by_label("close").first.click()
    
    locator = await utils.get_random_locator(page.get_by_label("Edit Note"))
    await locator.click()
    await page.wait_for_timeout(2000)
    await page.get_by_role("button", name="Update").click()
    
    x= await page.locator('p[aria-label="this-week-count"]').inner_text()
    xx= await page.locator('p[aria-label="next-week-count"]').inner_text()
    y= int(x)

    #   New Task
    await page.get_by_label("New Task").click()
    a=await utils.priority_random_async()

    await page.get_by_label(f"{a} *").check()

    await page.locator("input[name=\"title\"]").click()
    await utils.for_x_y_async(page, 1,20)

    await page.get_by_role("textbox").first.click()
    await utils.click_calendar_async(page)

    await page.get_by_role("combobox").nth(1).click()
    await utils.for_x_y_async(page, 1,20)

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

    xy= await page.locator('p[aria-label="this-week-count"]').inner_text()
    xxx= await page.locator('p[aria-label="next-week-count"]').inner_text()
    yy= int(xy)

    if yy == y+1 and xxx == xx:
        logging.info("New task added successfully for this week")
    elif yy==y and xxx == xx:
        logging.info("Task count remained same")
    elif yy== y and xxx== xx+1:
        logging.info("Task count increased but for next week")
    else:
        logging.info("Failure in task count increase")

    asyncio.sleep(3)

    # get the blue coloured done items out of 4 from the progress bar. max 4 possible
    divs = await page.query_selector_all('svg.text-blue + p.mb-0.ml-2')
    count2 = len(divs)

    # get the percentage of the progress bar
    div_locator = page.locator('div.MuiTypography-root.MuiTypography-caption.css-157rtdk')
    text_content = await div_locator.inner_text()     # Get the text content of the div
    percentage = ''.join(filter(str.isdigit, text_content))     # Extract the numeric part from the text (assuming the text is in the format '25%')

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
    # logging.info("Overview fields verified")

    async def download_1st(page):
        try:
            await download1(page)    
            await page.locator("div.apexcharts-menu-item.exportSVG").first.click() 
            await download1(page)
            await page.locator("div.apexcharts-menu-item.exportPNG").first.click()
            await download1(page)
            await page.locator("div.apexcharts-menu-item.exportCSV").first.click()
        except:
            logging.info("Download failure for 1st bar icon")

    async def download_2nd(page):
        try:
            await download2(page)
            await page.locator("div.apexcharts-menu-item.exportSVG").nth(1).click() 
            await download2(page)
            await page.locator("div.apexcharts-menu-item.exportPNG").nth(1).click()
            await download2(page)
            await page.locator("div.apexcharts-menu-item.exportCSV").nth(1).click()
        except:
            logging.info("Download failure for 2nd bar icon")

    async def download1(page):
        await page.locator("div").filter(has_text=re.compile(r"^Download SVGDownload PNGDownload CSV$")).first.click()
    async def download2(page):
        await page.locator("div").filter(has_text=re.compile(r"^Download SVGDownload PNGDownload CSV$")).nth(2).click()

    await download_1st(page)
    await download_2nd(page)
    # logging.info("Downloads completed")

async def run() -> None:
    async with async_playwright() as p:
        browser1 = await p.chromium.launch(headless=False)
        context1 = await browser1.new_context(storage_state="variables/playwright/.auth/state.json")
        await context1.grant_permissions(["microphone"], origin="https://staging.bluemind.app")
        context1.set_default_timeout(10000)
        contexts = [context1]

        await utils.start_trace(contexts)
        try: 
            page1 = await context1.new_page()
            await page1.set_viewport_size({"width": 1920, "height": 1080})
            await page1.goto("https://staging.bluemind.app/contacts")
            response_handler, request_handler = await utils.start_handler_async(page1, api_urls)
            await asyncio.gather(
                overview(page1)
            )
            await utils.stop_handler_async(page1, api_urls, response_handler, request_handler)
        
        except Exception as e:  # Save trace if failure
            exceptions.append(e)
            await utils.stop_trace(variable.script_name, contexts)
        
        finally:
            try:
                await context1.tracing.stop()  # Stop tracing
            except Exception as e:
                exceptions.append(e)
            await context1.close() 
            await browser1.close()  
    return exceptions

if __name__ == '__main__':
    exceptions = []
    # Ensure the states are recent by running the login scripts if necessary
    if not utils.is_recent_state(variable.state_path):
        subprocess.run(['python', variable.script_path], check=True)
    try:
        exceptions.extend(asyncio.run(run()))
        utils.start_report(test_results, variable.script_name)
    except Exception as e:
        exceptions.append(e)  # Collect exceptions
    finally:
        if exceptions:
            utils.traceback_error_logging_exp(variable.script_name, exceptions)
        utils.end_report(test_results, variable.script_name)
        

