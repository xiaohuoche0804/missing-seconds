#!/usr/bin/env python3
"""
番茄小说发布脚本 - Selenium版本（无头模式）
使用已运行的Chrome浏览器（通过debugger端口）
"""
import subprocess
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NOVEL_ID = "7637711913522056254"
WORKDIR = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒"

def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 publish_selenium.py <章节号>")
        print("  例: python3 publish_selenium.py 12")
        sys.exit(1)
    
    chapter_num = sys.argv[1]
    chapter_file = f"{WORKDIR}/第{chapter_num}章.md"
    
    if not os.path.exists(chapter_file):
        print(f"❌ 文件不存在: {chapter_file}")
        sys.exit(1)
    
    print(f"📖 发布第{chapter_num}章...")
    
    # 读取内容
    with open(chapter_file, encoding='utf-8') as f:
        content = f.read()
    
    # 解析标题
    lines = content.split('\n')
    raw_title = lines[0].strip()
    subtitle = raw_title.lstrip('#').strip() if raw_title.startswith('#') else raw_title
    m = re.match(r'^第\d+章\s*(.*)', subtitle)
    if m:
        subtitle = m.group(1).strip()
    if not subtitle or len(subtitle) < 2:
        subtitle = ""
    
    print(f"   章节号: {chapter_num}")
    print(f"   副标题: {subtitle or '(由平台生成)'}")
    print(f"   字数: {len(content)}")
    
    # 配置Chrome连接到已运行的浏览器
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    
    try:
        # 打开发布页面
        print("   打开发布页...")
        driver.get("https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter")
        time.sleep(3)
        
        # 填章节号 - 找到第一个输入框
        try:
            inputs = driver.find_elements(By.CSS_SELECTOR, "input")
            for inp in inputs:
                try:
                    if inp.is_displayed() and inp.is_enabled():
                        inp.clear()
                        inp.send_keys(chapter_num)
                        print("   ✓ 章节号已填")
                        break
                except:
                    continue
        except Exception as e:
            print(f"   ⚠️ 章节号填入失败: {e}")
        
        time.sleep(1)
        
        # 找正文输入区域并粘贴内容
        print("   粘贴正文...")
        
        # 方法1：尝试查找段落元素
        try:
            # 找contenteditable元素或文本区域
            paragraphs = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
            if paragraphs:
                for p in paragraphs:
                    if p.is_displayed():
                        p.click()
                        time.sleep(0.3)
                        p.send_keys(Keys.COMMAND + "a")
                        time.sleep(0.2)
                        subprocess.run(f'cat "{chapter_file}" | pbcopy', shell=True)
                        time.sleep(0.3)
                        p.send_keys(Keys.COMMAND + "v")
                        print("   ✓ 正文已粘贴 (contenteditable)")
                        break
        except Exception as e:
            print(f"   ⚠️ contenteditable方式失败: {e}")
        
        time.sleep(2)
        
        # 关闭风险检测弹窗
        try:
            time.sleep(1)
            # 查找包含"取消"文字的按钮
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if btn.is_displayed() and "取消" in btn.text:
                    btn.click()
                    print("   ✓ 关闭风险检测")
                    time.sleep(1)
                    break
        except:
            pass
        
        # 点下一步
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if btn.is_displayed() and btn.text.strip() == "下一步":
                    btn.click()
                    print("   ✓ 点击下一步")
                    time.sleep(3)
                    break
        except Exception as e:
            print(f"   ⚠️ 下一步按钮: {e}")
        
        # 等待并处理后续弹窗（错别字检测或发布设置）
        for i in range(20):
            time.sleep(1)
            page_text = driver.page_source
            
            if "错别字" in page_text and "提交" in page_text:
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if btn.is_displayed() and btn.text.strip() == "提交":
                            btn.click()
                            print("   ✓ 确认提交")
                            time.sleep(2)
                            break
                except:
                    pass
            
            if ("发布设置" in page_text or "确认发布" in page_text):
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if btn.is_displayed() and "确认发布" in btn.text:
                            btn.click()
                            print("   ✓ 确认发布")
                            time.sleep(3)
                            break
                except:
                    pass
        
        # 检查结果
        time.sleep(3)
        final_text = driver.page_source
        if "已发布" in final_text or "发布成功" in final_text:
            print(f"\n✅ 第{chapter_num}章发布成功!")
        else:
            print("\n⚠️ 发布流程完成，请手动检查页面状态")
            driver.save_screenshot(f"/tmp/publish_chapter_{chapter_num}.png")
            print(f"   已保存截图: /tmp/publish_chapter_{chapter_num}.png")
    
    except Exception as e:
        print(f"\n❌ 发布失败: {e}")
        try:
            driver.save_screenshot(f"/tmp/publish_error_{chapter_num}.png")
            print(f"   错误截图: /tmp/publish_error_{chapter_num}.png")
        except:
            pass
    
    finally:
        driver.quit()
        print("   浏览器已关闭")

if __name__ == '__main__':
    main()