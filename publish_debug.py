#!/usr/bin/env python3
"""Debug and publish chapter 12 - step by step with more visibility"""

from playwright.sync_api import sync_playwright
import time

CHAPTER_NUM = "12"
CHAPTER_TITLE = "地下赌场"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第12章.md"

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
    page = context.pages[0]
    
    print(f"Current page URL: {page.url}")
    
    # Navigate to the publish page
    URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(URL, timeout=30000)
    page.wait_for_load_state("networkidle", timeout=30000)
    time.sleep(3)
    
    print(f"After navigation URL: {page.url}")
    
    # Dismiss any dialogs
    try:
        page.keyboard.press("Escape")
        time.sleep(1)
    except:
        pass
    
    # Check for dialog with "放弃" button
    try:
        discard = page.get_by_role("button", name="放弃")
        if discard.is_visible():
            print("Found dialog, clicking 放弃...")
            discard.click()
            time.sleep(1)
    except:
        pass
    
    print(f"Page title: {page.title()}")
    
    # Save screenshot
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/debug1.png")
    print("Saved debug1.png")
    
    # Get visible text
    try:
        text = page.evaluate("document.body.innerText")
        print(f"Page text (first 300 chars): {text[:300]}")
    except Exception as e:
        print(f"Could not get page text: {e}")
    
    # Look for title input - the placeholder should be "请输入标题"
    try:
        title_input = page.locator('input[placeholder="请输入标题"]')
        if title_input.is_visible():
            print("Found title input!")
            title_input.fill(CHAPTER_TITLE)
            print(f"Filled: {CHAPTER_TITLE}")
        else:
            print("Title input not visible with placeholder query")
    except Exception as e:
        print(f"Title input error: {e}")
    
    time.sleep(1)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/debug2.png")
    print("Saved debug2.png - after title fill")
    
    # Look for content area - Quill uses .ql-editor
    try:
        editor = page.locator('.ql-editor')
        if editor.is_visible():
            print("Found .ql-editor!")
            # Clear it first
            editor.click()
            time.sleep(0.5)
            # Select all and replace
            editor.fill(content)
            print(f"Filled content: {len(content)} chars")
        else:
            print(".ql-editor not visible")
    except Exception as e:
        print(f"Content area error: {e}")
    
    time.sleep(2)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/debug3.png")
    print("Saved debug3.png - after content fill")
    
    # Check what we have now
    try:
        text = page.evaluate("document.body.innerText")
        print(f"Page text after content (first 500 chars):\n{text[:500]}")
    except Exception as e:
        print(f"Could not get page text: {e}")
    
    # Try clicking "下一步"
    try:
        next_btn = page.get_by_text("下一步")
        if next_btn.is_visible():
            print("Clicking 下一步...")
            next_btn.click()
            time.sleep(3)
            page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/debug4.png")
            print("Saved debug4.png - after next")
    except Exception as e:
        print(f"Next button error: {e}")
    
    print(f"\nFinal URL: {page.url}")
    try:
        text = page.evaluate("document.body.innerText")
        print(f"Final page text (first 500 chars):\n{text[:500]}")
    except:
        pass

    print("\n=== Done ===")