#!/usr/bin/env python3
"""Debug - find correct elements for fanqienovel chapter editor"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    cdp_url = "http://127.0.0.1:18800"
    browser = p.chromium.connect_over_cdp(cdp_url)
    
    context = browser.contexts[0]
    page = context.pages[0]
    
    URL = "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"
    page.goto(URL, timeout=30000)
    page.wait_for_load_state("networkidle", timeout=30000)
    time.sleep(3)
    
    page.screenshot(path="/Users/ganghonghai/Documents/openclaw-novel-workspace/debug_step1.png")
    print("Saved debug_step1.png")
    
    # Find ALL input elements with their attributes
    print("\n=== All INPUT elements ===")
    inputs = page.locator('input').all()
    for i, inp in enumerate(inputs):
        try:
            ph = inp.get_attribute('placeholder') or ''
            typ = inp.get_attribute('type') or 'text'
            val = inp.input_value()[:30] if inp.input_value() else ''
            visible = inp.is_visible()
            print(f"  [{i}] type={typ}, placeholder='{ph}', value='{val}', visible={visible}")
        except Exception as e:
            print(f"  [{i}] error: {e}")
    
    # Find ALL contenteditable elements
    print("\n=== All contenteditable elements ===")
    editable = page.locator('[contenteditable="true"]').all()
    for i, e in enumerate(editable):
        try:
            tag = e.evaluate("el => el.tagName")
            visible = e.is_visible()
            text = e.inner_text()[:50] if e.inner_text() else ''
            print(f"  [{i}] tag={tag}, visible={visible}, text='{text}...'")
        except Exception as e:
            print(f"  [{i}] error: {e}")
    
    # Find textareas
    print("\n=== All TEXTAREA elements ===")
    textareas = page.locator('textarea').all()
    for i, ta in enumerate(textareas):
        try:
            visible = ta.is_visible()
            val = ta.input_value()[:50] if ta.input_value() else ''
            print(f"  [{i}] visible={visible}, value='{val}...'")
        except Exception as e:
            print(f"  [{i}] error: {e}")
    
    # Find div with class containing editor or content
    print("\n=== Looking for editor-like divs ===")
    try:
        editor_divs = page.locator('div[class*="editor"], div[class*="content"], div[class*="ql"]').all()
        for i, d in enumerate(editor_divs):
            try:
                cls = d.get_attribute('class')
                visible = d.is_visible()
                text = d.inner_text()[:50] if d.inner_text() else ''
                print(f"  [{i}] class='{cls}', visible={visible}, text='{text}...'")
            except Exception as e:
                print(f"  [{i}] error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nDone!")