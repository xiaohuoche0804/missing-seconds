#!/usr/bin/env python3
"""Publish chapter 18 - fresh connect and work on existing tab"""

from playwright.sync_api import sync_playwright

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
print(f"Content: {len(content)} chars")

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0]
    
    print(f"Pages: {len(context.pages)}")
    
    # Find a page that has the publish form
    publish_page = None
    for pg in context.pages:
        url = pg.url
        if "publish" in url and "writer" in url:
            publish_page = pg
            print(f"Found publish page: {url[:80]}")
            break
    
    if publish_page is None:
        # Use first page
        publish_page = context.pages[0]
        print(f"No publish page found, using: {publish_page.url[:80]}")
    
    page = publish_page
    
    # Check current state
    print(f"\nCurrent URL: {page.url[:80]}")
    page.wait_for_timeout(2000)
    
    # Get page text
    page_text = page.locator('body').text_content()
    import re
    wc = re.search(r'正文字数\s*(\d+)', page_text)
    if wc:
        print(f"Current word count: {wc.group(1)}")
    
    # Find what's on the page
    if "第 18 章" in page_text or "第二起命案" in page_text:
        print("Chapter 18 info is present on this page")
    
    # Check if this is an edit/draft page or a confirm page
    if "发布" in page_text and "存草稿" in page_text:
        print("This appears to be the editing page")
    elif "确认" in page_text or "发布成功" in page_text:
        print("This appears to be a confirmation page")
    
    print("\nPage analysis complete")
    
    # If there's content (word count > 0), try clicking next/publish
    if wc and int(wc.group(1)) > 1000:
        print("\nContent exists, attempting to publish...")
        
        # Click next if button visible
        try:
            next_btn = page.get_by_role("button", name="下一步")
            if next_btn.is_visible():
                next_btn.click()
                print("Clicked Next")
                page.wait_for_timeout(2000)
        except:
            pass
        
        # Handle any dialog
        try:
            page.get_by_role("button", name="确定").click()
            page.wait_for_timeout(1000)
            print("Confirmed dialog")
        except:
            pass
        
        # Click publish
        try:
            page.get_by_role("button", name="发布").click()
            print("Clicked Publish")
            page.wait_for_timeout(3000)
        except:
            pass
        
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v8_result.png")
        print(f"Final URL: {page.url}")
    else:
        print("\nPage has no significant content - need to navigate fresh")
        page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/v8_current.png")
    
    print("\nDone!")