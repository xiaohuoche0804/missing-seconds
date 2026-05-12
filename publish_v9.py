#!/usr/bin/env python3
"""Final publish chapter 12 - clean approach"""

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
    # Connect via CDP
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
    print(f"Connected")
    
    # Use first context and page
    ctx = browser.contexts[0]
    pages = ctx.pages
    print(f"Pages: {len(pages)}")
    
    if pages:
        page = pages[0]
    else:
        page = ctx.new_page()
    
    print(f"Initial URL: {page.url}")
    
    # Navigate to publish page
    url = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(url, wait_until="domcontentloaded", timeout=25000)
    time.sleep(4)
    print(f"Nav URL: {page.url}")
    
    # Wait a bit more for React to render
    time.sleep(2)
    
    # Try to get all input elements
    print("\nInspecting inputs...")
    try:
        all_inputs = page.query_selector_all('input')
        for i, inp in enumerate(all_inputs):
            try:
                inp_type = inp.get_attribute('type') or 'text'
                inp_ph = inp.get_attribute('placeholder') or ''
                inp_val = inp.input_value()
                visible = inp.is_visible()
                print(f"  [{i}] type={inp_type}, placeholder='{inp_ph}', value='{inp_val}', visible={visible}")
            except:
                pass
    except Exception as e:
        print(f"Error inspecting: {e}")
    
    # Try filling chapter number
    print("\nFilling chapter number...")
    try:
        page.locator('input').first.fill(CHAPTER_NUM)
        print("  OK")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(1)
    
    # Try filling title
    print("Filling title...")
    try:
        page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
        print("  OK")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(1)
    
    # Try filling content - click on the paragraph area first
    print("Filling content...")
    try:
        # Click on the content area
        page.locator('paragraph').filter(has_text="请输入正文").click()
        time.sleep(0.5)
        # Ctrl+A and type
        page.keyboard.press("Control+a")
        time.sleep(0.3)
        page.keyboard.type(content, delay=5)
        print(f"  Done: {len(content)} chars")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(3)
    
    # Check word count
    try:
        body_text = page.inner_text('body')
        if '正文字数' in body_text:
            import re
            match = re.search(r'正文字数\n(\d+)', body_text)
            if match:
                print(f"Word count: {match.group(1)}")
    except:
        pass
    
    # Click 下一步
    print("Clicking 下一步...")
    try:
        page.get_by_text("下一步").click()
        print("  OK")
        time.sleep(5)
    except Exception as e:
        print(f"  Error: {e}")
    
    # Check page state
    print("\nChecking page...")
    try:
        body_text = page.inner_text('body')
        print(f"Body preview: {body_text[:400]}...")
    except:
        pass
    
    # Look for publish button
    print("\nLooking for publish button...")
    for btn_text in ["发布", "确认发布", "完成", "确认"]:
        try:
            if page.get_by_text(btn_text).is_visible():
                page.get_by_text(btn_text).click()
                print(f"  Clicked: {btn_text}")
                time.sleep(3)
                break
        except:
            pass
    
    print(f"\nFinal URL: {page.url}")
    
    try:
        final_text = page.inner_text('body')
        if '发布成功' in final_text:
            print("✅ SUCCESS!")
        elif '已发布' in final_text:
            print("✅ Published!")
        else:
            print("⚠️ Check manually")
    except:
        pass
    
    browser.close()
    print("\nDone!")