#!/usr/bin/env python3
"""Publish Chapter 17 using playwright HTTP CDP"""
import asyncio
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Connect via HTTP CDP (works!)
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        
        # Get existing pages
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        pages = ctx.pages
        print(f"Pages: {len(pages)}")
        
        # Find or create publish page
        pub_page = None
        for pg in pages:
            url = pg.url
            if 'publish' in url and 'fanqienovel' in url and 'chapter' not in url:
                pub_page = pg
                print("Found existing publish page:", pg.url[:80])
                break
        
        if not pub_page:
            print("Creating new page")
            pub_page = await ctx.new_page()
        
        # Navigate to fresh publish
        await pub_page.goto('https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter')
        await pub_page.wait_for_load_state('domcontentloaded', timeout=10000)
        await asyncio.sleep(8)
        
        print("URL:", pub_page.url[:100])
        
        # Find chapter number input
        inputs = await pub_page.query_selector_all('input')
        print(f"Inputs: {len(inputs)}")
        
        # Fill chapter number (first short input)
        for inp in inputs:
            val = await inp.input_value()
            ph = await inp.get_attribute('placeholder') or ''
            if not ph and len(val) <= 3 and not val:
                await inp.fill('17')
                print("Filled chapter:", '17')
                break
        
        await asyncio.sleep(0.5)
        
        # Fill title
        all_inputs = await pub_page.query_selector_all('input')
        for inp in all_inputs:
            ph = await inp.get_attribute('placeholder') or ''
            if '标题' in ph:
                await inp.fill('第17章 困局')
                print("Filled title")
                break
        
        await asyncio.sleep(0.5)
        
        # Find content editable area
        content_el = pub_page.locator('[contenteditable="true"]').first
        if await content_el.count() > 0:
            await content_el.click()
            await asyncio.sleep(0.5)
            print("Content area clicked")
            
            # Read chapter file
            with open('第17章.md', 'r') as f:
                content = f.read()
            content = re.sub(r'^---\n[\s\S]*?\n---\n', '', content)
            print("Content length:", len(content))
            
            # Select all and replace
            await content_el.select_text()
            await asyncio.sleep(0.3)
            
            # Type content using keyboard - use keyboard.updater_content for faster typing
            # Actually let's try fill via evaluate
            escaped = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
            html_parts = []
            for para in content.split('\n\n'):
                if para.strip():
                    html_parts.append('<p>' + para.strip().replace('\n', '<br>') + '</p>')
            html = ''.join(html_parts)
            js_escaped = html.replace('\\', '\\\\').replace('"', '\\"')
            
            result = await pub_page.evaluate(f"""
                (function() {{
                    var el = document.querySelector('[contenteditable="true"]');
                    el.focus();
                    el.innerHTML = "{js_escaped}";
                    el.dispatchEvent(new Event('input', {{bubbles: true}}));
                    return el.innerText.length;
                }})()
            """)
            print("Content injected, chars:", result)
            
            await asyncio.sleep(2)
        
        # Click save draft
        btns = await pub_page.query_selector_all('button')
        for btn in btns:
            txt = await btn.text_content()
            if txt and '存草稿' in txt:
                await btn.click()
                print("Clicked 存草稿")
                break
        
        await asyncio.sleep(3)
        
        # Check word count display
        try:
            text = await pub_page.inner_text('body')
            # Look for number pattern near 正文字数
            import re
            match = re.search(r'正文字数[^\d]*(\d+)', text)
            if match:
                print("Word count:", match.group(1))
        except:
            pass
        
        # Click 下一步
        btns2 = await pub_page.query_selector_all('button')
        for btn in btns2:
            txt = await btn.text_content()
            if txt and txt.strip() == '下一步':
                await btn.click()
                print("Clicked 下一步")
                break
        
        await asyncio.sleep(3)
        print("Final URL:", pub_page.url[:100])
        
        await browser.close()
        print("DONE")

asyncio.run(main())