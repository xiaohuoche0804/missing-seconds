#!/usr/bin/env python3
"""Publish chapter 18 - use a dedicated fresh page"""

from playwright.sync_api import sync_playwright

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
print(f"Content preview: {content[:80]}...")

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    print(f"Total pages: {len(context.pages)}")
    
    # Close all pages except one fresh one
    if len(context.pages) > 1:
        for i in range(len(context.pages) - 1, 0, -1):
            try:
                context.pages[i].close()
            except:
                pass
        print(f"Closed extra pages, now have: {len(context.pages)}")
    
    # Use the first (now only) page
    page = context.pages[0]
    print(f"Using page URL: {page.url[:80]}")
    
    # Navigate directly to publish URL
    print("\nNavigating to publish page...")
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(4000)
    
    print(f"After navigation URL: {page.url[:80]}")
    
    # Handle draft dialog
    try:
        discard = page.get_by_text("放弃", exact=False)
        if discard.is_visible(timeout=3000):
            discard.click()
            print("Dismissed draft dialog")
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f"No draft dialog: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v7_s1.png")
    
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
        print(f"Filled title: {CHAPTER_TITLE}")
    except Exception as e:
        print(f"Error: {e}")
    
    page.wait_for_timeout(500)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v7_s2.png")
    
    # Check if we have content area - look for Quill
    print("\nLooking for content editor...")
    
    # First check what elements are on the page
    html = page.content()
    has_quill = '.ql-editor' in html
    has_textarea = '<textarea' in html
    print(f"Has .ql-editor: {has_quill}, Has textarea: {has_textarea}")
    
    if has_quill:
        print("Found Quill editor")
        
        # Try to fill using standard method first
        try:
            editor = page.locator('.ql-editor').first
            if editor.is_visible(timeout=5000):
                editor.click()
                page.wait_for_timeout(500)
                # Select all and replace
                page.keyboard.press("Control+A")
                page.wait_for_timeout(200)
                editor.fill(content)
                print(f"Filled via fill(): {len(content)} chars")
        except Exception as e:
            print(f"Standard fill failed: {e}")
        
        page.wait_for_timeout(2000)
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v7_s3.png")
        
        # Check word count
        page_text = page.locator('body').text_content()
        import re
        wc_match = re.search(r'正文字数\s*(\d+)', page_text)
        if wc_match:
            print(f"Word count: {wc_match.group(1)}")
            
        if wc_match and int(wc_match.group(1)) > 100:
            print("Content looks good!")
        else:
            print("Content not filled properly, trying keyboard typing...")
            # Clear and use keyboard
            try:
                page.locator('.ql-editor').click()
                page.wait_for_timeout(200)
                page.keyboard.press("Control+A")
                page.wait_for_timeout(100)
                # Press Delete to clear
                page.keyboard.press("Delete")
                page.wait_for_timeout(200)
                # Type content
                page.keyboard.type(content, delay=3)
                page.wait_for_timeout(5000)
            except Exception as e:
                print(f"Keyboard typing error: {e}")
            
            page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v7_s4.png")
            
            page_text2 = page.locator('body').text_content()
            wc_match2 = re.search(r'正文字数\s*(\d+)', page_text2)
            if wc_match2:
                print(f"Word count after keyboard: {wc_match2.group(1)}")
    else:
        print("No Quill editor found!")
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v7_no_quill.png")
    
    # Click Next
    print("\nClicking Next...")
    try:
        page.get_by_role("button", name="下一步").click()
        print("Clicked next")
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Next error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v7_s5.png")
    
    # Handle risk dialog
    try:
        confirm = page.get_by_role("button", name="确定")
        if confirm.is_visible(timeout=2000):
            confirm.click()
            print("Confirmed risk dialog")
            page.wait_for_timeout(2000)
    except:
        pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v7_s6.png")
    
    # Click Publish
    print("\nLooking for publish button...")
    try:
        publish = page.get_by_role("button", name="发布")
        if publish.is_visible(timeout=5000):
            publish.click()
            print("Clicked PUBLISH!")
            page.wait_for_timeout(3000)
        else:
            print("'发布' not visible")
    except Exception as e:
        print(f"Publish error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v7_final.png")
    
    print(f"\nFinal URL: {page.url}")
    
    final_text = page.locator('body').text_content()
    if "成功" in final_text or "发布成功" in final_text:
        print("✅ PUBLICATION SUCCESS!")
    elif "第18章" in final_text or "第二起命案" in final_text:
        print("✅ Chapter info visible")
        import re
        wc = re.search(r'正文字数\s*(\d+)', final_text)
        if wc:
            print(f"   Word count: {wc.group(1)}")
    else:
        print("⚠️ Check screenshots")
    
    print("\nDone!")