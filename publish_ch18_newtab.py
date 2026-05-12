#!/usr/bin/env python3
"""Publish chapter 18 - fresh new tab approach"""

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
    
    print(f"Initial pages: {len(context.pages)}")
    
    # Create a fresh new page/tab
    new_page = context.new_page()
    print(f"Created new page")
    
    print(f"\nNavigating to publish URL on new page...")
    new_page.goto(PUBLISH_URL, wait_until="load", timeout=30000)
    new_page.wait_for_timeout(8000)
    
    print(f"URL: {new_page.url[:80]}")
    page_text = new_page.locator('body').text_content()
    print(f"Page text length: {len(page_text)}")
    
    new_page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/tab_s1.png")
    
    # Check for draft dialog
    try:
        discard = new_page.get_by_text("放弃")
        if discard.is_visible(timeout=3000):
            discard.click()
            print("Dismissed draft")
            new_page.wait_for_timeout(2000)
    except Exception as e:
        print(f"No draft: {e}")
    
    new_page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/tab_s2.png")
    
    # Check for Quill editor
    has_quill = new_page.evaluate("""() => !!document.querySelector('.ql-editor')""")
    print(f"Has Quill: {has_quill}")
    
    if has_quill:
        print("\nFilling content via Quill...")
        try:
            editor = new_page.locator('.ql-editor').first
            editor.click()
            new_page.wait_for_timeout(500)
            new_page.keyboard.press("Control+A")
            new_page.wait_for_timeout(200)
            new_page.keyboard.press("Delete")
            new_page.wait_for_timeout(200)
            
            # Type content
            new_page.keyboard.type(content, delay=3)
            print(f"Typed {len(content)} chars")
            new_page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Quill fill error: {e}")
    else:
        # Try textarea
        print("\nTrying textarea...")
        try:
            textarea = new_page.locator('textarea').first
            textarea.fill(content)
            print(f"Filled textarea with {len(content)} chars")
            new_page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Textarea error: {e}")
    
    new_page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/tab_s3.png")
    
    # Check word count
    page_text2 = new_page.locator('body').text_content()
    import re
    wc = re.search(r'正文字数\s*(\d+)', page_text2)
    if wc:
        print(f"Word count: {wc.group(1)}")
    else:
        print("No word count")
        print(f"Page excerpt: {page_text2[:300]}")
    
    # Fill chapter and title
    print("\nFilling chapter and title...")
    try:
        new_page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
        new_page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print("Filled inputs")
    except Exception as e:
        print(f"Input error: {e}")
    
    new_page.wait_for_timeout(500)
    new_page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/tab_s4.png")
    
    # Check word count again
    page_text3 = new_page.locator('body').text_content()
    wc3 = re.search(r'正文字数\s*(\d+)', page_text3)
    if wc3:
        print(f"Word count: {wc3.group(1)}")
    
    # Click Next
    print("\nClicking Next...")
    try:
        new_page.get_by_role("button", name="下一步").click()
        print("Clicked Next")
        new_page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Next error: {e}")
    
    new_page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/tab_s5.png")
    
    # Handle risk dialog
    try:
        confirm = new_page.get_by_role("button", name="确定")
        if confirm.is_visible(timeout=2000):
            confirm.click()
            new_page.wait_for_timeout(2000)
    except:
        pass
    
    new_page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/tab_s6.png")
    
    # Publish
    print("\nPublishing...")
    try:
        publish = new_page.get_by_role("button", name="发布")
        if publish.is_visible(timeout=5000):
            publish.click()
            new_page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Publish error: {e}")
    
    new_page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/tab_final.png")
    
    print(f"\nFinal URL: {new_page.url}")
    
    final_text = new_page.locator('body').text_content()
    if "成功" in final_text or "发布成功" in final_text:
        print("PUBLICATION SUCCESS!")
    elif "第18章" in final_text or "第二起命案" in final_text:
        print("Chapter visible")
        wc_final = re.search(r'正文字数\s*(\d+)', final_text)
        if wc_final:
            print(f"   Word count: {wc_final.group(1)}")
    
    print("\nDone!")