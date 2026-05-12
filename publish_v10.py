#!/usr/bin/env python3
"""Final publish chapter 12 - complete approach"""

from playwright.sync_api import sync_playwright
import time

CHAPTER_NUM = "12"
CHAPTER_TITLE = "地下赌场"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第12章.md"

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
    # Create fresh browser and context to avoid any session issues
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()
    
    print("Navigating to publish page...")
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter", 
              wait_until="domcontentloaded", timeout=20000)
    time.sleep(5)
    print(f"URL: {page.url}")
    
    # Check if logged in
    if "login" in page.url.lower():
        print("❌ Not logged in!")
        browser.close()
        exit(1)
    
    # Fill chapter number
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    time.sleep(0.5)
    print("Chapter number filled")
    
    # Fill title
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    time.sleep(0.5)
    print("Title filled")
    
    # Click on the content area to focus it first
    content_area = page.locator('.syl-editor').first
    content_area.click()
    time.sleep(0.5)
    
    # Type content using keyboard - this properly triggers React events
    print(f"Typing content ({len(content)} chars)...")
    page.keyboard.type(content, delay=1)
    print("Content typed")
    
    time.sleep(3)
    
    # Check word count
    try:
        body = page.inner_text('body')
        import re
        wc = re.search(r'正文字数\n(\d+)', body)
        print(f"Word count display: {wc.group(1) if wc else 'not found'}")
    except:
        pass
    
    # Click 下一步
    print("Clicking 下一步...")
    page.get_by_text("下一步").click()
    time.sleep(5)
    print(f"URL after next: {page.url}")
    
    # Take screenshot to see current state
    try:
        page.screenshot(path='/tmp/publish_step2.png')
        print("Screenshot saved to /tmp/publish_step2.png")
    except:
        pass
    
    # Look for confirmation text with actual content
    try:
        body = page.inner_text('body')
        # Check if content is actually there
        if '钱多多' in body:
            print("✅ Content confirmed on page!")
        else:
            print("⚠️ Content not visible on page")
        print(f"Page preview: {body[:300]}...")
    except Exception as e:
        print(f"Error checking body: {e}")
    
    # Click publish button
    print("\nLooking for publish button...")
    for btn_text in ["发布", "确认发布", "完成", "确认"]:
        try:
            btns = page.get_by_text(btn_text)
            if btns.count() > 0:
                for btn in btns.all():
                    if btn.is_visible():
                        btn.click()
                        print(f"Clicked: {btn_text}")
                        time.sleep(3)
                        break
        except Exception as e:
            print(f"  {btn_text}: {e}")
    
    print(f"\nFinal URL: {page.url}")
    
    try:
        final_text = page.inner_text('body')
        if '发布成功' in final_text:
            print("✅ SUCCESS! Chapter published!")
        elif '审核' in final_text:
            print("✅ Submitted for review!")
        elif '已发布' in final_text:
            print("✅ Already published!")
        else:
            print(f"Final preview: {final_text[:400]}...")
    except:
        pass
    
    browser.close()
    print("\nDone!")