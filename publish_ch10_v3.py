#!/usr/bin/env python3
"""One-shot: Edit chapter 10 via JS evaluate, click next, confirm publish"""

from playwright.sync_api import sync_playwright
import time

CHAPTER_ID = "7638477068807701054"
WRITER_ID = "7637711913522056254"
URL = f"https://fanqienovel.com/main/writer/{WRITER_ID}/publish/{CHAPTER_ID}?enter_from=modifychapter"

SCRIPT = """
() => {
  // 1. Fill chapter number
  var numInput = document.querySelector('.serial-input.byte-input');
  if (numInput) {
    numInput.value = '10';
    numInput.dispatchEvent(new Event('input', {bubbles: true}));
    numInput.dispatchEvent(new Event('change', {bubbles: true}));
  }
  
  // 2. Fill title
  var titleInput = document.querySelector('input[placeholder="请输入标题"]');
  if (titleInput) {
    titleInput.value = '照片';
    titleInput.dispatchEvent(new Event('input', {bubbles: true}));
  }
  
  // 3. Find and click 下一步
  var btns = Array.from(document.querySelectorAll('button'));
  var nextBtn = btns.find(b => b.innerText.trim() === '下一步');
  if (nextBtn) {
    nextBtn.click();
    return 'clicked next, disabled=' + nextBtn.disabled;
  }
  return 'next not found, btns=' + btns.map(b => b.innerText.trim()).join(',');
}
"""

CONFIRM_SCRIPT = """
() => {
  var btns = Array.from(document.querySelectorAll('button'));
  // Look for publish/confirm buttons
  var confirmBtn = btns.find(b => b.innerText.trim().includes('确认') || b.innerText.trim().includes('发布'));
  if (confirmBtn) {
    confirmBtn.click();
    return 'clicked: ' + confirmBtn.innerText.trim();
  }
  // Look in modal/dialog
  var dialogs = document.querySelectorAll('[role="dialog"], .modal, .dialog');
  for (var d = 0; d < dialogs.length; d++) {
    var dBtns = Array.from(dialogs[d].querySelectorAll('button'));
    var cb = dBtns.find(b => b.innerText.trim().includes('确认') || b.innerText.trim().includes('发布'));
    if (cb) { cb.click(); return 'dialog clicked: ' + cb.innerText.trim(); }
  }
  return 'no confirm found, body:' + document.body.innerText.substring(0, 200);
}
"""

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Step 1: Navigate to {URL}")
        page.goto(URL, wait_until="load", timeout=20000)
        page.wait_for_timeout(4000)
        
        print("Step 2: Handle draft dialog")
        try:
            page.get_by_text("放弃", exact=False).click(timeout=2000)
            page.wait_for_timeout(1000)
            print("  Clicked 放弃 on draft dialog")
        except:
            print("  No draft dialog")
        
        print("Step 3: Run JS to fill form and click 下一步")
        result = page.evaluate(SCRIPT)
        print(f"  Result: {result}")
        
        print("Step 4: Wait for navigation")
        page.wait_for_timeout(4000)
        print(f"  URL: {page.url}")
        print(f"  Body: {page.inner_text('body')[:400]}")
        
        print("Step 5: Try to confirm publish")
        page.wait_for_timeout(2000)
        confirm_result = page.evaluate(CONFIRM_SCRIPT)
        print(f"  Confirm result: {confirm_result}")
        
        page.wait_for_timeout(3000)
        print(f"\nFinal URL: {page.url}")
        final_body = page.inner_text("body")[:400]
        print(f"Final body: {final_body}")
        
        if "成功" in final_body or "已发布" in final_body or "发布时间" in final_body:
            print("\n✓ PUBLISH SUCCESS")
        elif "待审核" in final_body or "审核" in final_body:
            print("\n✓ PUBLISH SUCCESS (pending review)")
        elif "下一步" in final_body:
            print("\n! Still on edit page - may need another step")
        else:
            print("\n? Check manually")
        
        browser.close()

if __name__ == "__main__":
    main()