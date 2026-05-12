#!/usr/bin/env python3
"""Publish chapter 18 - direct approach with fresh page"""

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
    
    # Use first page
    page = context.pages[0]
    print(f"Using page URL: {page.url[:80]}")
    
    # Navigate fresh
    print("\nNavigating...")
    page.goto(URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)
    
    # Handle draft dialog
    try:
        discard = page.get_by_text("放弃", exact=False)
        if discard.is_visible(timeout=2000):
            discard.click()
            print("Dismissed draft dialog")
            page.wait_for_timeout(1000)
    except:
        pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v5_s1.png")
    print(f"After navigation - URL: {page.url[:80]}")
    
    # Fill inputs
    print("\nFilling inputs...")
    
    # Chapter number (input index 0)
    try:
        inp0 = page.locator('input[type="text"]').first
        inp0.fill(CHAPTER_NUM)
        print(f"Filled chapter: {CHAPTER_NUM}")
    except Exception as e:
        print(f"Chapter input error: {e}")
    
    # Title
    try:
        title_inp = page.locator('input[placeholder="请输入标题"]')
        if title_inp.is_visible():
            title_inp.fill(CHAPTER_TITLE)
            print(f"Filled title: {CHAPTER_TITLE}")
    except Exception as e:
        print(f"Title input error: {e}")
    
    page.wait_for_timeout(500)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v5_s2.png")
    
    # Content
    print("\nFilling content...")
    try:
        editor = page.locator('.ql-editor').first
        if editor.is_visible(timeout=3000):
            editor.click()
            page.keyboard.press("Control+A")
            page.wait_for_timeout(300)
            editor.fill(content)
            print(f"Filled {len(content)} chars")
    except Exception as e:
        print(f"Content error: {e}")
    
    page.wait_for_timeout(2000)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v5_s3.png")
    
    # Click Next
    print("\nClicking Next...")
    try:
        page.get_by_role("button", name="下一步").click()
        print("Clicked next")
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Next error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v5_s4.png")
    
    # Handle risk dialog
    try:
        confirm = page.get_by_role("button", name="确定")
        if confirm.is_visible(timeout=2000):
            confirm.click()
            print("Confirmed risk detection")
            page.wait_for_timeout(2000)
    except:
        pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v5_s5.png")
    
    # Check page state - look for publish or confirm button
    print("\nChecking page for publish button...")
    page_text = page.locator('body').text_content()
    
    if "发布" in page_text:
        print("Found '发布' in page")
    
    try:
        publish = page.get_by_role("button", name="发布")
        if publish.is_visible(timeout=3000):
            publish.click()
            print("Clicked PUBLISH!")
            page.wait_for_timeout(3000)
        else:
            print("'发布' button not visible")
    except Exception as e:
        print(f"Publish error: {e}")
    
    try:
        confirm = page.get_by_role("button", name="确认")
        if confirm.is_visible(timeout=3000):
            confirm.click()
            print("Clicked CONFIRM!")
            page.wait_for_timeout(3000)
    except:
        pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v5_final.png")
    
    print(f"\nFinal URL: {page.url}")
    
    final_text = page.locator('body').text_content()
    if "成功" in final_text or "已完成" in final_text:
        print("✅ SUCCESS - Publication complete!")
    elif "第18章" in final_text or "第二起命案" in final_text:
        print("✅ Chapter info visible")
    else:
        print("⚠️ Could not confirm - check screenshot")
    
    # Get word count
    import re
    wc = re.search(r'正文字数\s*(\d+)', final_text)
    if wc:
        print(f"Word count: {wc.group(1)}")
    
    print("\nAll screenshots saved with v5_ prefix")