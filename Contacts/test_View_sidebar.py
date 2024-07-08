from playwright.sync_api import sync_playwright, Playwright, Error, expect
from datetime import datetime, timedelta
import time
import os
import logging
import random
from dotenv import load_dotenv
import re
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

def view_sidebar(page):
    page.goto(url_contacts)
    page.wait_for_timeout(5000)
    page.get_by_text("All Contacts").click()
    page.wait_for_timeout(5000)

    response_handler = lambda response: utils.handle_response_failure1(response, api_urls, api_pattern)
    request_handler = lambda request: utils.handle_request1(request, api_urls, api_pattern)

    page.on('request', request_handler)
    page.on('response', response_handler)

    utils.tap_random_view_contact(page)
    page.wait_for_timeout(4000)
    # try:            
    #     page.get_by_label("Send Email").click()
    #     page.get_by_role("textbox").fill(utils.generate_random_string(20))
    #     page.get_by_placeholder("Type to Add email").first.fill(utils.generate_alphanumeric(4) + "@rutvikqa.testinator.com")
    #     page.keyboard.press("ArrowDown")
    #     page.keyboard.press("Enter")
    #     page.keyboard.press("Tab")
    #     page.keyboard.type(utils.generate_alphanumeric(4) + "@rutvikqa.testinator.com")
    #     page.keyboard.press("ArrowDown")
    #     page.keyboard.press("Enter")

    #     try:
    #         selected_files = utils.find_latest_policy()
    #         file_input =  page.locator('input[type="file"]')
    #         file_input.set_input_files(selected_files)
    #         logging.info(f"Added {selected_files} to the contact pop up.")
    #     except Exception as e:
    #         logging.info(f"Error in file upload .{e}")

    #     utils.Voice_to_text(page)
    # except: 
    #     logging.info("No email address for contact")
    #     pass

    #Task
    page.wait_for_timeout(2000)
    page.wait_for_selector('[data-testid="DateRangeOutlinedIcon"]').click()

    prio=utils.priority_random()
    page.get_by_text(f"{prio} *", exact=True).click()
    cate=utils.category_random()
    page.get_by_text(f"{cate} *", exact=True).click()

    if cate =="Events *":
        page.locator("input[name=\"title\"]").fill(utils.generate_random_string(10))
        page.keyboard.press("Tab")
    else:
        page.locator("input[name=\"title\"]").click()
        utils.for_x_y(page, "1", "8") 
        # Choice to add more letters to the subject clicked above or not
        toss = utils.coin_toss()
        if toss == "Heads":
            page.keyboard.type(utils.generate_random_string(10))
        page.keyboard.press("Tab")
        
    utils.Voice_to_text(page)   

    assert page.get_by_text(cate).is_visible()
    page.wait_for_timeout(2000)
    # Note
    page.get_by_test_id("DescriptionOutlinedIcon").first.click()
    page.get_by_role("combobox").click()
    toss = utils.coin_toss()
    if toss == "Heads":
        utils.for_x_y(page, "1", "20")
    else:
        x=random.randint(1,20)
        page.get_by_role("combobox").fill(utils.generate_random_string(x))
        page.keyboard.press("Enter")

    page.locator("#swich-swipe-2").check()
    prio=utils.priority_random()
    page.get_by_text(prio, exact=True).click()
    cate=utils.category_random()
    page.get_by_text(cate, exact=True).click()

    page.get_by_role("textbox").nth(1).click()
    utils.click_calendar()
    
    page.get_by_role("combobox").nth(1).click()
    utils.for_x_y(page, "1", "48")
    
    if page.get_by_role("combobox").nth(2).is_visible():
        page.get_by_role("combobox").nth(2).click()
        utils.for_x_y(page, "1", "48")
    else:
        pass
    toss = utils.coin_toss()
    utils.add_reminder(page, toss)

    selected_files = utils.upload_random_files(max_uploads=1)
    try:
        for file in selected_files:
            page.locator("input[type=\"file\"]").set_input_files(file)
    except Exception as e:
        logging.info(f"Error in file upload .{e}")

    utils.Voice_to_text(page)
    page.wait_for_timeout(2000)
    locator = page.locator("#tooltipContainer p")
    expect(locator).to_have_text() 

    # Sidebar Fields
    page.locator(".FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").first.click()
    utils.for_x_y(page, 1, 3)

    if page.get_by_text("Personal").is_visible():
        page.locator(".mb-3 > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").first.click()
        utils.for_x_y(page, 1, 8)

    page.locator(".mb-3 > .MuiFormControl-root").first.click()
    utils.generate_random_string(20)

    if page.get_by_text("Personal").is_visible():
        page.locator("div:nth-child(4) > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").click()
    else:     
        page.locator(".mb-3 > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").click()
    utils.for_x_y(page, 1, 8)

    if page.get_by_text("Business").is_visible():
        page.locator(".MuiPaper-root > div:nth-child(4) > .MuiFormControl-root").fill(utils.generate_random_numbers(10))

    if page.locator("div:nth-child(5) > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").is_visible():
        page.locator("div:nth-child(5) > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").click()
        toss=utils.coin_toss()
        if toss == "Heads":
            utils.for_x_y(page, 1, 25)
        else:
            utils.generate_random_string(10)
            page.keyboard.press("Enter")
    else:
        pass

    page.get_by_role("textbox", name="1 (702) 123-").click()

    for _ in range(15):
        page.keyboard.press("Backspace")

    number=utils.phone_number()
    page.get_by_role("textbox", name="1 (702) 123-").fill(number)

    page.locator(".custom-select__indicators").click()
    toss=utils.coin_toss()
    if toss == "Heads":
        utils.for_x_y(page, 1, 30)
    else:
        utils.generate_random_string(20)
        page.keyboard.press("Enter")

    if page.locator("div:nth-child(7) > .MuiFormControl-root").is_visible():
        page.locator("div:nth-child(7) > .MuiFormControl-root").click()

    if page.locator(".MuiPaper-root > div:nth-child(7) > .MuiFormControl-root").is_visible():
        page.locator(".MuiPaper-root > div:nth-child(7) > .MuiFormControl-root").click()

    if page.locator("div:nth-child(8) > .MuiFormControl-root").is_visible():
        page.locator("div:nth-child(8) > .MuiFormControl-root").click()

    utils.generate_random_string(20)
    
    page.get_by_role("combobox").first.click()
    utils.for_x_y(page, 1, 2)
    page.get_by_role("img").nth(3).click()

    days = ["M", "T", "W", "T", "F", "S", "S"]
    random_days = random.sample(days, random.randint(1, len(days)))
    for day in random_days:
        page.get_by_text(day, exact=True).first.click()

    toss=utils.coin_toss()
    
    if toss == "Heads":
        toss2=utils.coin_toss()
        if toss2 == "Heads":
            page.get_by_label("Available 24 hours").check()
        else:
            page.get_by_label("Not available").check()
        page.get_by_role("button", name="Save").click()
    
    else:
        page.get_by_label("Open time").click()
        utils.for_x_y(page, 1, 48)
        page.get_by_label("Close time").click()
        utils.for_x_y(page, 1, 48)
        page.get_by_role("button", name="Save").click()


    page.wait_for_timeout(5000)
    page.remove_listener("request", request_handler)
    page.remove_listener("response", response_handler)

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        view_sidebar(page)
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
