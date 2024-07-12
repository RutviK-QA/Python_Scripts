from playwright.sync_api import sync_playwright, Page
import re
import os
import logging
import random
from dotenv import load_dotenv
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

def handle_request(route, request):
    global intercepted_request
    if request.url == 'https://staging-api.bluemind.app/api/auth/resetpassword' and request.method == 'POST':
        intercepted_request = request
        route.fulfill(
            status=200,
            body='{"data":null,"message":"","responseType":"success"}',
            headers={'Content-Type': 'application/json'}
        )
    else:
        route.continue_()


def test_forgot_password(page: Page) -> None:
    page.goto(loginurl)
    logging.info("Opened the signin page.")

    page.wait_for_timeout(5000)
    page.click('text="Forgot password?"')
    print("Clicked 'Forgot password?' link.")
    logging.info("Clicked forgot password button.")

    usernames = ['rutvikk@rutvikqa.testinator.com', 'rutvikkk@rutvikqa.testinator.com', username]
    random_username = random.choice(usernames)
    page.wait_for_timeout(5000)
    page.fill('input[placeholder="Enter email"]', random_username)
    page.click('button:has-text("Send")')
    print("Entered email and submitted.")
    logging.info("Entered email and submitted.")

    page.wait_for_timeout(5000)

    page.click('button:has-text("Go to Reset Password")')
    print("Clicked 'Go to Reset Password' button.")
    logging.info("Clicked Go to reset password button")

    otp = utils.fetch_otp(mailinator, token)
    if otp:
        print("Fetched OTP:", otp)
        logging.info("Fetched OTP.")
    else:
        print("No OTP fetched, start the OTP fetching procedure.")
        logging.info("No OTP fetched.")

    if otp:
        page.wait_for_timeout(5000)
        page.fill('input[placeholder="Enter code"]', otp)
        print("Entered OTP.")
        logging.info("Entered OTP.")

    page.wait_for_timeout(5000)
    page.fill('input[placeholder="Password"]', password)
    page.fill('input[placeholder="Confirm password"]', password)

    page.wait_for_timeout(5000)
    page.route('**', handle_request)
    page.click('button:has-text("Reset Password")')
    page.wait_for_timeout(8000)
    logging.info("Entered passwords and pressed reset.")

    if intercepted_request:
        try:
            response = intercepted_request.response()
            status = response.status
            response_data = response.body().decode('utf-8')

            if status == 200:
                logging.info("Reset password API successful")
            else:
                logging.info(f"Intercepted request method: {intercepted_request.method}")
                logging.info(f"Intercepted request post data: {intercepted_request.post_data()}")
                logging.info(f"Intercepted request url: {intercepted_request.url}")
                logging.info(f"Intercepted request response data: {response_data}")
        except Exception as e:
            logging.error(f"Error while verifying the intercepted request: {e}")
    else:
        logging.info("Reset password API call not found")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        response_handler, request_handler = utils.start_handler(page, api_urls)
        test_forgot_password(page)
        utils.stop_handler(page, api_urls, response_handler, request_handler)
        browser.close

if __name__ == '__main__':
    try:
        main()
        utils.start_report(test_results, script_name)
    except Exception as e:
        utils.traceback_error_logging(script_name, e)
        utils.end_report(test_results, script_name)