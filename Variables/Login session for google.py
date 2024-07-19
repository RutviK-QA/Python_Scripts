import logging
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv(dotenv_path='variables/Variables.env')
load_dotenv(dotenv_path='variables/API.env')

password = os.getenv('PASS')
url = os.getenv('URL')
username = os.getenv('USER')

# Ensure directory exists
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Check if the login state file is recent
def is_recent_google_state(path, hours=8):
    if not os.path.exists(path):
        return False
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.now() - file_mod_time < timedelta(hours=hours)

# Function to login and save the storage state
def login_and_save_state():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        
        # Perform login actions
        page.get_by_role("button", name="Login with Google").click()
        try:
            page.get_by_role("link", name="rutvik khorasiya rutvik@").click()
        except:
            page.get_by_label("Email or phone").fill("rutvik@bluemind.app")
            page.get_by_label("Email or phone").press("Enter")
            page.get_by_label("Enter your password").fill("Rutvik2710$$")
            page.get_by_label("Enter your password").press("Enter")
            page.goto("https://dev.bluemind.app/socialSignIn?userData=eyJ1c2VyX2lkIjoyMTMsImVtYWlsIjoicnV0dmlrQGJsdWVtaW5kLmFwcCIsImZpcnN0bmFtZSI6InJ1dHZpayIsImxhc3RuYW1lIjoia2hvcmFzaXlhIiwiY3JlYXRlZF9hdCI6IjIwMjQtMDItMjdUMTE6NDI6MDUuMDAwWiIsInBhcmVudF9pZCI6MSwiZ3JvdXBfaWQiOnsiZ3JvdXBfaWQiOjcsImdyb3VwX25hbWUiOiJDbGllbnQifSwib3JnX2lkIjoxLCJjb21wYW55Ijp7ImlkIjoxOTYsIm5hbWUiOiJjIiwidXNlcl9pZCI6MjEzLCJ0YXJnZXRfZnljIjpudWxsLCJmeWMiOm51bGwsInRhcmdldF93ZWFsdGgiOm51bGwsIndlYWx0aCI6bnVsbCwicmV2ZW51ZSI6bnVsbCwiY29tcGxpYW5jZSI6bnVsbCwiY29tcGFueV9zbHVnIjoiY18xODA3MSIsImludml0YXRpb25fY29kZSI6IjMzZDdhYjEyLWI1MDQtNDBjZS1hYWVmLTM3MTNlZTI0ODYxMSIsImNyZWF0ZWRfYXQiOiIyMDI0LTAyLTI3VDExOjQyOjA1LjAwMFoiLCJ1cGRhdGVkX2F0IjoiMjAyNC0wMi0yN1QxMTo0MjowNS4wMDBaIiwiZGVsZXRlZF9hdCI6bnVsbH0sInN1YnNjcmlwdGlvbiI6eyJpZCI6MzU2LCJ1c2VyX2lkIjoyMTMsImNvbXBhbnlfaWQiOjE5Niwic3Vic2NyaXB0aW9uX2N1c3RvbWVyX2lkIjoiQXpxRXlxVTVVRDFRRWd5Iiwic3Vic2NyaXB0aW9uX3ByaWNlX2lkIjoiVGVzdC1QbGFuLTMtQ0FELVllYXJseSIsInN1YnNjcmlwdGlvbl9leHBpcmVfYXQiOiIyMDI0LTA3LTIwVDE0OjA2OjMyLjAwMFoiLCJpc19sZWdhY3kiOmZhbHNlLCJjcmVhdGVkX2F0IjoiMjAyNC0wMi0yN1QxMTo0MjowNS4wMDBaIiwidXBkYXRlZF9hdCI6IjIwMjQtMDctMTlUMTQ6MDY6MzMuMDAwWiIsImRlbGV0ZWRfYXQiOm51bGx9LCJhY2Nlc3NUb2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUpwWkNJNk1qRXpMQ0pwWVhRaU9qRTNNakV6T1Rnd09UTXNJbVY0Y0NJNk1UY3lNVFE0TkRRNU0zMC5sWTZmdEtUZGZQSXl4aWxKSU1PTGtsZnYwOFpiZjU1VXBZcjlrOGNyX2ZVIiwiaXNfYWN0aXZlX3N1YnNjcmlwdGlvbiI6dHJ1ZSwiaXNfc29jaWFsX3VzZXIiOnRydWUsIm1lc3NhZ2UiOiJMb2dnZWQgaW4gc3VjY2Vzc2Z1bGx5ISIsInByb3ZpZGVyIjoiZ29vZ2xlIn0=")
            page.goto("https://dev.bluemind.app/overview")
            
        # Wait for login to complete
        page.wait_for_timeout(5000)
        
        # Ensure the directory exists
        ensure_directory_exists('variables/playwright/.auth')
        
        # Save storage state (cookies, local storage) to a file
        context.storage_state(path="variables/playwright/.auth/state-google.json")
        browser.close()

# Main execution block
if __name__ == '__main__':
    state_path = 'variables/playwright/.auth/state-google.json'
    
    # Step 1: Check if the state is recent
    if not is_recent_google_state(state_path):
        # Step 2: Login and save the state if it's not recent
        login_and_save_state()
        logging.info("Created a new login session")
    else:
        logging.info("Logging in using existing session.")