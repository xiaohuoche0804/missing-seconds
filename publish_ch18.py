#!/usr/bin/env python3
"""Publish chapter 18 to fanqienovel - using existing user browser"""

from playwright.sync_api import sync_playwright

URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"

CHAPTER_NUM = "18"
CHAPTER_TITLE = "第二起命案"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第18章.md"

# Read content - strip metadata lines (first 2 lines with chapter info)
with open(CONTENT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Skip first 2 lines (chapter number and title), keep everything else as body
body_lines = []
skip_until_blank = True
for line in lines:
    if skip_until_blank:
        if line.strip() == "":
            skip_until_blank = False
        continue
    body_lines.append(line)

content = "".join(body_lines).strip()
print(f"Content length: {len(content)} chars")

with sync_playwright() as p:
    # Connect to existing Chrome via CDP
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    print(f"Using existing browser with {len(context.pages)} pages")
    
    print("Navigating to publish page...")
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)
    
    # Check for draft dialog
    print("Looking for draft dialog...")
    try:
        discard_btn = page.get_by_text("放弃", exact=False)
        if discard_btn.is_visible(timeout=3000):
            print("Found draft dialog, clicking '放弃'...")
            discard_btn.click()
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f"No draft dialog or already dismissed: {e}")
    
    print(f"Page title: {page.title()}")
    print(f"Current URL: {page.url}")
    
    page.wait_for_timeout(2000)
    
    # Find and fill chapter number first
    print("Looking for chapter number input...")
    try:
        inputs = page.locator('input').all()
        print(f"Found {len(inputs)} inputs on page")
        for i, inp in enumerate(inputs):
            try:
                print(f"  Input {i}: type={inp.get_attribute('type')}, placeholder={inp.get_attribute('placeholder')}, value={inp.input_value()[:50] if inp.input_value() else 'empty'}")
            except:
                print(f"  Input {i}: could not get info")
    except Exception as e:
        print(f"Error inspecting inputs: {e}")
    
    try:
        # Try to find by placeholder containing "章节"
        chapter_input = page.locator('input[placeholder*="章节"]').first
        if chapter_input.is_visible(timeout=5000):
            chapter_input.fill(CHAPTER_NUM)
            print(f"Filled chapter number: {CHAPTER_NUM}")
    except Exception as e:
        print(f"Could not find chapter number input: {e}")
    
    # Find and fill title
    print("Looking for title input...")
    try:
        title_input = page.locator('input[placeholder*="标题"]').first
        if not title_input.is_visible():
            title_input = page.locator('input[type="text"]').first
        if title_input.is_visible(timeout=5000):
            title_input.fill(CHAPTER_TITLE)
            print(f"Filled title: {CHAPTER_TITLE}")
    except Exception as e:
        print(f"Could not find title input: {e}")
    
    # Find content area and paste
    print("Looking for content area...")
    try:
        # Try to find the content textarea or div
        content_area = page.locator('.ql-editor, [contenteditable="true"], textarea').first
        if content_area.is_visible(timeout=5000):
            content_area.click()
            content_area.fill(content)
            print(f"Pasted content: {len(content)} chars")
        else:
            # Fallback: find any large text area
            textarea = page.locator('textarea').first
            if textarea.is_visible():
                textarea.fill(content)
                print(f"Pasted content via textarea: {len(content)} chars")
    except Exception as e:
        print(f"Could not find content area: {e}")
    
    page.wait_for_timeout(3000)
    
    # Look for next button
    print("Looking for next/step button...")
    try:
        next_btn = page.get_by_text("下一步", exact=False)
        if next_btn.is_visible(timeout=5000):
            next_btn.click()
            print("Clicked next button")
            page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Could not find next button: {e}")
    
    # Check for confirm/publish button
    print("Looking for publish button...")
    try:
        publish_btn = page.get_by_text("发布", exact=False)
        if publish_btn.is_visible(timeout=5000):
            publish_btn.click()
            print("Clicked publish button!")
            page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Could not find publish button: {e}")
    
    print(f"\nFinal URL: {page.url}")
    print(f"Page title: {page.title()}")
    
    # Take screenshot for reference
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/publish_result_ch18.png")
    print("Screenshot saved to publish_result_ch18.png")
    
    print("Done!")