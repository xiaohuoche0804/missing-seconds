#!/usr/bin/env python3
"""Publish chapter 12 - keyboard.type for content"""

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
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    ctx = browser.contexts[0]
    page = ctx.pages[0]
    
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter", 
              wait_until="domcontentloaded", timeout=20000)
    time.sleep(4)
    print(f"URL: {page.url}")
    
    # Fill number and title
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    print("Filled number and title")
    
    time.sleep(0.5)
    
    # Fill content using keyboard.type - click first to focus
    content_area = page.locator('.serial-editor-content .syl-editor').first
    content_area.click()
    time.sleep(0.5)
    
    # Select all and delete any existing content
    page.keyboard.press("Control+a")
    time.sleep(0.2)
    page.keyboard.press("Delete")
    time.sleep(0.2)
    
    # Type content with small delay
    page.keyboard.type(content, delay=2)
    print(f"Typed content: {len(content)} chars")
    
    time.sleep(3)
    
    # Check word count
    body = page.inner_text('body')
    if '正文字数' in body:
        import re
        match = re.search(r'正文字数\n(\d+)', body)
        if match:
            print(f"Word count: {match.group(1)}")
    
    # Click 下一步
    print("Clicking 下一步...")
    page.get_by_text("下一步").click()
    time.sleep(5)
    
    print(f"URL after next: {page.url}")
    
    # Click publish
    print("Clicking publish...")
    for btn in ["发布", "确认发布", "完成", "确认"]:
        try:
            page.get_by_text(btn).click(timeout=3000)
            print(f"Clicked {btn}")
            time.sleep(3)
            break
        except:
            pass
    
    print(f"Final URL: {page.url}")
    final_text = page.inner_text('body')
    
    if '发布成功' in final_text:
        print("✅ SUCCESS!")
    elif '已发布' in final_text or '审核' in final_text:
        print("✅ Chapter published/submitted!")
    else:
        print(f"Body preview: {final_text[:300]}...")
    
    browser.close()
    print("Done")