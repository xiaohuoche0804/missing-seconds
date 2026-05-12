#!/usr/bin/env python3
"""Final attempt - publish chapter 12 directly via fresh page"""

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
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    ctx = browser.contexts[0]
    
    # Create a brand new page to avoid any stale state
    page = ctx.new_page()
    print(f"New page", flush=True)
    
    page.goto("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter", 
              wait_until="domcontentloaded", timeout=20000)
    time.sleep(5)
    print(f"URL: {page.url}", flush=True)
    
    # Fill chapter number
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    time.sleep(0.5)
    
    # Fill title
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    time.sleep(0.5)
    print("Filled number and title", flush=True)
    
    # Fill content via JS - use the specific editor div
    page.evaluate("""
        (c) => {
            const editors = document.querySelectorAll('.syl-editor');
            console.log('syl-editor count:', editors.length);
            const e = editors[0];
            if(e) {
                e.innerText = c;
                e.dispatchEvent(new Event('input', {bubbles: true}));
                console.log('Set content, length:', c.length);
            }
        }
    """, content)
    print(f"Filled content via JS", flush=True)
    
    time.sleep(3)
    
    # Check word count
    body = page.inner_text('body')
    import re
    wc = re.search(r'正文字数\n(\d+)', body)
    print(f"Word count: {wc.group(1) if wc else 'not found'}", flush=True)
    
    # Click 下一步
    print("Clicking 下一步...", flush=True)
    page.get_by_text("下一步").click()
    time.sleep(5)
    print(f"URL after next: {page.url}", flush=True)
    
    # Check if we're on the publish confirmation page
    confirm_text = page.inner_text('body')
    print(f"Confirm page preview: {confirm_text[:300]}...", flush=True)
    
    # Click the appropriate publish button
    for btn in ["发布", "确认发布"]:
        try:
            page.get_by_text(btn, exact=True).click(timeout=3000)
            print(f"Clicked exact: {btn}", flush=True)
            time.sleep(3)
            break
        except:
            pass
        try:
            page.get_by_text(btn).click(timeout=3000)
            print(f"Clicked: {btn}", flush=True)
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
    elif '已发布' in final_text:
        print("✅ Already published!", flush=True)
    else:
        print(f"Body: {final_text[:400]}", flush=True)
    
    browser.close()
    print("Done", flush=True)