#!/usr/bin/env python3
"""Publish chapter 12 - final clean attempt"""

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
print(f"Content: {len(content)} chars", flush=True)

with sync_playwright() as p:
    print("Connecting via CDP...", flush=True)
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    print(f"Connected, contexts: {len(browser.contexts)}", flush=True)
    
    ctx = browser.contexts[0]
    print(f"Pages in context: {len(ctx.pages)}", flush=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    print(f"Initial URL: {page.url}", flush=True)
    
    # Navigate
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter", 
              wait_until="domcontentloaded", timeout=20000)
    time.sleep(4)
    print(f"Nav URL: {page.url}", flush=True)
    
    # Fill chapter number
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    time.sleep(0.3)
    
    # Fill title
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    time.sleep(0.3)
    print("Filled number and title", flush=True)
    
    # Fill content via JS
    page.evaluate("""
        (c) => {
            const e = document.querySelector('.serial-editor-content .syl-editor') || 
                      document.querySelectorAll('.syl-editor')[0];
            if(e) {
                e.innerText = c;
                e.dispatchEvent(new Event('input', {bubbles: true}));
            }
        }
    """, content)
    print(f"Filled content via JS: {len(content)} chars", flush=True)
    
    time.sleep(3)
    
    # Check state
    body = page.inner_text('body')
    import re
    wc = re.search(r'正文字数\n(\d+)', body)
    print(f"Word count display: {wc.group(1) if wc else 'not found'}", flush=True)
    
    # Click 下一步
    print("Clicking 下一步...", flush=True)
    page.get_by_text("下一步").click()
    time.sleep(5)
    print(f"URL after next: {page.url}", flush=True)
    
    # Click publish button
    for btn in ["发布", "确认发布"]:
        try:
            if page.get_by_text(btn).is_visible(timeout=2000):
                page.get_by_text(btn).click()
                print(f"Clicked {btn}", flush=True)
                time.sleep(3)
                break
        except:
            pass
    
    print(f"Final URL: {page.url}", flush=True)
    final_text = page.inner_text('body')
    
    if '发布成功' in final_text:
        print("✅ SUCCESS!", flush=True)
    elif '审核' in final_text:
        print("✅ Submitted for review!", flush=True)
    else:
        print(f"Body: {final_text[:400]}", flush=True)
    
    browser.close()
    print("Done", flush=True)