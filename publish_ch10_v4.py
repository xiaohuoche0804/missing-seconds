#!/usr/bin/env python3
"""Use real Chrome with existing session to publish chapter 10"""

from playwright.sync_api import sync_playwright
import os

CHAPTER_ID = "7638477068807701054"
WRITER_ID = "7637711913522056254"
URL = f"https://fanqienovel.com/main/writer/{WRITER_ID}/publish/{CHAPTER_ID}?enter_from=modifychapter"

def main():
    # Find Chrome user data dir
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default")
    
    if not os.path.exists(user_data_dir):
        user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    
    print(f"Using Chrome at: {chrome_path}")
    print(f"User data: {user_data_dir}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome_path,
            headless=True,
            user_data_dir=user_data_dir
        )
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        print(f"\nStep 1: Navigate to {URL}")
        page.goto(URL, wait_until="load", timeout=20000)
        page.wait_for_timeout(4000)
        
        print(f"  URL: {page.url}")
        body = page.inner_text("body")
        print(f"  Body preview: {body[:300]}")
        
        if "登录" in body and "验证码" in body:
            print("\n! NOT LOGGED IN - need to login manually")
            page.screenshot(path="need_login.png")
            print("  Screenshot saved to need_login.png")
        else:
            print("\n  Logged in - proceeding...")
            
            print("\nStep 2: Handle draft dialog if present")
            try:
                page.get_by_text("放弃", exact=False).click(timeout=2000)
                page.wait_for_timeout(1000)
                print("  Clicked 放弃")
            except:
                print("  No draft dialog")
            
            print("\nStep 3: Fill form and click 下一步")
            script_result = page.evaluate("""
            () => {
              var numInput = document.querySelector('.serial-input.byte-input');
              if (numInput) { numInput.value = '10'; numInput.dispatchEvent(new Event('input', {bubbles:true})); }
              var titleInput = document.querySelector('input[placeholder="请输入标题"]');
              if (titleInput) { titleInput.value = '照片'; titleInput.dispatchEvent(new Event('input', {bubbles:true})); }
              var btns = Array.from(document.querySelectorAll('button'));
              var nextBtn = btns.find(b => b.innerText.trim() === '下一步');
              if (nextBtn) { nextBtn.click(); return 'clicked next, disabled=' + nextBtn.disabled; }
              return 'next btn not found';
            }
            """)
            print(f"  Result: {script_result}")
            
            page.wait_for_timeout(4000)
            print(f"  URL after next: {page.url}")
            body2 = page.inner_text("body")
            print(f"  Body: {body2[:400]}")
            
            print("\nStep 4: Confirm publish if dialog appeared")
            page.wait_for_timeout(2000)
            confirm_result = page.evaluate("""
            () => {
              var btns = Array.from(document.querySelectorAll('button'));
              var confirmBtn = btns.find(b => b.innerText.trim().includes('确认') || b.innerText.trim().includes('发布'));
              if (confirmBtn) { confirmBtn.click(); return 'clicked: ' + confirmBtn.innerText.trim(); }
              return 'no confirm found, body:' + document.body.innerText.substring(0, 300);
            }
            """)
            print(f"  Result: {confirm_result}")
            
            page.wait_for_timeout(3000)
            print(f"\nFinal URL: {page.url}")
            final = page.inner_text("body")[:400]
            print(f"Final body: {final}")
            
            if "成功" in final or "已发布" in final or "发布时间" in final:
                print("\n✓ PUBLISH SUCCESS")
            elif "待审核" in final or "审核" in final:
                print("\n✓ PUBLISH SUCCESS (pending review)")
            elif "下一步" in final:
                print("\n! Still on edit page")
            else:
                print("\n? Check manually")
        
        browser.close()

if __name__ == "__main__":
    main()