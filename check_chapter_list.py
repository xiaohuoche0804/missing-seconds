#!/usr/bin/env python3
"""Check chapter list to see if chapter 18 was saved as draft"""

from playwright.sync_api import sync_playwright

CHAPTER_LIST_URL = "https://fanqienovel.com/main/writer/7637711913522056254/chapter-manage/763847706"

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0]
    
    page = context.pages[0]
    print(f"Using page: {page.url[:80]}")
    
    print("\nNavigating to chapter list...")
    page.goto(CHAPTER_LIST_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/chapter_list_check.png")
    
    # Get page text
    page_text = page.locator('body').text_content()
    print(f"Page text length: {len(page_text)}")
    print(f"Page excerpt: {page_text[:1000]}")
    
    # Look for chapter 18
    if "第18章" in page_text or "第二起命案" in page_text:
        print("\n✅ Chapter 18 found in list!")
    else:
        print("\n⚠️ Chapter 18 NOT found in list")
        
    # Look for all chapter mentions
    import re
    chapters = re.findall(r'第(\d+)章', page_text)
    print(f"\nChapters found: {chapters}")
    
    print("\nDone!")