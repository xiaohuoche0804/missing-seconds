#!/usr/bin/env python3
"""Publish chapter 12 using JS evaluate for content"""

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
    
    ctx = browser.contexts[0]
    page = ctx.pages[0]
    print(f"Current URL: {page.url}")
    
    # Navigate to fresh publish page
    url = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(url, wait_until="domcontentloaded", timeout=20000)
    time.sleep(4)
    print(f"Nav URL: {page.url}")
    
    # Fill chapter number using locator
    print("Filling chapter number...")
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    print("  OK")
    
    time.sleep(0.5)
    
    # Fill title
    print("Filling title...")
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    print("  OK")
    
    time.sleep(0.5)
    
    # Fill content using JS evaluate (bypasses React controlled input issue)
    print("Filling content via JS...")
    page.evaluate("""
        (content) => {
            const e = document.querySelector('.serial-editor-content .syl-editor');
            if(e) {
                e.innerText = content;
                // Also try to dispatch input event for React
                e.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    """, content)
    print(f"  Done: {len(content)} chars")
    
    time.sleep(3)
    
    # Check word count
    print("\nChecking state...")
    try:
        word_count = page.evaluate("""
            () => {
                const body = document.body.innerText;
                const match = body.match(/正文字数\\n(\\d+)/);
                return match ? match[1] : 'not found';
            }
        """)
        print(f"Word count display: {word_count}")
    except Exception as e:
        print(f"Error checking: {e}")
    
    # Also verify content was set
    content_check = page.evaluate("""
        () => {
            const e = document.querySelector('.serial-editor-content .syl-editor');
            return e ? e.innerText.substring(0, 100) : 'not found';
        }
    """)
    print(f"Content preview: {content_check}...")
    
    # Click 下一步
    print("\nClicking 下一步...")
    page.get_by_text("下一步").click()
    print("  OK")
    time.sleep(5)
    
    # Check page after next
    print(f"URL after next: {page.url}")
    
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
    
    # Final check
    final_text = page.evaluate("document.body.innerText")
    if '发布成功' in final_text:
        print("✅ SUCCESS!")
    elif '已发布' in final_text:
        print("✅ Published!")
    elif '审核' in final_text:
        print("✅ Chapter submitted for review!")
    else:
        print("⚠️ Manual check needed")
        print(f"Body: {final_text[:300]}...")
    
    browser.close()
    print("\nDone!")