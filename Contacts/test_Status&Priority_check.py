from playwright.sync_api import sync_playwright, Playwright, Error
from datetime import datetime, timedelta
import time
import os
import logging
import random
import json
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

# api_pattern = re.compile(fr'^{re.escape(api_url)}')
api_urls = []
test_results = []

api_patterns = [
    re.compile(r'^https://staging-api\.bluemind\.app/api/client/1'),
    re.compile(r'^https://staging-api\.bluemind\.app/api/client_tasks/save'),
    re.compile(r'^https://staging-api\.bluemind\.app/api/client_tasks/update'),
    re.compile(r'^https://staging-api\.bluemind\.app/api/client_tasks/delete')
]
choice1= ["Yes", "No"]
names = ["Medium *", "Low *", "High *"]

def find_random_button(page, role, name):
    # Try to find the elements matching the given role and name
    elements = page.get_by_role(role, name=name)
    total_elements = elements.count()

    if total_elements == 0:
        logging.info(f"No elements found with role '{role}' and name '{name}'")
        return None
    
    logging.info(f"Found {total_elements} elements with role '{role}' and name '{name}'")
    
    # If at least one element exists, return a random one
    try:
        # Generate a random index between 0 and total_elements - 1
        random_index = random.randint(0, total_elements - 1)
        if random_index == 0:
            random_element = elements.first
            logging.info(f"Selected element at position {random_index+1}")
        else:    
            random_element = elements.nth(random_index)
            logging.info(f"Selected element at position {random_index+1}")
        return random_element
    except Exception as e:
        logging.info(f"Error occurred: {e}")
        return None

api_urls = []
api_urls1= []

def click_random_status_button(page):
    # Selector to find all buttons with the common class
    buttons = page.locator('button[class*="MuiButtonBase-root MuiButton-root"]')
    total_buttons = buttons.count()

    if total_buttons == 0:
        logging.info("No status buttons found.")
        return
    # List of statuses to look for
    statuses = ["Nurture", "Contacted", "New", "Move To Prospect", "No Response", "Move To Client", "Do Not Contact", "Unqualified"]
    
    # Filter buttons that match the statuses
    matching_buttons = []
    for i in range(total_buttons):
        button_text = buttons.nth(i).text_content()
        if button_text in statuses:
            matching_buttons.append(buttons.nth(i))

    if not matching_buttons:
        logging.info("No matching status buttons found.")
        return

    # Randomly select one of the matching buttons
    try:
        random_button = random.choice(matching_buttons)
        random_button_text = random_button.text_content()
        logging.info(f"Randomly selected status button: {random_button_text}")
    except Exception as e:
        logging.info(f"Error occurred in selecting outer status button: {e}")
        return

    # Click the selected button
    random_button.click()
    return random_button_text

