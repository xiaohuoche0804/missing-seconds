#!/usr/bin/env python3
"""Publish chapter 12 - careful page management"""

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
    
    # Get the correct page - find the one on the publish URL
    target_url = "publish"
    page = None
    for i, ctx_page in enumerate(ctx.pages):
        print(f"  Page {i}: {ctx_page.url}")
        if target_url in ctx_page.url and "chapter-list" not in ctx_page.url:
            page = ctx_page
            print(f"  -> Using page {i}")
    
    if page is None:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print("Using first page")
    
    print(f"Current URL: {page.url}")
    
    # Navigate
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter", 
              wait_until="domcontentloaded", timeout=20000)
    time.sleep(4)
    print(f"Nav URL: {page.url}")
    
    # Fill number
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    time.sleep(0.5)
    
    # Fill title
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    time.sleep(0.5)
    print("Filled number and title")
    
    # Fill content via JS
    page.evaluate("""
        (c) => {
            const e = document.querySelector('.syl-editor');
            if(e) {
                e.innerText = c;
                console.log('Content set, length:', c.length);
            } else {
                console.log('Editor not found');
            }
        }
    """, content)
    print("Content filled via JS")
    
    time.sleep(3)
    
    # Check editor content
    editor_content = page.evaluate("""
        () => {
            const e = document.querySelector('.syl-editor');
            return e ? e.innerText.substring(0, 100) : 'not found';
        }
    """)
    print(f"Editor content: {editor_content}...")
    
    # Click 下一步
    print("Clicking 下一步...")
    page.get_by_text("下一步").click()
    time.sleep(5)
    print(f"URL after next: {page.url}")
    
    # Check the page
    body = page.inner_text('body')
    if '钱多多' in body:
        print("✅ Content confirmed on confirm page!")
    else:
        print("⚠️ Content not confirmed")
    
    # Click publish
    for btn in ["发布", "确认发布"]:
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
    elif '审核' in final_text:
        print("✅ Submitted for review!")
    else:
        print(f"Body: {final_text[:400]}...")
    
    browser.close()
    print("Done")