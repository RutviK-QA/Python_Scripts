from dotenv import load_dotenv
import logging
import random
from playwright.async_api import Page, async_playwright, expect
import os
from datetime import datetime, timedelta
import re
import asyncio
import tracemalloc
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Variables.utils as utils
from collections import defaultdict

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
exceptions = []

async def verify_signed_out(page: Page) -> None:
    await expect(page.get_by_text("Signed out successfully!")).to_be_visible()

async def accounts(page: Page) -> None:
    try:
        try:
            await page.wait_for_load_state("networkidle", timeout=8000)
        except:
            pass
        await page.wait_for_timeout(5000)
        # if await page.locator("div").filter(has_text=re.compile(r"^rutvik@bluemind\.app$")).locator("div").first.is_visible():
        #     await page.locator("div").filter(has_text=re.compile(r"^rutvik@bluemind\.app$")).locator("div").first.hover()
        # elif await page.locator("div").filter(has_text=re.compile(r"^Primary$")).first.is_visible():
        #     await page.locator("div").filter(has_text=re.compile(r"^Primary$")).first.hover()
        # elif await page.locator("div").filter(has_text=re.compile(r"^Make Primary$")).first.is_visible():
        #     await page.locator("div").filter(has_text=re.compile(r"^Make Primary$")).first.hover()
            
        o14=r"^Make Primaryrutvik@bluemind\.app$"
        o15=r"^Primaryrutvik@bluemind\.app$"
        o22=r"^rutvik@bluemind\.app$"
        # If rutvik@bluemind is found and is not primary, sign out
        if await page.locator("div").filter(has_text=re.compile(fr"{o14}")).get_by_label("Sign out").is_visible():
            await page.locator("div").filter(has_text=re.compile(fr"{o14}")).get_by_label("Sign out").click()
            await page.get_by_role("button", name="Sign Out").click()
            logging.info("Signed out of Google (non primary)")
            try:
                await verify_signed_out(page)
            except Exception as e:
                exceptions.append(e)
        # If rutvik@bluemind is found and is primary, then sign out    
        elif await page.locator("div").filter(has_text=re.compile(fr"{o15}")).get_by_label("Sign out").is_visible():
            await page.locator("div").filter(has_text=re.compile(fr"{o15}")).get_by_label("Sign out").click()
            await page.get_by_role("button", name="Sign Out").click()
            logging.info("Signed out of Google (primary)")
            try:
                await verify_signed_out(page)
            except Exception as e:
                exceptions.append(e)
        elif await page.locator("div").filter(has_text=re.compile(fr"{o22}")).get_by_label("Sign out").is_visible():
            await page.locator("div").filter(has_text=re.compile(fr"{o22}")).get_by_label("Sign out").click()
            await page.get_by_role("button", name="Sign Out").click()
            try:
                await verify_signed_out(page)
            except Exception as e:
                exceptions.append(e)
            logging.info("Signed out of Google")            
        # Try forced signout when only 1 is properly connected
        elif await page.get_by_label("Sign out").is_visible():
            await page.get_by_label("Sign out").click()
            await page.get_by_role("button", name="Sign Out").click()
            try:
                await verify_signed_out(page)
            except Exception as e:
                exceptions.append(e)
            logging.info("Signed out of Google")
        else:
            logging.info("skipped google signout")

        # if await page.locator("div").filter(has_text=re.compile(r"^rutvikqatest@outlook\.com$")).locator("div").first.is_visible(): 
        #     await page.locator("div").filter(has_text=re.compile(r"^rutvikqatest@outlook\.com$")).locator("div").first.hover()
        # elif await page.locator("div").filter(has_text=re.compile(r"^Primary$")).first.is_visible():
        #     await page.locator("div").filter(has_text=re.compile(r"^Primary$")).first.hover()
        # elif await page.locator("div").filter(has_text=re.compile(r"^Make Primary$")).first.is_visible():
        #     await page.locator("div").filter(has_text=re.compile(r"^Make Primary$")).first.hover()

        o12=r"^Make Primaryrutvikqatest@outlook\.com$"
        o13=r"^Primaryrutvikqatest@outlook\.com$"
        o21=r"^rutvikqatest@outlook\.com$"
        # If rutvikqatest@outlook is found and is not primary, sign out
        if await page.locator("div").filter(has_text=re.compile(fr"{o12}")).get_by_label("Sign out").is_visible(): 
            await page.locator("div").filter(has_text=re.compile(fr"{o12}")).get_by_label("Sign out").click()
            await page.get_by_role("button", name="Sign Out").click()
            logging.info("Signed out of Outlook (non primary)") 
            try:
                await verify_signed_out(page)
            except Exception as e:
                exceptions.append(e)

        # If rutvikqatest@outlook is found and is primary, sign out 
        elif await page.locator("div").filter(has_text=re.compile(fr"{o13}")).get_by_label("Sign out").is_visible():
                await page.locator("div").filter(has_text=re.compile(fr"{o13}")).get_by_label("Sign out").click() 
                await page.get_by_role("button", name="Sign Out").click()
                try:
                    await verify_signed_out(page)
                except Exception as e:
                    exceptions.append(e)
                logging.info("Signed out of Outlook (primary)")
        # Try forced signout when only 1 is properly connected
        elif await page.get_by_label("Sign out").is_visible():
                await page.get_by_label("Sign out").click()
                await page.get_by_role("button", name="Sign Out").click()
                try:
                    await verify_signed_out(page)
                except Exception as e:
                    exceptions.append(e)
                logging.info("Signed out of Outlook")
        elif await page.locator("div").filter(has_text=re.compile(fr"{o21}")).get_by_label("Sign out").is_visible():
            await page.locator("div").filter(has_text=re.compile(fr"{o21}")).get_by_label("Sign out").click()
            await page.get_by_role("button", name="Sign Out").click()
            try:
                await verify_signed_out(page)
            except Exception as e:
                exceptions.append(e)
            logging.info("Signed out of Outlook")
        else:
            logging.info("skipped outlook signout")
        
        

        # # Random choice to either remove or keep one of the reconnect accounts
        # random_n= random.choice([4,2])
        # reconnect_decision = random.choice([True, False])
        # if reconnect_decision == False:
        #     try:
        #         page.get_by_role("button").nth(random_n).click()
        #         page.get_by_role("button", name="Sign Out").click()
        #     except Exception as e: 
        #         logging.error(f"By tapping n={random_n}, error occured: {str(e)}")

        # if rutvik@bluemind is in reconnect, then reconnect
        if await page.locator("div").filter(has_text=re.compile(r"^rutvik@bluemind\.app$")).get_by_label("Reconnect").is_visible():   
            async with page.expect_popup() as popup:
                await page.locator("div").filter(has_text=re.compile(r"^rutvik@bluemind\.app$")).get_by_label("Reconnect").click()
            popup = await popup.value
            await utils.google(popup, google_account, google_password)
            logging.info("Reconnected to Google")
            await expect(page.get_by_text("Gmail account connected")).to_be_visible()

        elif await page.get_by_label("Reconnect").is_visible():
            async with page.expect_popup() as popup:
                await page.get_by_label("Reconnect").click()
            popup = await popup.value
            await utils.google(popup, google_account, google_password)
            logging.info("Reconnected to Google")
            await expect(page.get_by_text("Gmail account connected")).to_be_visible()
        else:
            logging.info("skipped google reconnect")

    # If outlook is still in reconnect, then reconnect
        if await page.locator("div").filter(has_text=re.compile(r"^rutvikqatest@outlook\.com$")).get_by_label("Reconnect").is_visible(): 
            await page.locator("div").filter(has_text=re.compile(r"^rutvikqatest@outlook\.com$")).get_by_label("Reconnect").click()
            await utils.outlook(page, outlook_account, outlook_password)
            logging.info("Reconnected to Outlook")
            # await expect(page.get_by_text("Outlook account connected")).to_be_visible()

        elif await page.get_by_label("Reconnect").is_visible():
            async with page.expect_popup() as popup:
                await page.get_by_label("Reconnect").click()
            popup = await popup.value
            await utils.outlook(page, outlook_account, outlook_password)
            logging.info("Reconnected to Outlook")
            # await expect(page.get_by_text("Outlook account connected")).to_be_visible()
        else:
            logging.info("skipped outlook reconnect")
    
        # If gmail is not connected, then connect gmail
        if await page.locator("div").filter(has_text=re.compile(r"^Add Google Account$")).get_by_role("img").is_visible():   
            async with page.expect_popup() as popup_info:
                await page.locator("div").filter(has_text=re.compile(r"^Add Google Account$")).get_by_role("img").click()
            popup = await popup_info.value
            await utils.google(popup, google_account, google_password)
            logging.info("Connected to Google")
            await expect(page.get_by_text("Gmail account connected")).to_be_visible()
        else:
            logging.info("skipped google connection")
        await page.wait_for_timeout(3000)
        # If outlook is not connected, then connect outlook
        if await page.locator("div").filter(has_text=re.compile(r"^Add Microsoft Account$")).get_by_role("img").is_visible():
            await page.locator("div").filter(has_text=re.compile(r"^Add Microsoft Account$")).get_by_role("img").click()
            await utils.outlook(page, outlook_account, outlook_password)
            # await expect(page.get_by_text("Outlook account connected")).to_be_visible()
            logging.info("Connected to Outlook")
        else:
            logging.info("skipped outlook connection")

        # Change primary account
        try:
            await page.locator("div").filter(has_text=re.compile(r"^rutvik@bluemind\.app$")).locator("div").first.hover()
        except:
            await page.locator("div").filter(has_text=re.compile(r"^rutvikqatest@outlook\.com$")).locator("div").first.hover()

        try:
            await page.locator("div").filter(has_text=re.compile(r"^Make Primary$")).nth(1).click()
            await page.get_by_role("button", name="Yes").click()
            logging.info("Switched primary account")
            await expect(page.get_by_text("Primary account updated")).to_be_visible()
        except:
            pass    

        # After all these, decide to log out or not for both accounts
        decision = random.choice([True, False])
        logging.info(f"Decision to log out: {decision}")

        if decision:
            #Try to find the primary and sign out of it
            try:
                await page.locator("div").filter(has_text=re.compile(fr"{o13}")).get_by_label("Sign out").click() 
                logging.info("trying sign out of Outlook")
            except:
                await page.locator("div").filter(has_text=re.compile(fr"{o15}")).get_by_label("Sign out").click()
                logging.info("trying sign out of Google")

            await page.get_by_role("button", name="Sign Out").click()
            await verify_signed_out(page) 
            
            second_decision = random.choice([True, False])
            # logging.info(f"Decision to log out of 2nd account: {second_decision}")

            # Signs out of the 2nd account if the decision is True
            if second_decision:
                await page.get_by_label("Sign Out").click()
                await page.get_by_role("button", name="Sign Out").click()
                logging.info("signed out of 2nd account aswell")
                await verify_signed_out(page)
    except Exception as e:
        exceptions.append(e)
    # return exceptions    

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
            await page1.goto("https://staging.bluemind.app/social-accounts")
            response_handler, request_handler = await utils.start_handler_async(page1, api_urls)
            await asyncio.gather(
                accounts(page1)
            )
            await utils.stop_handler_async(page1, api_urls, response_handler, request_handler)
        
        except Exception as e:  # Save trace if failure
            exceptions.append(e)
            await utils.stop_trace(script_name, contexts)
        
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
    if not utils.is_recent_state(state_path):
        subprocess.run(['python', script_path], check=True)
    try:
        exceptions.extend(asyncio.run(run()))
        utils.start_report(test_results, script_name)
    except Exception as e:
        exceptions.append(e)  # Collect exceptions
    finally:
        if exceptions:
            utils.traceback_error_logging_exp(script_name, exceptions)
        utils.end_report(test_results, script_name)
        

