#!/usr/bin/env python3
"""Publish chapter 18 with proper dialog handling"""

from playwright.sync_api import sync_playwright
import time

URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"

CHAPTER_NUM = "18"
CHAPTER_TITLE = "第二起命案"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第18章.md"

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
print(f"Content length: {len(content)} chars")

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    print(f"Total pages: {len(context.pages)}")
    
    # Find the target publish page
    target_page = None
    for i, pg in enumerate(context.pages):
        url = pg.url
        title = pg.title()
        print(f"  Page {i}: {url[:80]}")
        if "enter_from=newchapter" in url and "publish" in url:
            target_page = pg
    
    if target_page is None:
        target_page = context.pages[0]
        print("Using first page")
    
    page = target_page
    print(f"Using page: {page.url[:80]}")
    
    # Navigate fresh
    print("Navigating to publish page...")
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)
    
    # Check for draft dialog
    print("Checking for draft dialog...")
    try:
        discard_btn = page.get_by_text("放弃", exact=False)
        if discard_btn.is_visible(timeout=3000):
            print("Clicking '放弃'...")
            discard_btn.click()
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f"No draft dialog: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v4_step1.png")
    
    # Fill chapter number - use JavaScript to set value directly
    print("\nFilling chapter number...")
    try:
        # The first input is chapter number (text input with no placeholder)
        input0 = page.locator('input[type="text"]').first
        input0.click()
        input0.fill(CHAPTER_NUM)
        print(f"Filled: {CHAPTER_NUM}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Fill title
    print("Filling title...")
    try:
        title_input = page.locator('input[placeholder="请输入标题"]')
        if title_input.is_visible(timeout=3000):
            title_input.click()
            title_input.fill(CHAPTER_TITLE)
            print(f"Filled title: {CHAPTER_TITLE}")
        else:
            # Try second input
            inputs = page.locator('input').all()
            if len(inputs) > 1:
                inputs[1].click()
                inputs[1].fill(CHAPTER_TITLE)
                print(f"Filled title via input[1]")
    except Exception as e:
        print(f"Error: {e}")
    
    page.wait_for_timeout(500)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v4_step2.png")
    
    # Fill content using JavaScript to ensure it sticks
    print("\nFilling content...")
    try:
        content_area = page.locator('.ql-editor').first
        if content_area.is_visible(timeout=3000):
            content_area.click()
            # Use keyboard to select all and replace
            content_area.click()
            page.keyboard.press("Control+A")
            page.wait_for_timeout(200)
            content_area.fill(content)
            print(f"Filled content: {len(content)} chars")
        else:
            textarea = page.locator('textarea').first
            if textarea.is_visible():
                textarea.fill(content)
                print(f"Filled via textarea")
    except Exception as e:
        print(f"Error: {e}")
    
    page.wait_for_timeout(2000)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v4_step3.png")
    
    # Check word count
    try:
        body_text = page.locator('body').text_content()
        if "4316" in body_text or "4602" in body_text:
            print("Content appears to be filled correctly")
        else:
            # Try to find any number near "正文字数"
            import re
            match = re.search(r'正文字数\s*(\d+)', body_text)
            if match:
                print(f"Word count: {match.group(1)}")
            else:
                print("Could not find word count")
    except Exception as e:
        print(f"Error checking: {e}")
    
    # Click next
    print("\nClicking next...")
    try:
        next_btn = page.get_by_role("button", name="下一步")
        next_btn.click()
        print("Clicked next")
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v4_step4.png")
    
    # Handle risk detection dialog if it appears
    print("Checking for risk dialog...")
    try:
        confirm_btn = page.get_by_role("button", name="确定")
        if confirm_btn.is_visible(timeout=3000):
            print("Risk dialog appeared, clicking '确定'...")
            confirm_btn.click()
            page.wait_for_timeout(2000)
    except Exception as e:
        print(f"No risk dialog or already dismissed: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v4_step5.png")
    
    # Now look for publish button
    print("\nLooking for publish button...")
    try:
        # Try "发布" button
        publish_btn = page.get_by_role("button", name="发布")
        if publish_btn.is_visible(timeout=3000):
            print("Found '发布' button, clicking...")
            publish_btn.click()
            page.wait_for_timeout(3000)
        else:
            # Maybe it's already on confirm page, look for confirm
            confirm_btn2 = page.get_by_role("button", name="确认")
            if confirm_btn2.is_visible(timeout=3000):
                print("Found '确认' button, clicking...")
                confirm_btn2.click()
                page.wait_for_timeout(3000)
            else:
                print("No publish/confirm button visible")
    except Exception as e:
        print(f"Error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v4_final.png")
    
    print(f"\nFinal URL: {page.url}")
    
    # Verify what happened
    final_text = page.locator('body').text_content()
    if "发布成功" in final_text or "已完成" in final_text:
        print("✅ Publication appears successful!")
    else:
        print("⚠️ Could not confirm publication success")
        # Check current state
        if "第18章" in final_text or "第二起命案" in final_text:
            print("✅ Chapter info is present")
        if "4316" in final_text or "4602" in final_text:
            print("✅ Content is present")
    
    print("\nDone!")