# Function to search and process API response
def status_prio(page):
    page.wait_for_timeout(6000)
    request_handler = lambda request: utils.handle_request(request, api_urls)

    # Randomly select priority
    random_priority, random_choice = utils.select_random_priority(page)


    if random_priority:
        random_priority.click()
        page.wait_for_timeout(2000)
        page.on('request', request_handler)

        utils.random_prio(page, f"! {random_choice}")

    page.wait_for_timeout(5000) 
    page.remove_listener("request", request_handler)
    
    logging.info("Successful APIs in priority change:")
    for url in api_urls:
        logging.info(url)

    eliminate1=click_random_status_button(page)
    eliminate= ''.join(eliminate1)
    logging.info(f"To be eliminated status: {eliminate}")
    request_handler1 = lambda request: utils.handle_request1(request, api_urls1, api_patterns)

    page.on('request', request_handler1)

    menu_items = ["New", "Move To Prospect", "Nurture", "No Response", "Contacted", "Move To Client", "Do Not Contact", "Unqualified"]
    # menu_items = ["Move To Prospect", "Nurture"]
    # menu_items = random.choice(["Move To Prospect", "Nurture"])
    filtered_options = [option for option in menu_items if option != eliminate]

    if not filtered_options:
        logging.info("No valid menu items to choose from.")
    else:
        menu_item = random.choice(filtered_options)
        page.get_by_role("menuitem", name=menu_item).click()
        logging.info(f"Selected status: {menu_item}")

    if menu_item == "Move To Prospect":
        
        #Toggle Yes/No   If yes, then Task else if no, then sale opportunity
        random_choice11 = random.choice(choice1)
        if random_choice11 == "Yes":
            logging.info("Sales Opp Toggle Off")
            random_name1 = random.choice(names)
            page.get_by_label(random_name1).check()
            
            names1 = ["Sales *", "Events *", "Follow Ups *"]
            random_name1111 = random.choice(names1)
            logging.info(f"Type of Task {random_name1111}")
            page.get_by_label(random_name1111).check()

            page.wait_for_timeout(1000) 

            if random_name1111 =="Events *":
                page.locator("input[name=\"title\"]").fill(utils.generate_random_string(10))
                page.keyboard.press("Tab")
            else:
                page.keyboard.press("Tab")
                utils.for_x_y(page, "1", "8") 
                # Choice to add more letters to the subject clicked above or not
                random_choice1 = random.choice(choice1)
                if random_choice1 == "Yes":
                    page.keyboard.type(utils.generate_random_string(10))
                page.keyboard.press("Tab")
            
            #timezone press or no code
            random_choice4 = random.choice(choice1)
            if random_choice4 == "Yes":
                try:
                    page.locator("#formId").get_by_role("checkbox").check()
                except:
                    pass
            if random_choice4 == "No":
                try:
                    page.get_by_text("Timezone").click()
                    page.get_by_role("checkbox").check()
                    page.get_by_role("combobox").first.click()
                    utils.for_x_y(page, "1", "50")
                    page.get_by_role("combobox").nth(1).click()
                    utils.anti_for_x_y(page, "1", "200")
                    random_choice5 = random.choice(choice1)
                    if random_choice5 == "Yes":
                        page.get_by_role("button", name="Use current timezone").click()
                    else:
                        try:
                           page.get_by_role("button", name="Save").click()
                        except:
                            page.get_by_role("checkbox").check()
                            page.get_by_role("button", name="Save").click()

                except:
                    pass
            #due date 
            if random_name1111 != "Events *":
                page.get_by_role("textbox").first.click()
            else:
                page.get_by_role("textbox").nth(1).click()
            page.wait_for_timeout(1000)
            utils.click_calendar(page)
            page.wait_for_timeout(1000)
            # Removed nth1 and inserted first and nth2 made nth1
            page.get_by_role("combobox").first.click()
            utils.for_x_y(page, "1", "48")    
            try:
                page.get_by_role("combobox").nth(1).click()
                utils.for_x_y(page, "1", "48")
            except:
                pass
            #ADD REMINDER
            random_choice2 = random.choice(choice1)
            if random_choice2 == "Yes":
                random_choice23 = random.choice(choice1)
                utils.add_reminder(page, random_choice23)
                logging.info("Added Reminder")

            else:
                logging.info("No Reminder added")
                page.keyboard.press("Tab")
            
            utils.Voice_to_text(page)
            logging.info("Saved Move to Prospect")

        else:
            logging.info("Sales Opp Toggle On")
            page.get_by_label("", exact=True).check()
            random_choice6 = random.choice(choice1)
            if random_choice6 == "Yes":
                page.locator("div").filter(has_text=re.compile(r"^Insurance$")).click()
                logging.info("Selected Insurance")
            else:
                page.locator("div").filter(has_text=re.compile(r"^Investment$")).click()
                logging.info("Selected Investment")
            page.get_by_label("New Sale").click()
            page.keyboard.press("Tab")
            page.locator("div").filter(has_text=re.compile(r"^Product$")).click()
            utils.for_x_y(page, "1", "15")
            page.keyboard.press("Tab")
            page.keyboard.type(utils.generate_random_numbers(10))
            page.get_by_label("Click here to Select Expected").click()
            random_name21 = random.choice(names)

            page.get_by_label(random_name21).check()
            page.get_by_role("textbox").first.click()
            utils.click_calendar(page)
            
            page.get_by_role("combobox").nth(1).click()
            utils.for_x_y(page, "1", "48")
            try:
                page.get_by_role("combobox").nth(2).click()
                utils.for_x_y(page, "1", "48")
            except:
                pass
            #ADD REMINDER
            random_choice12 = random.choice(choice1)
            if random_choice12 == "Yes":
                random_choice33 = random.choice(choice1)
                utils.add_reminder(page, random_choice33)
                logging.info("Added Reminder in inner pop up")

            else:
                logging.info("No Reminder added in inner pop up")
                page.keyboard.press("Tab")
                page.keyboard.press("Tab")

            
            utils.Voice_to_text(page)

            page.get_by_label("New Sale").click()
            page.keyboard.press("Tab")

            page.locator("div").filter(has_text=re.compile(r"^Product$")).nth(1).click()
            utils.for_x_y(page, "1", "15")    
            page.keyboard.press("Tab")
            page.keyboard.type(utils.generate_random_numbers(10))
            page.locator("button").filter(has_text="* Closing Date").click()
            random_name111 = random.choice(names)

            page.get_by_label(random_name111).check()
            page.get_by_role("textbox").first.click()
            utils.click_calendar(page)
            
            page.get_by_role("combobox").nth(1).click()
            utils.for_x_y(page, "1", "48")
            try:
                page.get_by_role("combobox").nth(2).click()
                utils.for_x_y(page, "1", "48")
            except:
                pass
        
            random_choice13 = random.choice(choice1)
            # random_choice13 = "Yes"
            if random_choice13 == "Yes":
                random_choice43 = random.choice(choice1)
                utils.add_reminder(page, random_choice43)
                logging.info("Added Remixnder in inner pop up")  
            else:
                logging.info("No Reminder added in inner pop up")
                page.keyboard.press("Tab")
            
            utils.Voice_to_text(page)
            logging.info("Saved Move to Prospect's inner pop up")

            random_delete = random.choice(choice1)
            if random_delete == "Yes":  
                page.get_by_test_id("DeleteIcon").first.click()
            else:
                page.get_by_test_id("DeleteIcon").nth(1).click()
            page.get_by_role("button", name="Save").click()
            logging.info("Saved Move to Prospect")

    elif menu_item == "Move To Client":

        choice11= ["Yes", "No", "Cancel"] 
        random_choice = random.choice(choice11)
        if random_choice == "Yes":
            page.get_by_role("button", name="Yes").click()
        elif random_choice == "No":
            page.get_by_role("button", name="No").click()
        elif random_choice == "Cancel":
            page.get_by_label("close").click()
        logging.info(f"Move to Client : {random_choice}")
        page.wait_for_timeout(3000)
        
    else:
        page.wait_for_timeout(3000) 
        pass
    page.wait_for_timeout(5000)
    page.remove_listener("request", request_handler1)
    logging.info("Success!")
    page.wait_for_timeout(5000)  

