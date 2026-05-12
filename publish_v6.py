#!/usr/bin/env python3
"""Publish chapter 12 to fanqienovel - robust version"""

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
    
    print("Current page:", page.url)
    
    # Navigate to publish page
    URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(URL, wait_until="commit", timeout=30000)
    time.sleep(5)  # Wait for page to render
    
    print(f"After navigation: {page.url}")
    
    # Fill chapter number
    print("\nFilling chapter number...")
    try:
        page.locator('input').first.fill(CHAPTER_NUM)
        print("  Done")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.3)
    
    # Fill title
    print("Filling title...")
    try:
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print("  Done")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.3)
    
    # Fill content using keyboard.type
    print("Filling content...")
    try:
        editor = page.locator('.serial-editor-container.notranslate .syl-editor').first
        editor.click()
        time.sleep(0.5)
        # Select all and replace
        page.keyboard.press("Control+a")
        time.sleep(0.3)
        page.keyboard.type(content, delay=3)
        print(f"  Done: {len(content)} chars")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(2)
    
    # Click 下一步
    print("\nClicking 下一步...")
    try:
        page.get_by_text("下一步").click()
        print("  Done")
        time.sleep(5)
    except Exception as e:
        print(f"  Error: {e}")
    
    # Click publish
    print("\nClicking publish button...")
    for btn_text in ["发布", "确认发布", "完成", "确认"]:
        try:
            btn = page.get_by_text(btn_text)
            if btn.is_visible():
                btn.click()
                print(f"  Clicked: {btn_text}")
                time.sleep(3)
                break
        except:
            pass
    
    print(f"\nFinal URL: {page.url}")
    
    # Check for success
    try:
        body_text = page.evaluate("document.body.innerText")
        if '发布成功' in body_text:
            print("✅ SUCCESS!")
        elif '已发布' in body_text:
            print("✅ Published!")
        else:
            print("⚠️ Manual check needed")
            print(f"Body: {body_text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print("Done!")