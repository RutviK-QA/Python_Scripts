#Script in progress, do not assume it works

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
from collections import defaultdict
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
api_urls = defaultdict(dict)
test_results = []

def sidebar_note(page):
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
    page.get_by_label(f"{prio} *", exact=True).click()
    cate=utils.category_random()
    page.get_by_label(f"{cate} *", exact=True).click()
    logging.info(f"In Note, task selected: category {cate}, priority {prio}") 

    try:
        page.get_by_role("textbox").nth(2).click(timeout=2000)
    except:
        page.get_by_role("textbox").nth(1).click(timeout=2000)
    utils.click_calendar(page)
    
    page.get_by_role("combobox").nth(1).click()
    utils.for_x_y(page, "1", "48")
    
    if page.get_by_role("combobox").nth(2).is_visible():
        page.get_by_role("combobox").nth(2).click()
        utils.for_x_y(page, "1", "48")
    else:
        pass
    toss = utils.coin_toss()
    utils.add_reminder(page, toss)

    m=1
    selected_files = utils.upload_random_files(m)
    try:
        for file in selected_files:
            page.locator("input[type=\"file\"]").set_input_files(file)
    except Exception as e:
        logging.info(f"Error in file upload .{e}")

    utils.Voice_to_text(page)
    page.wait_for_timeout(3000)
    expect(page.locator("#tooltipContainer p")).to_be_visible() 

def task_sidebar(page):
    prio=utils.priority_random()
    page.get_by_text(f"{prio} *", exact=True).click()
    logging.info(f"Priority: {prio}")
    cate=utils.category_random()
    page.get_by_text(f"{cate} *", exact=True).click()
    logging.info(f"Category: {cate}")   

    if cate =="Events":
        page.locator("input[name=\"title\"]").fill(utils.generate_alphanumeric(10))
        page.keyboard.press("Tab")
        page.get_by_role("textbox").nth(1).click()
    else:
        page.locator("input[name=\"title\"]").click()
        utils.for_x_y(page, "1", "8") 
        # Choice to add more letters to the subject clicked above or not
        toss = utils.coin_toss()
        if toss == "Heads":
            page.keyboard.type(utils.generate_random_string(10))
        page.keyboard.press("Tab")
        page.get_by_role("textbox").first.click()
    
    utils.click_calendar(page)
    utils.Voice_to_text(page)   
    page.wait_for_timeout(5000)
    # Assert if task is visible on the sidebar once saved
    try:
        tomorrow = datetime.today() + timedelta(days=1)
        formatted_date = tomorrow.strftime("%b/%d/")
        try:
            assert page.get_by_text(f"{cate}{formatted_date}").is_visible()
            logging.info("Asserted task visibility on sidebar")
        except:
            try:
                assert page.get_by_text(f"{cate}{formatted_date}").first.is_visible()
                assert page.get_by_text(f"{cate}{formatted_date}").nth(1).is_visible()
                logging.info("Asserted 2nd task visibility on sidebar")
                try:
                    assert page.get_by_text(f"{cate}{formatted_date}").nth(2).is_visible()
                    logging.info("Asserted 3rd task visibility on sidebar")
                except:
                    pass
            except:
                pass
    except:
        logging.info("Failed to assert task visibility on sidebar, moving on")

