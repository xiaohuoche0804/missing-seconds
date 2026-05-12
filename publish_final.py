#!/usr/bin/env python3
"""Publish chapter 12 to fanqienovel - with correct element selectors"""

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
    
    # Navigate to publish page
    URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(URL, timeout=30000)
    page.wait_for_load_state("networkidle", timeout=30000)
    time.sleep(3)
    
    print(f"Page title: {page.title()}")
    print(f"URL: {page.url}")
    
    # Step 1: Fill chapter number (input[0] - no placeholder, first input)
    print("\n[Step 1] Filling chapter number...")
    try:
        num_input = page.locator('input').first
        if num_input.is_visible():
            num_input.fill(CHAPTER_NUM)
            print(f"  Filled chapter number: {CHAPTER_NUM}")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
    
    # Step 2: Fill title
    print("\n[Step 2] Filling title...")
    try:
        title_input = page.locator('input[placeholder="请输入标题"]')
        if title_input.is_visible():
            title_input.fill(CHAPTER_TITLE)
            print(f"  Filled title: {CHAPTER_TITLE}")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
    
    # Step 3: Fill content - use evaluate to set innerText on the contenteditable div
    print("\n[Step 3] Filling content...")
    try:
        editor = page.locator('.syl-editor')
        if editor.is_visible():
            editor.click()
            time.sleep(0.5)
            # Use evaluate to set content since fill doesn't work on divs
            page.evaluate("""
                (content) => {
                    const editor = document.querySelector('.syl-editor');
                    editor.innerText = content;
                    // Trigger input event for reactivity
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                }
            """, content)
            print(f"  Filled content: {len(content)} chars")
        else:
            print("  Editor not visible")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(2)
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/step3.png")
    print("  Saved step3.png")
    
    # Check current state
    try:
        text = page.evaluate("document.body.innerText")
        if '正文至少输入1000字' in text:
            print("  ⚠️ Warning: Page shows '正文至少输入1000字'")
    except:
        pass
    
    # Step 4: Click "下一步"
    print("\n[Step 4] Clicking 下一步...")
    try:
        next_btn = page.get_by_text("下一步")
        if next_btn.is_visible():
            next_btn.click()
            print("  Clicked 下一步")
            time.sleep(3)
    except Exception as e:
        print(f"  Error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/step4.png")
    print("  Saved step4.png")
    
    # Step 5: Click publish button (may be "发布" or similar)
    print("\n[Step 5] Looking for publish button...")
    time.sleep(2)
    
    # Check what's on page now
    try:
        text = page.evaluate("document.body.innerText")
        print(f"  Page text preview: {text[:400]}...")
    except:
        pass
    
    # Try clicking publish-related buttons
    for btn_name in ["发布", "确认发布", "完成", "确认"]:
        try:
            btn = page.get_by_text(btn_name)
            if btn.is_visible():
                print(f"  Clicking '{btn_name}'...")
                btn.click()
                time.sleep(3)
                break
        except:
            pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/step5.png")
    print("  Saved step5.png")
    
    print(f"\n=== Final URL: {page.url} ===")
    
    # Check for success indicators
    try:
        final_text = page.evaluate("document.body.innerText")
        if '发布成功' in final_text or 'success' in final_text.lower():
            print("✅ Publish appears successful!")
        elif '草稿' in final_text or '保存' in final_text:
            print("⚠️ Content may be saved as draft - needs manual check")
        else:
            print("⚠️ Could not confirm publish - check screenshot")
    except:
        pass
    
    print("\nDone!")