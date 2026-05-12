#!/usr/bin/env python3
"""Publish chapter 18 - wait for Quill to fully load"""

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
    page.goto(PUBLISH_URL, wait_until="domcontentloaded", timeout=30000)
    print(f"Initial URL: {page.url[:80]}")
    
    # Wait for the page to be interactive - wait for specific indicators
    print("Waiting for page to be ready...")
    
    # Wait for network to be idle (no pending requests)
    page.wait_for_load_state("networkidle", timeout=30000)
    print("Network idle")
    
    # Now wait a bit more for Vue to render
    page.wait_for_timeout(5000)
    
    # Check if Quill is now present
    has_quill = page.evaluate("""() => !!document.querySelector('.ql-editor')""")
    print(f"Has Quill after wait: {has_quill}")
    
    if not has_quill:
        print("Quill still not found, trying longer wait...")
        page.wait_for_timeout(5000)
        has_quill = page.evaluate("""() => !!document.querySelector('.ql-editor')""")
        print(f"Has Quill after longer wait: {has_quill}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/ready_s1.png")
    
    # Handle draft if present
    try:
        discard = page.get_by_text("放弃")
        if discard.is_visible(timeout=2000):
            discard.click()
            print("Dismissed draft")
            page.wait_for_timeout(2000)
    except Exception as e:
        print(f"No draft: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/ready_s2.png")
    
    if has_quill:
        print("\nQuill found, proceeding...")
        
        # Fill chapter number
        try:
            page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
            print(f"Filled chapter: {CHAPTER_NUM}")
        except Exception as e:
            print(f"Chapter fill error: {e}")
        
        # Fill title
        try:
            page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
            print(f"Filled title: {CHAPTER_TITLE}")
        except Exception as e:
            print(f"Title fill error: {e}")
        
        page.wait_for_timeout(500)
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/ready_s3.png")
        
        # Fill content - click first then type
        print("\nFilling content...")
        try:
            editor = page.locator('.ql-editor').first
            editor.click()
            page.wait_for_timeout(500)
            
            # Select all and clear
            page.keyboard.press("Control+A")
            page.wait_for_timeout(300)
            page.keyboard.press("Delete")
            page.wait_for_timeout(300)
            
            # Type content
            print(f"Typing {len(content)} chars...")
            page.keyboard.type(content, delay=2)
            page.wait_for_timeout(2000)
            print("Content typed")
        except Exception as e:
            print(f"Content error: {e}")
        
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/ready_s4.png")
        
        # Check word count
        page_text = page.locator('body').text_content()
        import re
        wc = re.search(r'正文字数\s*(\d+)', page_text)
        if wc:
            print(f"Word count: {wc.group(1)}")
        
        # Click Next
        print("\nClicking Next...")
        try:
            page.get_by_role("button", name="下一步").click()
            print("Clicked Next")
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Next error: {e}")
        
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/ready_s5.png")
        
        # Handle risk dialog
        try:
            confirm = page.get_by_role("button", name="确定")
            if confirm.is_visible(timeout=2000):
                confirm.click()
                page.wait_for_timeout(2000)
        except:
            pass
        
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/ready_s6.png")
        
        # Publish
        print("\nPublishing...")
        try:
            publish = page.get_by_role("button", name="发布")
            if publish.is_visible(timeout=5000):
                publish.click()
                page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Publish error: {e}")
        
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/ready_final.png")
        
        print(f"\nFinal URL: {page.url}")
        
        final_text = page.locator('body').text_content()
        if "成功" in final_text or "发布成功" in final_text:
            print("PUBLICATION SUCCESS!")
        elif "第18章" in final_text or "第二起命案" in final_text:
            print("Chapter visible")
            wc_final = re.search(r'正文字数\s*(\d+)', final_text)
            if wc_final:
                print(f"   Word count: {wc_final.group(1)}")
    else:
        print("Could not find Quill editor")
        # Let's see what the page actually contains
        page_text = page.locator('body').text_content()
        print(f"Page text: {page_text[:500]}")
    
    print("\nDone!")