#!/usr/bin/env python3
"""Publish chapter 18 - wait for page load properly"""

from playwright.sync_api import sync_playwright
import time

CHAPTER_NUM = "18"
CHAPTER_TITLE = "第二起命案"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第18章.md"
PUBLISH_URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"

# Read content
with open(CONTENT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

body_lines = []
skip_until_blank = True
for line in lines:
    if skip_until_blank:
        if line.strip() == "":
            skip_until_blank = False
        continue
    body_lines.append(line)

content = "".join(body_lines).strip()
print(f"Content: {len(content)} chars")

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0]
    
    print(f"Pages: {len(context.pages)}")
    page = context.pages[0]
    
    print(f"\nNavigating to publish URL...")
    page.goto(PUBLISH_URL, wait_until="load", timeout=30000)
    
    print("Waiting for page to settle...")
    page.wait_for_timeout(8000)
    
    print(f"URL after wait: {page.url[:80]}")
    print(f"Title: {page.title()}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/wait_s1.png")
    
    # Check what's on the page
    page_text = page.locator('body').text_content()
    print(f"Page text length: {len(page_text)}")
    
    # Check for Quill
    quill_check = page.evaluate("""() => {
        const editor = document.querySelector('.ql-editor');
        return {
            hasEditor: !!editor,
            editorVisible: editor ? getComputedStyle(editor).display !== 'none' : false,
            bodyHTML: document.body.innerHTML.substring(0, 500)
        };
    }""")
    print(f"Quill check: {quill_check}")
    
    # Handle draft if present
    try:
        discard = page.get_by_text("放弃")
        if discard.is_visible(timeout=3000):
            discard.click()
            print("Dismissed draft")
            page.wait_for_timeout(2000)
    except Exception as e:
        print(f"No draft: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/wait_s2.png")
    
    # Try to wait for Quill editor specifically
    print("\nWaiting for Quill editor...")
    try:
        page.wait_for_selector('.ql-editor', timeout=10000)
        print("Quill editor found!")
    except Exception as e:
        print(f"Quill not found: {e}")
        # Check if there's any textarea or other editor
        html = page.content()
        if '<textarea' in html:
            print("Found textarea!")
        if 'quill' in html.lower():
            print("Quill mentioned in HTML")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/wait_s3.png")
    
    # Try to fill anyway
    print("\nAttempting to fill inputs...")
    try:
        page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print("Filled chapter and title")
    except Exception as e:
        print(f"Input fill error: {e}")
    
    page.wait_for_timeout(1000)
    
    # Try to click and paste in editor
    print("\nAttempting to fill content...")
    try:
        # Wait for any contenteditable
        page.wait_for_selector('[contenteditable="true"]', timeout=5000)
        editor = page.locator('[contenteditable="true"]').first
        editor.click()
        page.wait_for_timeout(500)
        page.keyboard.press("Control+A")
        page.wait_for_timeout(200)
        page.paste(content)
        print("Pasted content")
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Content fill error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/wait_s4.png")
    
    # Check word count
    page_text2 = page.locator('body').text_content()
    import re
    wc = re.search(r'正文字数\s*(\d+)', page_text2)
    if wc:
        print(f"Word count: {wc.group(1)}")
    
    print("\nDone!")