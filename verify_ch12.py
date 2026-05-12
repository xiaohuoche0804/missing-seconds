#!/usr/bin/env python3
"""Verify chapter 12 was published"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    ctx = browser.contexts[0]
    page = ctx.pages[0]
    
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254/chapter-list", timeout=20000)
    time.sleep(3)
    print(f"URL: {page.url}")
    
    body = page.inner_text('body')
    print(f"Body preview: {body[:500]}")
    
    browser.close()