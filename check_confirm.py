#!/usr/bin/env python3
"""Check the publish result - navigate to confirm page"""

from playwright.sync_api import sync_playwright

# The URL from the previous run that seemed to have content
URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/7638483104562151998?enter_from=newchapter"

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    print(f"Using existing browser with {len(context.pages)} pages")
    
    print("Navigating to the publish result page...")
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)
    
    print(f"Page title: {page.title()}")
    print(f"Current URL: {page.url}")
    
    # Take screenshot
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/publish_confirm.png")
    print("Screenshot saved to publish_confirm.png")
    
    # Inspect the page
    print("\nInspecting page content...")
    try:
        # Look for any visible text
        body = page.locator('body')
        text = body.text_content()[:2000]
        print(f"Page text (first 2000 chars):\n{text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Look for buttons
    print("\nLooking for buttons...")
    try:
        buttons = page.locator('button').all()
        for i, btn in enumerate(buttons):
            try:
                if btn.is_visible():
                    print(f"  Button {i}: {btn.text_content()}")
            except:
                pass
    except Exception as e:
        print(f"Error finding buttons: {e}")
    
    print("Done!")