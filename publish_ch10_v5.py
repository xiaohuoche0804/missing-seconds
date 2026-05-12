#!/usr/bin/env python3
"""Try to use existing Chrome session via context storage"""

from playwright.sync_api import sync_playwright
import os

CHAPTER_ID = "7638477068807701054"
WRITER_ID = "7637711913522056254"
URL = f"https://fanqienovel.com/main/writer/{WRITER_ID}/publish/{CHAPTER_ID}?enter_from=modifychapter"

def main():
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome_path, headless=True)
        
        # Try to use first context (existing Chrome profile)
        try:
            context = browser.contexts[0]
            page = context.pages[0]
        except:
            context = browser.new_context()
            page = context.new_page()
        
        print(f"Step 1: Navigate to {URL}")
        page.goto(URL, wait_until="load", timeout=20000)
        page.wait_for_timeout(4000)
        print(f"  URL: {page.url}")
        body = page.inner_text("body")
        print(f"  Body preview: {body[:300]}")
        
        browser.close()

if __name__ == "__main__":
    main()