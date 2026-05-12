#!/usr/bin/env python3
"""Launch fresh browser and publish chapter 12"""

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
print(f"Content: {len(content)} chars")

with sync_playwright() as p:
    # Launch a completely fresh browser (not connecting to existing)
    browser = p.chromium.launch(headless=False)
    print(f"Launched browser")
    
    ctx = browser.new_context()
    print(f"Created context")
    
    page = ctx.new_page()
    print(f"Created page")
    
    # Navigate
    url = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    print(f"URL: {page.url}")
    
    # Fill chapter number
    print("Filling chapter number...")
    try:
        page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
        print("  OK")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
    
    # Fill title
    print("Filling title...")
    try:
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print("  OK")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
    
    # Fill content - click on the paragraph/editor area
    print("Filling content...")
    try:
        # Find the content area - the paragraph with placeholder text
        para = page.locator('paragraph').filter(has_text="请输入正文")
        if para.is_visible():
            para.click()
            time.sleep(0.5)
            page.keyboard.press("Control+a")
            time.sleep(0.2)
            page.keyboard.type(content, delay=3)
            print(f"  OK: {len(content)} chars")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(3)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/fresh_s3.png")
    print("Screenshot s3")
    
    # Check word count
    try:
        body = page.inner_text('body')
        import re
        match = re.search(r'正文字数\n(\d+)', body)
        if match:
            print(f"Word count: {match.group(1)}")
    except:
        pass
    
    # Click 下一步
    print("Clicking 下一步...")
    try:
        page.get_by_text("下一步").click()
        print("  OK")
        time.sleep(5)
    except Exception as e:
        print(f"  Error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/fresh_s4.png")
    print("Screenshot s4")
    
    # Check for publish button
    print("Looking for publish button...")
    time.sleep(2)
    try:
        body = page.inner_text('body')
        print(f"Body preview: {body[:300]}...")
    except:
        pass
    
    for btn in ["发布", "确认发布", "完成", "确认"]:
        try:
            if page.get_by_text(btn).is_visible():
                page.get_by_text(btn).click()
                print(f"  Clicked: {btn}")
                time.sleep(3)
                break
        except:
            pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/fresh_s5.png")
    print("Screenshot s5")
    
    print(f"\nFinal URL: {page.url}")
    
    try:
        text = page.inner_text('body')
        if '发布成功' in text:
            print("✅ SUCCESS!")
        elif '已发布' in text:
            print("✅ Published!")
        else:
            print("⚠️ Check screenshots")
    except Exception as e:
        print(f"Error: {e}")
    
    browser.close()
    print("Done")