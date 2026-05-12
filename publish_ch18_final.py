#!/usr/bin/env python3
"""Publish chapter 18 - complete flow with careful element handling"""

from playwright.sync_api import sync_playwright

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
    
    # Always work on first page
    page = context.pages[0]
    
    print(f"\nStep 1: Navigate to publish page")
    page.goto(PUBLISH_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    print(f"URL: {page.url[:80]}")
    
    # Handle draft
    print("\nStep 2: Handle draft dialog")
    try:
        discard = page.get_by_text("放弃")
        if discard.is_visible(timeout=3000):
            discard.click()
            print("Dismissed draft")
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f"No draft: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/final_s1.png")
    
    # Fill inputs
    print("\nStep 3: Fill inputs")
    
    # Chapter number
    try:
        inp0 = page.locator('input[type="text"]').first
        inp0.click()
        inp0.fill(CHAPTER_NUM)
        print(f"Chapter: {CHAPTER_NUM}")
    except Exception as e:
        print(f"Chapter error: {e}")
    
    # Title
    try:
        title = page.locator('input[placeholder="请输入标题"]')
        title.click()
        title.fill(CHAPTER_TITLE)
        print(f"Title: {CHAPTER_TITLE}")
    except Exception as e:
        print(f"Title error: {e}")
    
    page.wait_for_timeout(500)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/final_s2.png")
    
    # Content - use triple approach: clear, focus, type
    print("\nStep 4: Fill content")
    
    try:
        editor = page.locator('.ql-editor')
        if editor.count() > 0:
            print("Found Quill editor")
            
            # Click and select all
            editor.first.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Control+A")
            page.wait_for_timeout(200)
            page.keyboard.press("Delete")
            page.wait_for_timeout(200)
            
            # Type content character by character
            print("Typing content...")
            page.keyboard.type(content, delay=2)
            print(f"Typed {len(content)} chars")
            
            page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Content error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/final_s3.png")
    
    # Check word count
    page_text = page.locator('body').text_content()
    import re
    wc = re.search(r'正文字数\s*(\d+)', page_text)
    if wc:
        print(f"Word count: {wc.group(1)}")
    
    # Next button
    print("\nStep 5: Click next")
    try:
        page.get_by_role("button", name="下一步").click()
        print("Clicked Next")
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Next error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/final_s4.png")
    
    # Handle risk dialog
    try:
        confirm = page.get_by_role("button", name="确定")
        if confirm.is_visible(timeout=2000):
            confirm.click()
            print("Confirmed risk dialog")
            page.wait_for_timeout(2000)
    except:
        pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/final_s5.png")
    
    # Publish
    print("\nStep 6: Publish")
    try:
        publish = page.get_by_role("button", name="发布")
        if publish.is_visible(timeout=5000):
            publish.click()
            print("Clicked PUBLISH!")
            page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Publish error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/final_s6.png")
    
    print(f"\nFinal URL: {page.url}")
    
    final_text = page.locator('body').text_content()
    if "成功" in final_text or "发布成功" in final_text:
        print("✅ PUBLICATION SUCCESS!")
    elif "第18章" in final_text or "第二起命案" in final_text:
        print("✅ Chapter visible")
        wc2 = re.search(r'正文字数\s*(\d+)', final_text)
        if wc2:
            print(f"   Word count: {wc2.group(1)}")
    else:
        print("⚠️ Check screenshots")
    
    print("\nDone!")