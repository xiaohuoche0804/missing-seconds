#!/usr/bin/env python3
"""Publish chapter 12 - use Playwright CDP without browser.contexts"""

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
    # Connect using HTTP CDP endpoint
    browser = p.chromium.connect("http://127.0.0.1:18800")
    print(f"Connected to browser")
    print(f"Browser contexts: {len(browser.contexts)}")
    
    # Get the default context
    ctx = browser.contexts[0]
    print(f"Context pages: {len(ctx.pages)}")
    
    # Use the first page
    page = ctx.pages[0]
    print(f"Current URL: {page.url}")
    
    # Navigate
    url = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(url, wait_until="domcontentloaded", timeout=25000)
    time.sleep(5)
    print(f"After nav URL: {page.url}")
    
    # Fill chapter number - using nth to get specific input
    print("Filling chapter number...")
    try:
        inputs = page.locator('input[type="text"]').all()
        for i, inp in enumerate(inputs):
            ph = inp.get_attribute('placeholder') or 'none'
            print(f"  [{i}] placeholder='{ph}', visible={inp.is_visible()}")
    except Exception as e:
        print(f"Input list error: {e}")
    
    # Fill using the nth input directly  
    try:
        page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
        print("  Chapter number filled")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.5)
    
    # Fill title
    print("Filling title...")
    try:
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print("  Title filled")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.5)
    
    # Fill content - click on editor and type
    print("Filling content...")
    try:
        # Find the main editor - it's the div with "请输入正文" text
        editor = page.locator('.syl-editor').first
        editor.click()
        time.sleep(0.5)
        # Select all and type
        page.keyboard.press("Control+a")
        time.sleep(0.2)
        page.keyboard.type(content, delay=2)
        print(f"  Content typed: {len(content)} chars")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(3)
    
    # Take a screenshot to see state
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_s3.png")
    print("Screenshot saved")
    
    # Click next
    print("Clicking 下一步...")
    try:
        page.get_by_text("下一步").click()
        print("  Clicked")
        time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_s4.png")
    
    # Click publish
    print("Clicking publish...")
    for btn in ["发布", "确认发布", "完成", "确认"]:
        try:
            if page.get_by_text(btn).is_visible():
                page.get_by_text(btn).click()
                print(f"  Clicked: {btn}")
                time.sleep(3)
                break
        except:
            pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_s5.png")
    
    print(f"\nFinal URL: {page.url}")
    
    try:
        text = page.inner_text('body')
        if '发布成功' in text or '已发布' in text:
            print("✅ SUCCESS!")
        else:
            print("⚠️ Check screenshots")
    except Exception as e:
        print(f"Error: {e}")
    
    browser.close()
    print("Done")