#!/usr/bin/env python3
"""Publish chapter 12 - minimize page interactions"""

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
    print(f"Page URL: {page.url}")
    
    # Navigate
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter", 
              wait_until="domcontentloaded", timeout=20000)
    time.sleep(3)
    
    # Fill chapter number and title via locator
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    print("Filled number and title")
    
    # Fill content via JS
    page.evaluate("""
        (c) => {
            const e = document.querySelector('.serial-editor-content .syl-editor') || 
                      document.querySelectorAll('.syl-editor')[0];
            if(e) e.innerText = c;
        }
    """, content)
    print("Filled content via JS")
    
    time.sleep(2)
    
    # Click next
    page.get_by_text("下一步").click()
    time.sleep(5)
    
    # Click publish
    for btn in ["发布", "确认发布", "完成", "确认"]:
        try:
            page.get_by_text(btn).click(timeout=3000)
            print(f"Clicked {btn}")
            time.sleep(3)
            break
        except:
            pass
    
    print(f"Final URL: {page.url}")
    body = page.inner_text('body')
    print(f"Body preview: {body[:200]}...")
    
    browser.close()
    print("Done")