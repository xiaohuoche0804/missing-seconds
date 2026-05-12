#!/usr/bin/env python3
"""Publish chapter 12 to fanqienovel - minimal version"""

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
    
    print("Checking current page...")
    print(f"  URL: {page.url}")
    print(f"  Title: {page.title()}")
    
    # Navigate to publish page
    URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(URL, timeout=30000)
    page.wait_for_load_state("networkidle", timeout=30000)
    time.sleep(3)
    
    print(f"\nAfter navigation:")
    print(f"  URL: {page.url}")
    print(f"  Title: {page.title()}")
    
    # Fill chapter number
    print("\nFilling chapter number...")
    try:
        page.locator('input').first.fill(CHAPTER_NUM)
        print(f"  Done")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
    
    # Fill title
    print("Filling title...")
    try:
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print(f"  Done")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
    
    # Fill content - try using trix/effectively an editable
    print("Filling content...")
    try:
        # Find the main content editor
        editor_selector = '.serial-editor-container.notranslate .syl-editor'
        page.locator(editor_selector).click()
        time.sleep(0.5)
        # Use Ctrl+A to select all
        page.keyboard.press("Control+a")
        time.sleep(0.3)
        # Type the content (sends one character at a time to avoid issues)
        page.keyboard.type(content, delay=5)  # 5ms delay between chars
        print(f"  Done: {len(content)} chars")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(2)
    
    print("\nClicking 下一步...")
    try:
        page.get_by_text("下一步").click()
        print("  Clicked")
        time.sleep(5)
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\nLooking for publish button...")
    for btn in ["发布", "确认发布", "完成", "确认"]:
        try:
            if page.get_by_text(btn).is_visible():
                page.get_by_text(btn).click()
                print(f"  Clicked '{btn}'")
                time.sleep(3)
                break
        except:
            pass
    
    print(f"\nFinal URL: {page.url}")
    
    try:
        text = page.evaluate("document.body.innerText")
        if '发布成功' in text or '已发布' in text:
            print("✅ Publish SUCCESS!")
        else:
            print("⚠️ Check manually")
            print(f"Page preview: {text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nDone!")