#!/usr/bin/env python3
"""Publish chapter 18 - use JavaScript to set content in Quill editor"""

from playwright.sync_api import sync_playwright

URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"

CHAPTER_NUM = "18"
CHAPTER_TITLE = "第二起命案"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第18章.md"

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
print(f"Content preview: {content[:80]}...")

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    page = context.pages[0]
    print(f"Using page URL: {page.url[:80]}")
    
    # Navigate
    print("\nNavigating...")
    page.goto(URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)
    
    # Handle draft
    try:
        discard = page.get_by_text("放弃", exact=False)
        if discard.is_visible(timeout=2000):
            discard.click()
            print("Dismissed draft")
            page.wait_for_timeout(1000)
    except:
        pass
    
    # Fill chapter number
    print("\nFilling chapter...")
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    
    # Fill title
    print("Filling title...")
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    page.wait_for_timeout(500)
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_s1.png")
    
    # Fill content using JavaScript - use a separate variable for JS code
    print("\nFilling content via JavaScript...")
    
    # Escape content for JavaScript
    content_escaped = content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
    
    page.click('.ql-editor')
    page.wait_for_timeout(500)
    
    js_template = """
    const editor = document.querySelector('.ql-editor');
    if (editor) {
        editor.innerHTML = '';
        const text = `{CONTENT}`;
        const div = document.createElement('div');
        div.textContent = text;
        editor.appendChild(div);
        editor.dispatchEvent(new Event('input', { bubbles: true }));
        editor.dispatchEvent(new Event('change', { bubbles: true }));
        console.log('Content set, length: ' + text.length);
    } else {
        console.log('Editor not found');
    }
    """
    js_code = js_template.replace('{CONTENT}', content_escaped)
    
    result = page.evaluate(js_code)
    print(f"JS result: {result}")
    
    page.wait_for_timeout(2000)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_s2.png")
    
    # Check word count
    page_text = page.locator('body').text_content()
    import re
    wc_match = re.search(r'正文字数\s*(\d+)', page_text)
    if wc_match:
        print(f"Word count: {wc_match.group(1)}")
    
    if wc_match and int(wc_match.group(1)) > 0:
        print("Content filled successfully!")
    else:
        print("Content still showing 0 - trying keyboard typing...")
        
        # Try keyboard typing
        page.evaluate("""() => {
            const editor = document.querySelector('.ql-editor');
            editor.innerHTML = '';
            editor.dispatchEvent(new Event('focus', { bubbles: true }));
        }""")
        page.wait_for_timeout(300)
        
        page.keyboard.type(content, delay=5)
        page.wait_for_timeout(3000)
        
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_s3.png")
        
        page_text2 = page.locator('body').text_content()
        wc_match2 = re.search(r'正文字数\s*(\d+)', page_text2)
        if wc_match2:
            print(f"Word count after keyboard: {wc_match2.group(1)}")
    
    # Click Next
    print("\nClicking Next...")
    page.get_by_role("button", name="下一步").click()
    page.wait_for_timeout(2000)
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_s4.png")
    
    # Handle risk dialog
    try:
        page.get_by_role("button", name="确定").click()
        page.wait_for_timeout(2000)
        print("Confirmed risk dialog")
    except:
        pass
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_s5.png")
    
    # Look for publish button
    print("\nLooking for publish button...")
    try:
        publish_btn = page.get_by_role("button", name="发布")
        if publish_btn.is_visible(timeout=3000):
            publish_btn.click()
            print("Clicked PUBLISH!")
            page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Publish button not found: {e}")
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v6_final.png")
    
    print(f"\nFinal URL: {page.url}")
    
    final_text = page.locator('body').text_content()
    if "成功" in final_text or "发布成功" in final_text:
        print("✅ PUBLICATION SUCCESS!")
    elif "第18章" in final_text or "第二起命案" in final_text:
        print("✅ Chapter visible")
        wc = re.search(r'正文字数\s*(\d+)', final_text)
        if wc:
            print(f"   Word count: {wc.group(1)}")
    else:
        print("⚠️ Check screenshots")
    
    print("\nDone!")