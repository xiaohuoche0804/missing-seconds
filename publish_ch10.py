#!/usr/bin/env python3
"""Publish Chapter 10 '照片' to fanqienovel - targeted script"""

from playwright.sync_api import sync_playwright
import sys

CHAPTER_ID = "7638477068807701054"
WRITER_ID = "7637711913522056254"
CHAPTER_NUM = "10"
CHAPTER_TITLE = "照片"
URL = f"https://fanqienovel.com/main/writer/{WRITER_ID}/publish/{CHAPTER_ID}?enter_from=modifychapter"

def main():
    print(f"Publishing Chapter {CHAPTER_NUM}: {CHAPTER_TITLE}")
    print(f"URL: {URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()

        print("Step 1: Navigate to chapter edit page...")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        print("Step 2: Handle draft dialog if present...")
        try:
            discard_btn = page.get_by_text("放弃", exact=False)
            if discard_btn.is_visible(timeout=3000):
                print("  Found draft dialog, clicking '放弃'...")
                discard_btn.click()
                page.wait_for_timeout(1000)
        except Exception as e:
            print(f"  No draft dialog: {e}")

        print("Step 3: Wait for form to stabilize...")
        page.wait_for_timeout(3000)

        # Check current state
        print("Step 4: Check page state...")
        try:
            next_btn = page.get_by_text("下一步", exact=False)
            if next_btn.is_visible(timeout=5000):
                print(f"  '下一步' button visible, disabled={next_btn.get_attribute('disabled')}")
                # Check chapter number and title fields
                body_text = page.inner_text("body")
                if "第10章" in body_text or "10" in body_text:
                    print("  Chapter number field has '10' - form is good")
                if "照片" in body_text:
                    print("  Title field has '照片' - form is good")
        except Exception as e:
            print(f"  Could not find '下一步' button: {e}")

        print("Step 5: Click '下一步'...")
        try:
            next_btn = page.get_by_text("下一步", exact=False)
            next_btn.click()
            print("  Clicked '下一步' successfully")
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"  Failed to click '下一步': {e}")
            # Try via evaluate
            page.evaluate("() => { const btns = Array.from(document.querySelectorAll('button')); const next = btns.find(b => b.innerText.trim()==='下一步'); if(next) next.click(); }")
            page.wait_for_timeout(3000)

        print("Step 6: Check URL after clicking next...")
        print(f"  Current URL: {page.url}")

        print("Step 7: Look for publish confirmation dialog...")
        page.wait_for_timeout(2000)
        body_text = page.inner_text("body")
        print(f"  Body text preview: {body_text[:500]}")

        if "发布" in body_text or "确认" in body_text or "时间" in body_text:
            print("  Found publish confirmation dialog - clicking confirm...")
            try:
                confirm_btn = page.get_by_text("确认", exact=False)
                confirm_btn.click()
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  Could not find confirm button: {e}")
                try:
                    publish_btn = page.get_by_text("发布", exact=False)
                    publish_btn.click()
                    page.wait_for_timeout(2000)
                except Exception as e2:
                    print(f"  Could not find publish button: {e2}")

        print("Step 8: Final check...")
        final_url = page.url
        final_text = page.inner_text("body")
        print(f"  Final URL: {final_url}")
        print(f"  Final body preview: {final_text[:300]}")

        if "成功" in final_text or "已发布" in final_text:
            print("✓ PUBLISH SUCCESS")
        elif "下一步" in final_text:
            print("! Still on same page - need further interaction")
        else:
            print(f"? Unexpected final state")

        browser.close()

if __name__ == "__main__":
    main()