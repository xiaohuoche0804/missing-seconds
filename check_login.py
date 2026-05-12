#!/usr/bin/env python3
"""One-shot: Login first, then edit chapter 10"""

from playwright.sync_api import sync_playwright

CHAPTER_ID = "7638477068807701054"
WRITER_ID = "7637711913522056254"
URL = f"https://fanqienovel.com/main/writer/{WRITER_ID}/publish/{CHAPTER_ID}?enter_from=modifychapter"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Step 1: Check login page")
        page.goto("https://fanqienovel.com/main/writer/login", wait_until="load", timeout=15000)
        page.wait_for_timeout(2000)
        print(f"  Title: {page.title()}")
        print(f"  URL: {page.url}")
        body = page.inner_text("body")
        print(f"  Body: {body[:200]}")
        
        print("\nStep 2: Navigate to chapter edit page")
        page.goto(URL, wait_until="load", timeout=20000)
        page.wait_for_timeout(4000)
        print(f"  URL: {page.url}")
        print(f"  Body: {page.inner_text('body')[:400]}")
        
        browser.close()

if __name__ == "__main__":
    main()