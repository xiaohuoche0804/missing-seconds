#!/usr/bin/env python3
"""One-shot publish chapter 12"""

from playwright.sync_api import sync_playwright
import time, sys

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
print(f"Content: {len(content)} chars", flush=True)

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        print("Connected", flush=True)
        
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        
        # Navigate fresh
        print("Navigating...", flush=True)
        page.goto("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter", 
                  wait_until="domcontentloaded", timeout=20000)
        time.sleep(3)
        print(f"URL: {page.url}", flush=True)
        
        # Fill chapter number
        page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
        print("Chapter number filled", flush=True)
        time.sleep(0.5)
        
        # Fill title
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print("Title filled", flush=True)
        time.sleep(0.5)
        
        # Fill content via JS
        page.evaluate("""
            (c) => {
                const e = document.querySelector('.serial-editor-content .syl-editor') || 
                          document.querySelector('.syl-editor');
                if(e) { e.innerText = c; }
            }
        """, content)
        print("Content filled via JS", flush=True)
        time.sleep(2)
        
        # Click 下一步
        print("Clicking 下一步...", flush=True)
        page.get_by_text("下一步").click()
        time.sleep(5)
        print(f"URL after next: {page.url}", flush=True)
        
        # Click publish button
        print("Clicking publish...", flush=True)
        for btn in ["发布", "确认发布", "完成", "确认"]:
            try:
                if page.get_by_text(btn).is_visible(timeout=3000):
                    page.get_by_text(btn).click()
                    print(f"Clicked: {btn}", flush=True)
                    time.sleep(3)
                    break
            except:
                pass
        
        print(f"Final URL: {page.url}", flush=True)
        
        # Get page text to confirm
        text = page.inner_text('body')
        print(f"Page text preview: {text[:200]}...", flush=True)
        
        if '发布成功' in text or '已发布' in text:
            print("✅ SUCCESS!", flush=True)
        elif '审核' in text:
            print("✅ Submitted for review!", flush=True)
        else:
            print("⚠️ Check manually", flush=True)
        
        browser.close()
        
except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("Done", flush=True)