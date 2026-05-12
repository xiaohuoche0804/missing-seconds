#!/usr/bin/env python3
"""Publish Chapter 10 '照片' to fanqienovel - minimal fast script"""

from playwright.sync_api import sync_playwright
import os
import tempfile

CHAPTER_ID = "7638477068807701054"
WRITER_ID = "7637711913522056254"
CHAPTER_NUM = "10"
CHAPTER_TITLE = "照片"
URL = f"https://fanqienovel.com/main/writer/{WRITER_ID}/publish/{CHAPTER_ID}?enter_from=modifychapter"

def main():
    print(f"Publishing Chapter {CHAPTER_NUM}: {CHAPTER_TITLE}")

    # Use a fresh temporary profile
    tmpdir = tempfile.mkdtemp(prefix="fq_ch10_")
    print(f"Using profile: {tmpdir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("Navigating...")
            page.goto(URL, wait_until="load", timeout=20000)
            page.wait_for_timeout(2000)

            print("Checking for draft dialog...")
            try:
                discard = page.get_by_text("放弃", exact=False)
                if discard.is_visible(timeout=2000):
                    print("  Clicking 放弃...")
                    discard.click()
                    page.wait_for_timeout(1000)
            except Exception as e:
                print(f"  No draft dialog: {e}")

            print("Clicking 下一步...")
            try:
                next_btn = page.get_by_text("下一步", exact=False)
                next_btn.click(timeout=5000)
                print("  Clicked!")
                page.wait_for_timeout(3000)
            except Exception as e:
                print(f"  Click failed: {e}")

            print(f"URL after next: {page.url}")
            print(f"Body: {page.inner_text('body')[:400]}")

            # Look for confirm/publish
            try:
                if page.get_by_text("确认", exact=False).is_visible(timeout=3000):
                    print("Clicking 确认...")
                    page.get_by_text("确认", exact=False).click()
                    page.wait_for_timeout(3000)
            except:
                pass

            print(f"\nFinal URL: {page.url}")
            final = page.inner_text("body")[:300]
            print(f"Final body: {final}")

            if "成功" in final or "已发布" in final or "发布时间" in final:
                print("\n✓ PUBLISH SUCCESS")
            else:
                print("\n? Check status manually")

        finally:
            browser.close()
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == "__main__":
    main()