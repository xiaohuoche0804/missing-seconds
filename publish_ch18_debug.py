#!/usr/bin/env python3
"""Publish chapter 18 - detailed debugging of Quill editor"""

from playwright.sync_api import sync_playwright

CHAPTER_NUM = "18"
CHAPTER_TITLE = "第二起命案"
CONTENT_FILE = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第18章.md"
PUBLISH_URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"

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
print(f"Content first 100: {content[:100]}")

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0]
    
    print(f"Pages: {len(context.pages)}")
    page = context.pages[0]
    
    print(f"\nNavigating...")
    page.goto(PUBLISH_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    
    # Handle draft dialog FIRST
    try:
        discard = page.get_by_text("放弃")
        if discard.is_visible(timeout=3000):
            discard.click()
            print("Dismissed draft")
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f"No draft: {e}")
    
    # Fill chapter and title
    print("\nFilling chapter and title...")
    page.locator('input[type="text"]').first.fill(CHAPTER_NUM)
    page.locator('input[placeholder="请输入标题"]').fill(CHAPTER_TITLE)
    page.wait_for_timeout(500)
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/debug_s1.png")
    
    # Now do detailed debugging of the editor
    print("\nDetailed editor analysis...")
    
    # Check if Quill exists
    quill_exists = page.evaluate("""() => {
        return {
            hasQuill: typeof Quill !== 'undefined',
            hasEditor: document.querySelector('.ql-editor') !== null,
            editorHTML: document.querySelector('.ql-editor') ? document.querySelector('.ql-editor').innerHTML.substring(0, 100) : 'none',
            quillRoot: document.querySelector('.ql-editor') ? document.querySelector('.ql-editor').textContent.length : 0
        };
    }""")
    print(f"Quill status: {quill_exists}")
    
    # Try to trigger Quill properly
    print("\nTrying Quill-compatible paste...")
    
    # Use JS to simulate proper Quill content setting
    # Quill uses a Delta-based system, we need to use paste event properly
    escaped_content = content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
    
    js_code = """
    () => {
        const editor = document.querySelector('.ql-editor');
        if (!editor) return {error: 'no editor'};
        
        // Focus the editor first
        editor.focus();
        
        // Get the Quill instance
        const quill = document.querySelector('.ql-container') ? 
            window.__quill || document.querySelector('[data-quill]')?.__vue__?._value || null : null;
        
        // Try direct innerHTML
        editor.innerHTML = '';
        const lines = `CONTENT_PLACEHOLDER`.split('\\n');
        
        // Insert line by line using text nodes (simulates typing)
        let first = true;
        for (const line of lines) {
            if (!first) {
                editor.appendChild(document.createElement('br'));
            }
            if (line) {
                editor.appendChild(document.createTextNode(line));
            }
            first = false;
        }
        
        // Trigger input event properly
        const inputEvent = new InputEvent('input', {
            bubbles: true,
            cancelable: true,
            inputType: 'insertText',
            data: `CONTENT_PLACEHOLDER`
        });
        editor.dispatchEvent(inputEvent);
        
        // Trigger change event
        const changeEvent = new Event('change', { bubbles: true });
        editor.dispatchEvent(changeEvent);
        
        return {
            editorTextLength: editor.textContent.length,
            editorHTML: editor.innerHTML.substring(0, 200)
        };
    }
    """.replace('CONTENT_PLACEHOLDER', escaped_content)
    
    result = page.evaluate(js_code)
    print(f"JS result: {result}")
    
    page.wait_for_timeout(3000)
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/debug_s2.png")
    
    # Check word count
    page_text = page.locator('body').text_content()
    import re
    wc_match = re.search(r'正文字数\s*(\d+)', page_text)
    if wc_match:
        print(f"Word count: {wc_match.group(1)}")
        if int(wc_match.group(1)) > 0:
            print("Content filled!")
    else:
        print("No word count found")
        # Print page text excerpt
        print(f"Page text excerpt: {page_text[:500]}")
    
    print("\nDone!")