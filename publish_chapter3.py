#!/usr/bin/env python3
"""Publish chapter 12 to fanqienovel - using existing user browser, step by step"""

from playwright.sync_api import sync_playwright

CHAPTER_NUM = "12"
CHAPTER_TITLE = "地下赌场"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第12章.md"

# Read content - strip metadata lines (first 2 lines with chapter info)
with open(CONTENT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Skip first 2 lines (chapter number and title), keep everything else as body
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
    
    print(f"Using existing browser, current URL: {page.url}")
    
    # Go to the new chapter publish URL
    URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    print(f"Navigating to {URL}...")
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)
    
    print(f"After navigation URL: {page.url}")
    print(f"Page title: {page.title()}")
    
    # Check for draft dialog - click "放弃" if present
    try:
        dialog = page.locator('button:has-text("放弃")')
        if dialog.is_visible(timeout=3000):
            print("Found draft dialog, clicking '放弃'...")
            dialog.click()
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f"No draft dialog: {e}")
    
    # Now check what's on the page
    print("\n=== Page Snapshot ===")
    page.wait_for_timeout(2000)
    
    # Get all visible text to understand the page structure
    body_text = page.locator('body').inner_text()
    print(f"Body text preview: {body_text[:500]}...")
    
    # Try to find and fill chapter number
    print("\n=== Looking for chapter number input ===")
    try:
        num_input = page.locator('input[type="number"]').first
        if num_input.is_visible(timeout=5000):
            num_input.fill(CHAPTER_NUM)
            print(f"Filled chapter number: {CHAPTER_NUM}")
    except Exception as e:
        print(f"Could not find number input: {e}")
    
    # Try to find and fill title (placeholder contains "请输入标题")
    print("\n=== Looking for title input ===")
    try:
        title_input = page.locator('input[placeholder="请输入标题"]')
        if title_input.is_visible(timeout=5000):
            title_input.fill(CHAPTER_TITLE)
            print(f"Filled title: {CHAPTER_TITLE}")
        else:
            # Try by placeholder text
            all_inputs = page.locator('input').all()
            for inp in all_inputs:
                ph = inp.get_attribute('placeholder') or ''
                if '标题' in ph or '章节' in ph:
                    print(f"Found title input with placeholder: {ph}")
                    inp.fill(CHAPTER_TITLE)
                    break
    except Exception as e:
        print(f"Could not find title input: {e}")
    
    # Find content area
    print("\n=== Looking for content area ===")
    try:
        # Try the Quill editor common class
        content_area = page.locator('.ql-editor').first
        if not content_area.is_visible():
            content_area = page.locator('[contenteditable="true"]').first
        if not content_area.is_visible():
            content_area = page.locator('textarea').first
        
        if content_area.is_visible(timeout=5000):
            content_area.click()
            page.wait_for_timeout(500)
            # Clear and fill
            content_area.fill(content)
            print(f"Pasted content: {len(content)} chars")
    except Exception as e:
        print(f"Could not find content area: {e}")
    
    page.wait_for_timeout(2000)
    
    # Click "下一步"
    print("\n=== Clicking Next ===")
    try:
        next_btn = page.get_by_text("下一步", exact=False)
        if next_btn.is_visible(timeout=5000):
            print("Clicking next button...")
            next_btn.click()
            page.wait_for_timeout(3000)
            print(f"URL after next: {page.url}")
    except Exception as e:
        print(f"Could not find next button: {e}")
    
    # Click "发布" or "确认发布"
    print("\n=== Clicking Publish ===")
    try:
        # Look for publish-related button text
        for btn_text in ["发布", "确认", "完成", "提交"]:
            btn = page.get_by_text(btn_text, exact=False)
            if btn.is_visible(timeout=3000):
                print(f"Clicking '{btn_text}' button...")
                btn.click()
                page.wait_for_timeout(3000)
                break
    except Exception as e:
        print(f"Could not find publish button: {e}")
    
    print(f"\nFinal URL: {page.url}")
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/publish_result2.png")
    print("Screenshot saved to publish_result2.png")
    
    # Final check
    final_text = page.locator('body').inner_text()
    if '发布成功' in final_text or 'success' in final_text.lower():
        print("✅ Publish appears successful!")
    else:
        print("⚠️ Could not confirm publish success - manual check needed")
        print(f"Final body text: {final_text[:300]}...")

    print("Done!")