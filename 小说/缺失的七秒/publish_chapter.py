#!/usr/bin/env python3
"""
番茄小说发布脚本 - 直接CDP WebSocket版本
直接通过WebSocket连接OpenClaw的Chrome CDP
"""
import json
import time
import re
import os
import sys
import websocket

CDP_URL = "ws://127.0.0.1:18800/devtools/page/3D975DB77AC63B657C2C336F654A8A8B"
WORKDIR = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒"

def send_cmd(ws, method, params=None, id=1):
    msg = {"id": id, "method": method}
    if params:
        msg["params"] = params
    ws.send(json.dumps(msg))
    
def get_response(ws, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            data = ws.recv()
            if isinstance(data, str) and '"id"' in data:
                return json.loads(data)
        except:
            time.sleep(0.1)
    return None

def main():
    if len(sys.argv) < 2:
        print("用法: python3 publish_chapter.py <章节号>")
        sys.exit(1)
    
    chapter_num = sys.argv[1]
    chapter_file = f"{WORKDIR}/第{chapter_num}章.md"
    
    if not os.path.exists(chapter_file):
        print(f"❌ 文件不存在: {chapter_file}")
        sys.exit(1)
    
    print(f"📖 发布第{chapter_num}章...")
    
    with open(chapter_file, encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    raw_title = lines[0].strip()
    subtitle = raw_title.lstrip('#').strip() if raw_title.startswith('#') else raw_title
    m = re.match(r'^第\d+章\s*(.*)', subtitle)
    if m:
        subtitle = m.group(1).strip()
    
    print(f"   章节号: {chapter_num}")
    print(f"   副标题: {subtitle or '(由平台生成)'}")
    print(f"   字数: {len(content)}")
    
    ws = websocket.WebSocket()
    ws.connect(CDP_URL)
    print("   ✓ 已连接到Chrome CDP")
    
    try:
        # 填入章节号
        result = send_cmd(ws, "Runtime.evaluate", {
            "expression": """
            (function() {
                // 找到章节号输入框并填入
                const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
                for (const inp of inputs) {
                    if (inp.offsetWidth > 0 && inp.offsetHeight > 0) {
                        const rect = inp.getBoundingClientRect();
                        if (rect.width > 30 && rect.width < 100 && inp.value.length <= 3) {
                            inp.focus();
                            inp.value = '';
                            for (let c of '%s') inp.value += c;
                            inp.dispatchEvent(new Event('input', {bubbles: true}));
                            inp.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'filled chapter: ' + inp.value;
                        }
                    }
                }
                return 'no input found';
            })();
            """ % chapter_num
        }, 2)
        resp = get_response(ws, timeout=10)
        if resp:
            val = resp.get("result", {}).get("result", {}).get("value", "")
            print(f"   填章节号: {val}")
        
        time.sleep(1)
        
        # 填入标题
        result = send_cmd(ws, "Runtime.evaluate", {
            "expression": """
            (function() {
                const fullTitle = '第%s章 %s';
                const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
                for (const inp of inputs) {
                    if (inp.offsetWidth > 0 && inp.offsetHeight > 0) {
                        const rect = inp.getBoundingClientRect();
                        if (rect.width > 150) {
                            inp.focus();
                            inp.value = '';
                            for (let c of fullTitle) inp.value += c;
                            inp.dispatchEvent(new Event('input', {bubbles: true}));
                            inp.dispatchEvent(new Event('change', {bubbles: true}));
                            return 'filled title: ' + inp.value;
                        }
                    }
                }
                return 'no title input';
            })();
            """ % (chapter_num, subtitle)
        }, 3)
        resp = get_response(ws, timeout=10)
        if resp:
            val = resp.get("result", {}).get("result", {}).get("value", "")
            print(f"   填标题: {val}")
        
        time.sleep(1)
        
        # 粘贴正文内容
        result = send_cmd(ws, "Runtime.evaluate", {
            "expression": """
            (function() {
                const text = `%s`;
                const ta = document.createElement('textarea');
                ta.value = text;
                ta.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                
                // 找到正文区域
                const editables = document.querySelectorAll('[contenteditable="true"], [role="textbox"]');
                for (const el of editables) {
                    if (el.offsetWidth > 0 && el.offsetHeight > 100) {
                        el.focus();
                        document.execCommand('selectAll', false, null);
                        document.execCommand('paste', false, null);
                        return 'pasted to: ' + el.tagName + ' text:' + el.innerText.length + 'chars';
                    }
                }
                
                // 备用：找最大的可编辑元素
                const allEd = document.querySelectorAll('[contenteditable]');
                let best = null;
                for (const el of allEd) {
                    if (!best || (el.offsetHeight > best.offsetHeight)) best = el;
                }
                if (best && best.offsetHeight > 100) {
                    best.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('paste', false, null);
                    return 'pasted to contenteditable, height:' + best.offsetHeight;
                }
                
                return 'content pasted to clipboard, but no editable area found';
            })();
            """ % content.replace('`', '\\`').replace('\\', '\\\\')
        }, 4)
        resp = get_response(ws, timeout=15)
        if resp:
            val = resp.get("result", {}).get("result", {}).get("value", "")
            print(f"   粘贴正文: {val[:80]}...")
        
        time.sleep(2)
        
        # 点击存草稿
        result = send_cmd(ws, "Runtime.evaluate", {
            "expression": """
            (function() {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.includes('存草稿') || btn.textContent.includes('保存')) {
                        btn.click();
                        return 'clicked: ' + btn.textContent.trim();
                    }
                }
                return 'save button not found';
            })();
            """
        }, 5)
        resp = get_response(ws, timeout=10)
        if resp:
            val = resp.get("result", {}).get("result", {}).get("value", "")
            print(f"   存草稿: {val}")
        
        time.sleep(3)
        
        # 点击下一步
        result = send_cmd(ws, "Runtime.evaluate", {
            "expression": """
            (function() {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent.trim() === '下一步') {
                        btn.click();
                        return 'clicked 下一步';
                    }
                }
                return '下一步 button not found';
            })();
            """
        }, 6)
        resp = get_response(ws, timeout=10)
        if resp:
            val = resp.get("result", {}).get("result", {}).get("value", "")
            print(f"   下一步: {val}")
        
        time.sleep(3)
        
        # 检查页面状态
        result = send_cmd(ws, "Runtime.evaluate", {
            "expression": "document.body.innerText.substring(0, 500)"
        }, 7)
        resp = get_response(ws, timeout=10)
        if resp:
            val = resp.get("result", {}).get("result", {}).get("value", "")
            print(f"   页面内容: {val[:200]}...")
        
        print("\n✅ 自动化流程完成，请在浏览器中确认发布状态")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ws.close()

if __name__ == '__main__':
    main()