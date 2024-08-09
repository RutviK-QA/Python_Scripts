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

async def main():
    script_name = await utils.script_name()  # Await the asynchronous function
    print(script_name)

# Run the main async function
asyncio.run(main())