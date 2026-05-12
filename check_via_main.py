#!/usr/bin/env python3
"""Check chapter list via main writer page"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    ctx = browser.contexts[0]
    page = ctx.pages[0]
    
    # Start from main writer page
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254", timeout=20000)
    time.sleep(5)
    print(f"URL: {page.url}")
    
    body = page.inner_text('body')
    print(f"Body preview: {body[:400]}")
    
    # Click on chapter manage if visible
    try:
        page.get_by_text("章节管理").click()
        time.sleep(3)
        print(f"After chapter manage click: {page.url}")
        body2 = page.inner_text('body')
        if '第12章' in body2 or '地下赌场' in body2:
            print("✅ Chapter 12 found!")
        else:
            print(f"Body: {body2[:400]}")
    except Exception as e:
        print(f"Error: {e}")
    
    browser.close()