def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("https://staging.bluemind.app/contacts")
        status_prio(page)
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


# from playwright.sync_api import sync_playwright, Playwright, Error
# from datetime import datetime, timedelta
# import time
# import os
# import logging
# import random
# import json
# from dotenv import load_dotenv
# import re
# import  string
# # Load environment variables
# load_dotenv(dotenv_path='variables/Variables.env')
# load_dotenv(dotenv_path='variables/API_responses.env')

# password = os.getenv('PASS')
# url = os.getenv('URL')
# username = os.getenv('USER')
# logs_folder = os.getenv('LOGS')

# # Setup logging
# if not os.path.exists(logs_folder):
#     os.makedirs(logs_folder)
# log_file_path = os.path.join(logs_folder, 'Status_&_Priority.txt')
# logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# api_pattern= re.compile(r'^https://staging-api\.bluemind\.app/api/client/1')
# api_pattern1= re.compile(r'^https://staging-api\.bluemind\.app/api/client_tasks/save')
# api_pattern2= re.compile(r'^https://staging-api\.bluemind\.app/api/client_tasks/update')
# api_pattern3= re.compile(r'^https://staging-api\.bluemind\.app/api/client_tasks/delete')


# # Def for Random chars
# def generate_random_string(length):
#     characters = string.ascii_letters + string.digits + string.punctuation + ' '
#     return ''.join(random.choice(characters) for _ in range(length))

# def generate_random_numbers(length):
#     characters = string.digits
#     return ''.join(random.choice(characters) for _ in range(length))



# def random_prio(page, exclude_priority: str):

#     names = ["! Low", "! Medium", "! High"]
#     # Exclude the specified priority
#     names = [name for name in names if name != exclude_priority]
    
#     if not names:
#         logging.info("No priorities available to select from after exclusion.")
#         return
#     random_name = random.choice(names)
#     page.get_by_role("menuitem", name=random_name).click()
#     time.sleep(2)    

