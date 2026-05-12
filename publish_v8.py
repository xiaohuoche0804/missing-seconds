#!/usr/bin/env python3
"""Publish chapter 12 using playwright with explicit CDP URL"""

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
    cdp_url = "http://127.0.0.1:18800"
    
    try:
        browser = p.chromium.connect_over_cdp(cdp_url)
        print(f"Connected to browser via CDP")
        
        ctx = browser.contexts[0]
        page = ctx.pages[0]
        print(f"Current URL: {page.url}")
        
        # Navigate to publish page
        url = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(4)
        print(f"After nav: {page.url}")
        
        # Fill chapter number
        print("Filling chapter number...")
        page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
        
        time.sleep(0.5)
        
        # Fill title
        print("Filling title...")
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        
        time.sleep(0.5)
        
        # Fill content using keyboard
        print("Filling content...")
        editor = page.locator('.syl-editor').first
        editor.click()
        time.sleep(0.5)
        page.keyboard.press("Control+a")
        time.sleep(0.2)
        page.keyboard.type(content, delay=3)
        print(f"  Done: {len(content)} chars")
        
        time.sleep(3)
        
        # Click 下一步
        print("Clicking 下一步...")
        page.get_by_text("下一步").click()
        time.sleep(5)
        
        # Click publish
        print("Clicking publish...")
        for btn in ["发布", "确认发布", "完成", "确认"]:
            if page.get_by_text(btn).is_visible():
                page.get_by_text(btn).click()
                print(f"  Clicked: {btn}")
                time.sleep(3)
                break
        
        print(f"\nFinal URL: {page.url}")
        
        text = page.inner_text('body')
        if '发布成功' in text:
            print("✅ SUCCESS!")
        elif '已发布' in text:
            print("✅ Published!")
        else:
            print("⚠️ Check manually")
            print(f"Body: {text[:300]}...")
        
        browser.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

print("Done")