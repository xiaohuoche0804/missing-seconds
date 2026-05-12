#!/usr/bin/env python3
"""Publish chapter 12 to fanqienovel - fixed selectors"""

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
    
    # Step 1: Fill chapter number
    print("\n[Step 1] Filling chapter number...")
    try:
        num_input = page.locator('input').first
        if num_input.is_visible():
            num_input.fill(CHAPTER_NUM)
            print(f"  Done: {CHAPTER_NUM}")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
    
    # Step 2: Fill title
    print("\n[Step 2] Filling title...")
    try:
        title_input = page.locator('input[placeholder="请输入标题"]')
        if title_input.is_visible():
            title_input.fill(CHAPTER_TITLE)
            print(f"  Done: {CHAPTER_TITLE}")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
    
    # Step 3: Fill content - find the editor with "请输入正文" placeholder
    print("\n[Step 3] Filling content...")
    try:
        # The main editor contains text "请输入正文"
        # Use locator that filters by text
        editor = page.locator('.serial-editor-container .syl-editor').first
        if editor.is_visible():
            # Click first to focus
            editor.click()
            time.sleep(0.3)
            # Set content via JS
            page.evaluate("""(content) => {
                const editors = document.querySelectorAll('.serial-editor-container .syl-editor');
                if (editors[0]) {
                    editors[0].innerText = content;
                }
            }""", content)
            print(f"  Done: {len(content)} chars")
        else:
            print("  Editor not visible")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(2)
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/s3.png")
    print("  Saved s3.png")
    
    # Check word count
    try:
        body = page.locator('body').inner_text()
        if '正文字数' in body:
            # Extract word count
            import re
            match = re.search(r'正文字数\n(\d+)', body)
            if match:
                print(f"  Current word count: {match.group(1)}")
    except:
        pass
    
    # Step 4: Click "下一步"
    print("\n[Step 4] Clicking 下一步...")
    try:
        next_btn = page.get_by_text("下一步")
        if next_btn.is_visible():
            next_btn.click()
            print("  Clicked")
            time.sleep(5)  # Wait longer for navigation
    except Exception as e:
        print(f"  Error: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/s4.png")
    print("  Saved s4.png")
    
    print(f"  URL after next: {page.url}")
    
    # Step 5: Click publish button
    print("\n[Step 5] Looking for publish button...")
    time.sleep(2)
    
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
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/s5.png")
    print("  Saved s5.png")
    
    print(f"\n=== Final URL: {page.url} ===")
    
    try:
        final_text = page.evaluate("document.body.innerText")
        if '发布成功' in final_text:
            print("✅ Publish successful!")
        elif '已发布' in final_text:
            print("✅ Chapter appears published!")
        else:
            print("⚠️ Check screenshots - manual verification may be needed")
            print(f"Page text: {final_text[:300]}...")
    except Exception as e:
        print(f"Error checking result: {e}")
    
    print("\nDone!")