# def select_random_priority(page):
#     choices = ["Low", "Medium", "High"]
#     random.shuffle(choices)  # Shuffle the list to randomize the order

#     for random_choice in choices:
#         try:
#             random_priority = find_random_button(page, "button", f"! {random_choice}")
#             if random_priority:
#                 return random_priority, random_choice
#         except Exception as e:
#             logging.info(f"Error occurred while finding random button for '{random_choice}': {e}")

#     logging.info("Failed to find any elements for all priorities")
#     return None, None  # Handle the case where no elements were found

# def find_random_button(page, role, name):
#     # Try to find the elements matching the given role and name
#     elements = page.get_by_role(role, name=name)
#     total_elements = elements.count()

#     if total_elements == 0:
#         logging.info(f"No elements found with role '{role}' and name '{name}'")
#         return None
    
#     logging.info(f"Found {total_elements} elements with role '{role}' and name '{name}'")
    
#     # If at least one element exists, return a random one
#     try:
#         # Generate a random index between 0 and total_elements - 1
#         random_index = random.randint(0, total_elements - 1)
#         if random_index == 0:
#             random_element = elements.first
#             logging.info(f"Selected element at position {random_index+1}")
#         else:    
#             random_element = elements.nth(random_index)
#             logging.info(f"Selected element at position {random_index+1}")
#         return random_element
#     except Exception as e:
#         logging.info(f"Error occurred: {e}")
#         return None

# api_urls = []

# def handle_request(request):
#     if request.method == "PUT" or request.method == "POST":
#         logging.info(f"Request URL: {request.url}")
#         api_urls.append(request.url)

# api_urls1= []

# def handle_request1(request):

#     if api_pattern.match(request.url):
#         logging.info(f"Request URL 1: {request.url}")
#         api_urls.append(request.url)

#     if api_pattern1.match(request.url):
#         logging.info(f"Request URL 2: {request.url}")
#         api_urls1.append(request.url)

#     if api_pattern2.match(request.url):
#         logging.info(f"Request URL 3: {request.url}")
#         api_urls1.append(request.url)

#     if api_pattern3.match(request.url):
#         logging.info(f"Request URL 4: {request.url}")
#         api_urls1.append(request.url)

# def click_random_status_button(page):
#     # Selector to find all buttons with the common class
#     buttons = page.locator('button[class*="MuiButtonBase-root MuiButton-root"]')
#     total_buttons = buttons.count()

#     if total_buttons == 0:
#         logging.info("No status buttons found.")
#         return

#     logging.info(f"Found {total_buttons} status buttons.")

#     # List of statuses to look for
#     statuses = ["Nurture", "Contacted", "New", "Move To Prospect", "No Response", "Move To Client", "Do Not Contact", "Unqualified"]
    
#     # Filter buttons that match the statuses
#     matching_buttons = []
#     for i in range(total_buttons):
#         button_text = buttons.nth(i).text_content()
#         if button_text in statuses:
#             matching_buttons.append(buttons.nth(i))

#     if not matching_buttons:
#         logging.info("No matching status buttons found.")
#         return

#     # Randomly select one of the matching buttons
#     random_button = random.choice(matching_buttons)
#     random_button_text = random_button.text_content()
#     logging.info(f"Randomly selected status button: {random_button_text}")
    
#     # Click the selected button
#     random_button.click()

# # Function to search and process API response
# def search(page):
#     # Navigate to the page and perform actions
#     page.goto("https://staging.bluemind.app/login")
#     time.sleep(2)

#     # Perform login actions if required
#     if page.locator('[placeholder="Enter Email"]').is_visible():
#         page.locator('[placeholder="Enter Email"]').fill(username)
#         logging.info("Entered email")
#         page.locator('[placeholder="Password"]').fill(password)
#         page.keyboard.press("Enter")
#         logging.info("Logged In")
#         page.wait_for_navigation()
#     else:
#         pass
#     page.goto("https://staging.bluemind.app/contacts")
#     time.sleep(3)

#     # TEST API along with random priority

#     request_handler = lambda request: handle_request(request)

#     # Randomly select priority
#     random_priority, random_choice = select_random_priority(page)


#     if random_priority:
#         random_priority.click()
#         time.sleep(2)    
#         page.on('request', request_handler)

#         random_prio(page, f"! {random_choice}")

#     time.sleep(10)  # Adjust timeout as needed
#     page.remove_listener("request", request_handler)
    
