#!/usr/bin/env python3
"""Publish chapter 18 properly - using correct page targeting"""

from playwright.sync_api import sync_playwright
import time

URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"

CHAPTER_NUM = "18"
CHAPTER_TITLE = "第二起命案"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第18章.md"

# Read content
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
print(f"First 100 chars: {content[:100]}")

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    print(f"Total pages in browser: {len(context.pages)}")
    
    # List all pages
    for i, pg in enumerate(context.pages):
        print(f"  Page {i}: url={pg.url}, title={pg.title()[:50]}")
    
    # Try to find a page that has the publish URL already loaded
    target_page = None
    for pg in context.pages:
        if "publish" in pg.url and "763848" in pg.url:
            target_page = pg
            print(f"Found target page at index {context.pages.index(pg)}")
            break
    
    # If not found, use the first page
    if target_page is None:
        target_page = context.pages[0] if context.pages else context.new_page()
        print(f"Using first page")
    
    page = target_page
    
    print(f"\nUsing page: {page.url}")
    
    # Navigate if needed
    if "publish" not in page.url or "enter_from=newchapter" not in page.url:
        print("Navigating to publish page...")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
    else:
        print("Already on publish page, refreshing...")
        page.reload(wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
    
    # Check for draft dialog
    print("Looking for draft dialog...")
    try:
        # Look for any dialog or modal
        dialogs = page.locator('[role="dialog"], .modal, .ant-modal, .dialog').all()
        for d in dialogs:
            try:
                if d.is_visible():
                    print(f"Found dialog: {d.text_content()[:100]}")
                    # Try to click discard/abandon button
                    discard_btn = page.get_by_text("放弃", exact=False)
                    if discard_btn.is_visible():
                        print("Clicking '放弃'...")
                        discard_btn.click()
                        page.wait_for_timeout(1000)
            except:
                pass
    except Exception as e:
        print(f"Dialog check: {e}")
    
    page.wait_for_timeout(2000)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/step1_initial.png")
    print("Screenshot step 1 saved")
    
    # Get all inputs
    print("\nInspecting inputs...")
    inputs = page.locator('input').all()
    print(f"Found {len(inputs)} inputs")
    for i, inp in enumerate(inputs):
        try:
            info = f"Input {i}: type={inp.get_attribute('type')}, placeholder={inp.get_attribute('placeholder')}"
            val = inp.input_value()
            if val:
                info += f", value={val[:30]}"
            print(f"  {info}")
        except Exception as e:
            print(f"  Input {i}: error - {e}")
    
    # Fill chapter number (the first text input)
    print("\nFilling chapter number...")
    try:
        # Find the first text input (should be chapter number)
        input0 = page.locator('input[type="text"]').first
        if input0.is_visible():
            input0.click()
            input0.fill(CHAPTER_NUM)
            print(f"Filled chapter number: {CHAPTER_NUM}")
    except Exception as e:
        print(f"Error filling chapter number: {e}")
    
    # Fill title
    print("Filling title...")
    try:
        title_input = page.locator('input[placeholder="请输入标题"]')
        if not title_input.is_visible():
            title_input = page.locator('input').nth(1)
        if title_input.is_visible():
            title_input.click()
            title_input.fill(CHAPTER_TITLE)
            print(f"Filled title: {CHAPTER_TITLE}")
    except Exception as e:
        print(f"Error filling title: {e}")
    
    page.wait_for_timeout(1000)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/step2_filled.png")
    
    # Fill content
    print("\nFilling content...")
    try:
        # Try Quill editor first
        content_area = page.locator('.ql-editor').first
        if not content_area.is_visible():
            content_area = page.locator('[contenteditable="true"]').first
        if not content_area.is_visible():
            content_area = page.locator('textarea').first
        
        if content_area.is_visible():
            content_area.click()
            # Clear first
            content_area.fill("")
            content_area.fill(content)
            print(f"Filled content: {len(content)} chars")
        else:
            print("Content area not visible!")
    except Exception as e:
        print(f"Error filling content: {e}")
    
    page.wait_for_timeout(2000)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/step3_content.png")
    
    # Get word count
    try:
        word_count_text = page.locator('.word-count, [class*="word"], .count').first.text_content()
        print(f"Word count display: {word_count_text}")
    except:
        pass
    
    # Click next
    print("\nClicking next...")
    try:
        next_btn = page.get_by_role("button", name="下一步")
        if next_btn.is_visible():
            next_btn.click()
            print("Clicked next")
            page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Error clicking next: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/step4_next.png")
    
    # Click publish/confirm
    print("\nLooking for publish button...")
    try:
        # Try publish button
        publish_btn = page.get_by_role("button", name="发布")
        if publish_btn.is_visible():
            publish_btn.click()
            print("Clicked publish!")
            page.wait_for_timeout(3000)
        else:
            # Try confirm or other buttons
            confirm_btn = page.get_by_role("button", name="确认")
            if confirm_btn.is_visible():
                confirm_btn.click()
                print("Clicked confirm!")
                page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Error clicking publish: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/step5_final.png")
    
    print(f"\nFinal URL: {page.url}")
    print(f"Page title: {page.title()}")
    
    # Get visible text to verify
    try:
        body = page.locator('body')
        text = body.text_content()[:500]
        print(f"\nPage text preview: {text}")
    except:
        pass
    
    print("\nAll screenshots saved!")