#!/usr/bin/env python3
"""Check chapter list and verify chapter 12 status"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    ctx = browser.contexts[0]
    page = ctx.pages[0]
    
    # Go to chapter list
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254/chapter-list", timeout=20000)
    time.sleep(5)
    
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")
    
    body = page.inner_text('body')
    print(f"Body preview: {body[:600]}")
    
    # Look for chapter 12
    if '第12章' in body or '地下赌场' in body:
        print("\n✅ Chapter 12 found!")
    else:
        print("\n⚠️ Chapter 12 not found in list")
    
    browser.close()