#     logging.info("Successful APIs in priority change:")
#     for url in api_urls:
#         logging.info(url)

#     click_random_status_button(page)
#     request_handler1 = lambda request: handle_request1(request)

#     page.on('request', request_handler1)

#     # menu_item = random.choice(["Move To Prospect"]) 

#     menu_item = random.choice(["New", "Move To Prospect", "Nurture", "No Response", "Contacted", "Move To Client", "Do Not Contact", "Unqualified"]) 
#     page.get_by_role("menuitem", name=menu_item).click()
#     logging.info(f"Selected status: {menu_item}")

#     if menu_item == "Move To Prospect":
        
#         #Toggle Yes/No   If yes, then Task else if no, then sale opportunity
#         choice1= ["Yes", "No"]
#         random_choice11 = random.choice(choice1)
#         if random_choice11 == "Yes":
#             logging.info("Toggle Off")
#             names = ["Medium *", "Low *", "High *"]
#             random_name1 = random.choice(names)
#             page.get_by_label(random_name1).check()
            
#             names1 = ["Sales *", "Events *", "Follow Ups *"]
#             # names1 = ["Events *", "Events *"]
#             random_name1111 = random.choice(names1)
#             logging.info(random_name1111)
#             page.get_by_label(random_name1111).check()
                
#             page.keyboard.press("Tab")
#             time.sleep(1)

#             if random_name1111 =="Events *":
#                 page.locator("input[name=\"title\"]").fill(generate_random_string(10))
#                 page.keyboard.press("Tab")
#             else:
#                 for _ in range(random.randint(1, 8)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#                 # Choice to add more letters to the subject clicked above or not

#                 random_choice1 = random.choice(choice1)
#                 if random_choice1 == "Yes":
#                     page.keyboard.type(generate_random_string(10))
#                 page.keyboard.press("Tab")
            
#             random_choice4 = random.choice(choice1)
#             if random_choice4 == "Yes":
#                 try:
#                     page.locator("#formId").get_by_role("checkbox").check()
#                 except:
#                     pass
#             if random_choice4 == "No":
#                 try:
#                     page.get_by_text("Timezone").click()
#                     page.get_by_role("checkbox").check()
#                     page.get_by_role("combobox").first.click()
#                     for _ in range(random.randint(100, 200)):
#                         page.keyboard.press("ArrowDown")
#                     page.keyboard.press("Enter")
#                     page.get_by_role("combobox").nth(1).click()
#                     for _ in range(random.randint(1, 100)):
#                         page.keyboard.press("ArrowDown")
#                     page.keyboard.press("Enter")
#                     random_choice5 = random.choice(choice1)
#                     if random_choice5 == "Yes":
#                         page.get_by_role("button", name="Use current timezone").click()
#                     else:
#                         try:
#                            page.get_by_role("button", name="Save").click()
#                         except:
#                             page.get_by_role("checkbox").check()
#                             page.get_by_role("button", name="Save").click()

#                 except:
#                     pass
#             #due date and after that is pending
#             try:
#                 page.get_by_role("textbox", timeout=2000).first.click()
#             except:
#                 page.get_by_role("textbox").nth(1).click()

#             time.sleep(2)
#             tomorrow = datetime.today() + timedelta(days=1)
#             day_str = tomorrow.strftime('%d')
#             try:
#                 page.get_by_role("gridcell", name=day_str, exact=True).click()
#             except:
#                 page.get_by_label("Next month").click()
#                 time.sleep(1)
#                 page.get_by_role("gridcell", name="1", exact=True).click() 
            
#             # Removed nth1 and inserted first and nth2 made nth1
#             page.get_by_role("combobox").first.click()
#             for _ in range(random.randint(1, 48)):
#                 page.keyboard.press("ArrowDown")
#             page.keyboard.press("Enter")
#             try:
#                 page.get_by_role("combobox").nth(1).click()
#                 for _ in range(random.randint(1, 48)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#             except:
#                 pass
        
#             random_choice2 = random.choice(choice1)
#             # random_choice2 = "Yes"

