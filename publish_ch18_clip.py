#!/usr/bin/env python3
"""Publish chapter 18 - using clipboard paste for content"""

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
    page = context.pages[0]
    
    print(f"\nNavigating...")
    page.goto(PUBLISH_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    print(f"URL: {page.url[:80]}")
    
    # Handle draft dialog FIRST
    print("\nHandling draft dialog...")
    try:
        discard = page.get_by_text("放弃")
        if discard.is_visible(timeout=3000):
            discard.click()
            print("Dismissed draft")
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f"No draft dialog: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/clip_s1.png")
    
    # Fill chapter and title
    print("\nFilling chapter and title...")
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    page.wait_for_timeout(500)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/clip_s2.png")
    
    # Fill content using clipboard paste
    print("\nFilling content via clipboard...")
    
    try:
        editor = page.locator('.ql-editor').first
        editor.click()
        page.wait_for_timeout(300)
        
        # Select all and clear
        page.keyboard.press("Control+A")
        page.wait_for_timeout(200)
        page.keyboard.press("Delete")
        page.wait_for_timeout(200)
        
        # Paste from clipboard - use the page keyboard API directly
        # We'll set clipboard via JS first
        escaped_content = content.replace('\\', '\\\\').replace('`', '\\`')
        js_code = """
        () => {
            window.__pasteContent = `CONTENT_PLACEHOLDER`.replace(/\\n/g, '\n');
        }
        """.replace('CONTENT_PLACEHOLDER', escaped_content)
        page.evaluate(js_code)
        
        # Now trigger paste
        page.keyboard.press("Control+V")
        page.wait_for_timeout(3000)
        
        print("Pasted content via clipboard")
    except Exception as e:
        print(f"Paste error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/clip_s3.png")
    
    # Check word count
    page_text = page.locator('body').text_content()
    import re
    wc = re.search(r'正文字数\s*(\d+)', page_text)
    if wc:
        print(f"Word count: {wc.group(1)}")
        if int(wc.group(1)) > 0:
            print("Content filled!")
    else:
        print("Could not find word count")
    
    # Click Next
    print("\nClicking Next...")
    try:
        page.get_by_role("button", name="下一步").click()
        print("Clicked Next")
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Next error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/clip_s4.png")
    
    # Handle risk dialog
    try:
        confirm = page.get_by_role("button", name="确定")
        if confirm.is_visible(timeout=2000):
            confirm.click()
            print("Confirmed")
            page.wait_for_timeout(2000)
    except:
        pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/clip_s5.png")
    
    # Publish
    print("\nPublishing...")
    try:
        publish = page.get_by_role("button", name="发布")
        if publish.is_visible(timeout=5000):
            publish.click()
            print("Clicked Publish")
            page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Publish error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/clip_final.png")
    
    print(f"\nFinal URL: {page.url}")
    
    final_text = page.locator('body').text_content()
    if "成功" in final_text or "发布成功" in final_text:
        print("PUBLICATION SUCCESS!")
    elif "第18章" in final_text or "第二起命案" in final_text:
        print("Chapter visible")
        wc2 = re.search(r'正文字数\s*(\d+)', final_text)
        if wc2:
            print(f"   Word count: {wc2.group(1)}")
    else:
        print("Check screenshots")
        if "存草稿" in final_text:
            print("  -> Save draft button visible, content not submitted")
        if "下一步" in final_text:
            print("  -> Next button visible, still on editing page")
    
    print("\nDone!")