def view_sidebar(page):
    page.goto(url_contacts)
    page.wait_for_timeout(5000)
    page.get_by_text("All Contacts").click()
    page.wait_for_timeout(5000)

    utils.tap_random_view_contact(page)
    page.wait_for_timeout(4000)

    #Email sending from sidebar
    try:            
        page.get_by_label("Send Email").click()
        page.get_by_role("textbox").fill(utils.generate_random_string(20))
        page.get_by_placeholder("Type to Add email").first.fill(utils.generate_alphanumeric(4) + "@rutvikqa.testinator.com")
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        page.keyboard.press("Tab")
        page.keyboard.type(utils.generate_alphanumeric(4) + "@rutvikqa.testinator.com")
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")

        try:
            selected_files = utils.find_latest_policy()
            file_input =  page.locator('input[type="file"]')
            file_input.set_input_files(selected_files)
            logging.info(f"Added {selected_files} to the contact pop up.")
        except Exception as e:
            logging.info(f"Error in file upload .{e}")

        utils.Voice_to_text(page)
    except: 
        logging.info("No email address for contact")
        pass

    # Task
    page.wait_for_timeout(2000)
    page.wait_for_selector('[data-testid="DateRangeOutlinedIcon"]').click()
    task_sidebar(page)

    # Note
    page.get_by_test_id("DescriptionOutlinedIcon").first.click()
    sidebar_note(page)

    # Sidebar Input Fields going from the right side top to bottom and moving to bottom left later on for business and personal type of contacts
    try:
        if page.locator(".FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").first.is_visible(timeout=5000):
            page.locator(".FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").first.click()
            utils.for_x_y(page, 1, 3)
    except:
        try:
            page.locator(".FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").first.click(timeout=3000)
            utils.for_x_y(page, 1, 3)
        except:
            pass

    if page.get_by_text("Personal").is_visible():
        page.locator(".mb-3 > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").first.click()
        utils.for_x_y(page, 1, 8)

    try:
        page.locator(".mb-3 > .MuiFormControl-root").first.click()  
        utils.generate_random_string(20)
    except:
        logging.info("Skipped City field")

    if page.get_by_text("Personal").is_visible():
        page.locator("div:nth-child(4) > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").click()
    else:     
        try:
            page.locator(".mb-3 > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").first.click()
        except:
            page.locator(".mb-3 > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").click()
    utils.for_x_y(page, 1, 8)

    if page.get_by_text("Business").is_visible():
        try:
            page.locator(".MuiPaper-root > div:nth-child(4) > .MuiFormControl-root").click()
            utils.remove_field_input(page)
            page.keyboard.type(utils.generate_random_numbers(10))
        except:
            page.locator("div:nth-child(5) > .MuiFormControl-root").click()
            utils.remove_field_input(page)
            page.keyboard.type(utils.generate_random_numbers(10))
        

    if page.locator("div:nth-child(5) > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").is_visible():
        page.locator("div:nth-child(5) > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").click()
        toss=utils.coin_toss()
        if toss == "Heads":
            utils.for_x_y(page, 1, 25)
        else:
            utils.generate_random_string(10)
            page.keyboard.press("Enter")
    elif page.locator("div:nth-child(4) > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").is_visible(): 
        page.locator("div:nth-child(4) > .FamilyStatusDropDown > .MuiAutocomplete-root > .MuiFormControl-root > .MuiInputBase-root").click()
        toss=utils.coin_toss()
        if toss == "Heads":
            utils.for_x_y(page, 1, 25)
        else:
            utils.generate_random_string(10)
            page.keyboard.press("Enter")

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
    
    def input_field(page):
        page.keyboard.press("Control+A")
        page.keyboard.type(utils.generate_random_string(20), delay=0)
        

    # try:
    #     page.locator("div:nth-child(8) > .MuiFormControl-root").click(timeout=1000)
    #     logging.info("1st try")
    #     input_field(page)
    # except: 
    #     try:
    #         page.locator(".MuiPaper-root > div:nth-child(7) > .MuiFormControl-root").first.click(timeout=1000)
    #         logging.info("2nd try")
    #         input_field(page)
    #     except:
    #         try:
    #             page.locator("div:nth-child(7) > .MuiFormControl-root").first.click(timeout=1000)
    #             logging.info("3rd try")
    #             input_field(page)
    #         except:
    #             try:
    #                 page.get_by_role("textbox", name="1 (702) 123-").click(timeout=1000)
    #                 page.keyboard.press("Tab")
    #                 page.keyboard.press("Tab")
    #                 page.keyboard.press("Tab")
    #                 input_field(page)
    #                 logging.info("4th try")
    #             except Exception as e:
    #                 logging.info(f"FAILURE.{e}")

    # Until the selection bug is fixed, use the below code, after that, comment the below code and uncomment the above code
    page.get_by_role("textbox", name="1 (702) 123-").click(timeout=1000)
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")
    input_field(page)

    
    page.get_by_label("Open").nth(1).click()
    utils.for_x_y(page, 1, 2)
    try:
        page.get_by_role("img").nth(3).click(timeout=1000)
    except:
        try:
            page.locator(".font-bold > .cursor-pointer > svg").click(timeout=1000)
        except:
            page.locator(".font-bold > .cursor-pointer > svg > path").first.click(timeout=1000)

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
        
    
    else:
        page.get_by_label("Open time").click()
        utils.for_x_y(page, 1, 24)
        page.get_by_label("Close time").click()
        utils.anti_for_x_y(page, 1, 24)

    try:    
        page.get_by_role("button", name="Save").click()
    except:
        page.get_by_role("button", name="close").click()
        logging.info("Save button not clickable, closing availability pop up")

    page.get_by_role("button", name="Save").click()

    logging.info("Sidebar input fields saved")
    page.wait_for_timeout(3000)
    try:
        page.get_by_label("Close", exact=True).click()
        page.wait_for_timeout(500)
    except:
        pass
    # page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    # page.evaluate("window.scrollTo(0, 0)")
    # element = page.locator("div:nth-child(2) > .LastContactedBlock > .MuiPaper-root > div:nth-child(3) > div").first
    # element.scroll_into_view_if_needed()
    #task from left panel of sidebar
    try:
        page.get_by_test_id("CalendarMonthOutlinedIcon").click()
    except:
        page.get_by_label("Create Task").click()
    
    task_sidebar(page)
    page.wait_for_timeout(4000)

    #note from left panel of sidebar
    try:
        page.get_by_label("Create Note").click()
    except:
        page.get_by_test_id("DescriptionOutlinedIcon").nth(1).click()

    sidebar_note(page)
    utils.move_to_random(page)
    logging.info("Sidebar test completed")

    # check for attached file in notes. if it opens, then close it
    try:
        page.locator(".lastContactedBottomRight > .MuiButtonBase-root").click()
        page.get_by_role("button", name="close").click()
    except:
        pass

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        # page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        view_sidebar(page)
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