#             if random_choice2 == "Yes":
#                 page.keyboard.press("Tab")
#                 page.get_by_role("button", name="Add Reminder").click()
#                 page.get_by_role("combobox").nth(2).click()
#                 for _ in range(random.randint(1, 2)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#                 page.keyboard.press("Tab")
#                 random_choice23 = random.choice(choice1)
#                 if random_choice23 == "Yes":
#                     for _ in range(random.randint(1, 10)):
#                         page.keyboard.press("ArrowDown")
#                 else:
#                     for _ in range(random.randint(1, 100)):
#                         page.keyboard.press("ArrowUp")
#                 page.keyboard.press("Tab")
#                 for _ in range(random.randint(1, 4)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#                 page.keyboard.press("Tab")
#                 page.keyboard.press("Tab")
#                 logging.info("Added Reminder")

#             else:
#                 logging.info("No Reminder added")
#                 page.keyboard.press("Tab")
            
#             page.get_by_role("button", name="Start").click()
#             time.sleep(3)   
#             page.get_by_role("button", name="Stop").click()
#             page.get_by_role("button", name="Reset").click()
#             page.get_by_role("button", name="Reset").press("Shift+Tab")
#             page.get_by_role("button", name="Start").press("Shift+Tab")
#             page.keyboard.type(generate_random_string(100))
#             page.get_by_role("button", name="Save").click()
#             logging.info("Saved Move to Prospect")

#         else:
#             logging.info("Toggle On")
#             page.get_by_label("", exact=True).check()
#             random_choice6 = random.choice(choice1)
#             if random_choice6 == "Yes":
#                 page.locator("div").filter(has_text=re.compile(r"^Insurance$")).click()
#                 logging.info("Toggled Insurance")
#             else:
#                 page.locator("div").filter(has_text=re.compile(r"^Investment$")).click()
#                 logging.info("Toggled Investment")
#             page.get_by_label("New Sale").click()
#             page.keyboard.press("Tab")
#             page.locator("div").filter(has_text=re.compile(r"^Product$")).click()
#             for _ in range(random.randint(1, 15)):
#                 page.keyboard.press("ArrowDown")
#             page.keyboard.press("Enter")
#             page.keyboard.press("Tab")
#             page.keyboard.type(generate_random_numbers(10))
#             page.get_by_label("Click here to Select Expected").click()
#             names = ["Medium *", "Low *", "High *"]
#             random_name21 = random.choice(names)

#             page.get_by_label(random_name21).check()
#             page.get_by_role("textbox").first.click()
#             time.sleep(1)
#             tomorrow = datetime.today() + timedelta(days=1)
#             day_str = tomorrow.strftime('%d')
#             try:
#                 page.get_by_role("gridcell", name=day_str, exact=True).click()
#             except:
#                 page.get_by_label("Next month").click()
#                 time.sleep(0.5)
#                 page.get_by_role("gridcell", name="1", exact=True).click() 
            
#             page.get_by_role("combobox").nth(1).click()
#             for _ in range(random.randint(1, 48)):
#                 page.keyboard.press("ArrowDown")
#             page.keyboard.press("Enter")
#             try:
#                 page.get_by_role("combobox").nth(2).click()
#                 for _ in range(random.randint(1, 48)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#             except:
#                 pass
        
#             random_choice12 = random.choice(choice1)
#             # random_choice12 = "Yes"
#             if random_choice12 == "Yes":
#                 page.keyboard.press("Tab")

#                 page.get_by_role("button", name="Add Reminder").click()
#                 page.get_by_role("combobox").nth(2).click()
#                 for _ in range(random.randint(1, 2)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#                 page.keyboard.press("Tab")
#                 random_choice33 = random.choice(choice1)
#                 if random_choice33 == "Yes":
#                     for _ in range(random.randint(1, 10)):
#                         page.keyboard.press("ArrowDown")
#                 else:
#                     for _ in range(random.randint(1, 100)):
#                         page.keyboard.press("ArrowUp")
#                 page.keyboard.press("Tab")
#                 for _ in range(random.randint(1, 4)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#                 page.keyboard.press("Tab")
#                 page.keyboard.press("Tab")
#                 logging.info("Added Reminder in inner pop up")

#             else:
#                 logging.info("No Reminder added in inner pop up")
#                 page.keyboard.press("Tab")
#                 page.keyboard.press("Tab")

            
#             page.get_by_role("button", name="Start").click()
#             time.sleep(10)   
#             page.get_by_role("button", name="Stop").click()
#             page.get_by_role("button", name="Reset").click()
#             page.keyboard.press("Shift+Tab")
#             page.keyboard.press("Shift+Tab")
#             page.keyboard.type(generate_random_string(100))
#             page.get_by_role("button", name="Save").click()

