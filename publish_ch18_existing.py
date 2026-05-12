#!/usr/bin/env python3
"""Publish chapter 18 - use existing browser page properly"""

from playwright.sync_api import sync_playwright

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
print(f"Content: {len(content)} chars")

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0]
    
    print(f"Total pages: {len(context.pages)}")
    
    # List all pages
    for i, pg in enumerate(context.pages):
        print(f"  Page {i}: {pg.url[:80]}")
    
    # Find a page with publish in URL, or use first page
    target_page = None
    for pg in context.pages:
        if 'publish' in pg.url and 'writer' in pg.url:
            target_page = pg
            print(f"Found publish page at index {context.pages.index(pg)}")
            break
    
    if target_page is None:
        target_page = context.pages[0]
        print("Using first page")
    
    page = target_page
    print(f"\nUsing page URL: {page.url[:80]}")
    
    # Handle draft dialog if present
    try:
        discard = page.get_by_text("放弃")
        if discard.is_visible(timeout=3000):
            discard.click()
            print("Dismissed draft")
            page.wait_for_timeout(2000)
    except Exception as e:
        print(f"No draft: {e}")
    
    # Wait for Quill
    print("\nWaiting for Quill editor...")
    try:
        page.wait_for_selector('.ql-editor', timeout=15000)
        print("Quill editor found!")
    except Exception as e:
        print(f"Quill not found: {e}")
        # Check what's there
        html = page.content()
        if '.ql-editor' in html:
            print("Quill is in HTML but not visible yet")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/existing_s1.png")
    
    # Get current state
    page_text = page.locator('body').text_content()
    import re
    wc = re.search(r'正文字数\s*(\d+)', page_text)
    if wc:
        print(f"Current word count: {wc.group(1)}")
    
    # Fill chapter number
    print("\nFilling chapter number...")
    try:
        page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
        print(f"Filled: {CHAPTER_NUM}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Fill title
    print("Filling title...")
    try:
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print(f"Filled: {CHAPTER_TITLE}")
    except Exception as e:
        print(f"Error: {e}")
    
    page.wait_for_timeout(500)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/existing_s2.png")
    
    # Fill content
    print("\nFilling content...")
    try:
        editor = page.locator('.ql-editor').first
        editor.click()
        page.wait_for_timeout(500)
        
        # Select all and delete
        page.keyboard.press("Control+A")
        page.wait_for_timeout(200)
        page.keyboard.press("Delete")
        page.wait_for_timeout(200)
        
        # Type content
        print(f"Typing {len(content)} chars...")
        page.keyboard.type(content, delay=2)
        page.wait_for_timeout(2000)
        print("Done typing")
    except Exception as e:
        print(f"Content error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/existing_s3.png")
    
    # Check word count
    page_text2 = page.locator('body').text_content()
    wc2 = re.search(r'正文字数\s*(\d+)', page_text2)
    if wc2:
        print(f"Word count: {wc2.group(1)}")
    
    # Click Next
    print("\nClicking Next...")
    try:
        page.get_by_role("button", name="下一步").click()
        print("Clicked Next")
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Next error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/existing_s4.png")
    
    # Handle risk dialog
    try:
        confirm = page.get_by_role("button", name="确定")
        if confirm.is_visible(timeout=2000):
            confirm.click()
            page.wait_for_timeout(2000)
    except:
        pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/existing_s5.png")
    
    # Publish
    print("\nPublishing...")
    try:
        publish = page.get_by_role("button", name="发布")
        if publish.is_visible(timeout=5000):
            publish.click()
            page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Publish error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/existing_final.png")
    
    print(f"\nFinal URL: {page.url}")
    
    final_text = page.locator('body').text_content()
    if "成功" in final_text or "发布成功" in final_text:
        print("✅ PUBLICATION SUCCESS!")
    elif "第18章" in final_text or "第二起命案" in final_text:
        print("✅ Chapter visible")
        wc_final = re.search(r'正文字数\s*(\d+)', final_text)
        if wc_final:
            print(f"   Word count: {wc_final.group(1)}")
    
    print("\nDone!")