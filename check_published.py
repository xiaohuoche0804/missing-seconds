#!/usr/bin/env python3
"""Check published chapters and verify chapter 18 status"""

from playwright.sync_api import sync_playwright

# Navigate to the novel's chapter list
URL = "https://fanqienovel.com/main/writer/7637711913522056254/article"

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    print(f"Using existing browser with {len(context.pages)} pages")
    
    print("Navigating to chapter list...")
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)
    
    print(f"Page title: {page.title()}")
    print(f"Current URL: {page.url}")
    
    # Take screenshot
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/chapter_list.png")
    print("Screenshot saved to chapter_list.png")
    
    # Try to find chapter list content
    print("\nLooking for chapter list...")
    try:
        # Get all headings
        headings = page.locator('h1, h2, h3, h4, h5, h6').all()
        for h in headings:
            try:
                if h.is_visible():
                    print(f"Heading: {h.text_content()}")
            except:
                pass
    except Exception as e:
        print(f"Error getting headings: {e}")
    
    # Try to get text content that might show chapters
    print("\nLooking for chapter info...")
    try:
        # Find any text containing "第" and "章"
        all_text = page.locator('body').text_content()
        chapters_found = []
        for line in all_text.split('\n'):
            if '第' in line and '章' in line and len(line.strip()) < 100:
                chapters_found.append(line.strip())
        print(f"Found {len(chapters_found)} chapter references")
        for ch in chapters_found[:20]:
            print(f"  {ch}")
    except Exception as e:
        print(f"Error finding chapters: {e}")
    
    print("Done!")