#             page.get_by_label("New Sale").click()
#             page.keyboard.press("Tab")

#             page.locator("div").filter(has_text=re.compile(r"^Product$")).nth(1).click()
#             for _ in range(random.randint(1, 15)):
#                 page.keyboard.press("ArrowDown")
#             page.keyboard.press("Enter")
#             page.keyboard.press("Tab")
#             page.keyboard.type(generate_random_numbers(10))
#             page.locator("button").filter(has_text="* Closing Date").click()
#             names = ["Medium *", "Low *", "High *"]
#             random_name111 = random.choice(names)

#             page.get_by_label(random_name111).check()
#             page.get_by_role("textbox").first.click()
#             time.sleep(1)
#             tomorrow = datetime.today() + timedelta(days=1)
#             day_str = tomorrow.strftime('%d')
#             try:
#                 page.get_by_role("gridcell", name=day_str, exact=True).click()
#             except:
#                 page.get_by_label("Next month").click()
#                 time.sleep(0.5)
#                 page.get_by_role("gridcell", name="1", exact=True).click() 
            
#             page.get_by_role("combobox").nth(1).click()
#             for _ in range(random.randint(1, 48)):
#                 page.keyboard.press("ArrowDown")
#             page.keyboard.press("Enter")
#             try:
#                 page.get_by_role("combobox").nth(2).click()
#                 for _ in range(random.randint(1, 48)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#             except:
#                 pass
        
#             random_choice13 = random.choice(choice1)
#             # random_choice13 = "Yes"
#             if random_choice13 == "Yes":
#                 page.keyboard.press("Tab")

#                 page.get_by_role("button", name="Add Reminder").click()
#                 page.get_by_role("combobox").nth(2).click()
#                 for _ in range(random.randint(1, 2)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#                 page.keyboard.press("Tab")
#                 random_choice43 = random.choice(choice1)
#                 if random_choice43 == "Yes":
#                     for _ in range(random.randint(1, 10)):
#                         page.keyboard.press("ArrowDown")
#                 else:
#                     for _ in range(random.randint(1, 100)):
#                         page.keyboard.press("ArrowUp")
#                 page.keyboard.press("Tab")
#                 for _ in range(random.randint(1, 4)):
#                     page.keyboard.press("ArrowDown")
#                 page.keyboard.press("Enter")
#                 page.keyboard.press("Tab")
#                 page.keyboard.press("Tab")
#                 logging.info("Added Reminder in inner pop up")  

            
#             else:
#                 logging.info("No Reminder added in inner pop up")
#                 page.keyboard.press("Tab")
            
#             page.get_by_role("button", name="Start").click()
#             time.sleep(3)   
#             page.get_by_role("button", name="Stop").click()
#             page.get_by_role("button", name="Reset").click()
#             page.get_by_role("button", name="Reset").press("Shift+Tab")
#             page.get_by_role("button", name="Start").press("Shift+Tab")
#             page.keyboard.type(generate_random_string(100))
#             page.get_by_role("button", name="Save").click()
#             logging.info("Saved Move to Prospect's inner pop up")

#             random_delete = random.choice(choice1)
#             if random_delete == "Yes":  
#                 page.get_by_test_id("DeleteIcon").first.click()
#             else:
#                 page.get_by_test_id("DeleteIcon").nth(1).click()
#             page.get_by_role("button", name="Save").click()
#             logging.info("Saved Move to Prospect")

#     elif menu_item == "Move To Client":

#         choice11= ["Yes", "No", "Cancel"] 
#         random_choice = random.choice(choice11)
#         if random_choice == "Yes":
#             page.get_by_role("button", name="Yes").click()
#         elif random_choice == "No":
#             page.get_by_role("button", name="No").click()
#         elif random_choice == "Cancel":
#             page.get_by_label("close").click()
#         logging.info(f"Move to Client : {random_choice}")
#         time.sleep(3)
        
#     else:
#         time.sleep(3)  
#         pass
#     page.remove_listener("request", request_handler1)

#     time.sleep(5)  

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     context = browser.new_context(storage_state="variables/playwright/.auth/state.json")
#     page = context.new_page()
#     page.set_viewport_size({"width": 1920, "height": 1080})
#     search(page)
#     browser.close()


