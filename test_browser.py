#!/usr/bin/env python3
"""Test browser connection and page state"""

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    page = context.pages[0]
    
    print(f"Browser connected, contexts: {len(browser.contexts)}")
    print(f"Pages in context: {len(context.pages)}")
    print(f"Current page URL: {page.url}")
    print(f"Current page title: {page.title()}")
    
    # Try to navigate to a simple URL
    print("\nNavigating to publish URL...")
    try:
        page.goto("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter", timeout=20000)
        print(f"After nav URL: {page.url}")
        print(f"After nav title: {page.title()}")
        
        # Check if page is still alive
        page.wait_for_timeout(3000)
        print(f"After wait URL: {page.url}")
        
        # Take a screenshot
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/test_browser.png")
        print("Screenshot saved")
        
    except Exception as e:
        print(f"Error: {e}")
        # Try with existing page
        print(f"Page still has URL: {page.url}")
    
    browser.close()
    print("Done")