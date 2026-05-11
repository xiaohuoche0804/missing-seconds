#!/usr/bin/env python3
"""
番茄小说发布脚本 - CDP WebSocket版本
直接通过WebSocket连接OpenClaw的Chrome CDP
"""
import json
import time
import re
import os
import subprocess
import websocket

CDP_URL = "ws://127.0.0.1:18800/devtools/page/403E4EA89687FD9D61DDBF557C62B7E6"
WORKDIR = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒"

def send_cmd(ws, method, params=None, id=1):
    msg = {"id": id, "method": method}
    if params:
        msg["params"] = params
    ws.send(json.dumps(msg))
    
def get_response(ws, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        data = ws.recv()
        if isinstance(data, str) and '"id"' in data:
            return json.loads(data)
    return None

def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 publish_cdp.py <章节号>")
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
    if not subtitle or len(subtitle) < 2:
        subtitle = ""
    
    print(f"   章节号: {chapter_num}")
    print(f"   副标题: {subtitle or '(由平台生成)'}")
    print(f"   字数: {len(content)}")
    
    ws = websocket.WebSocket()
    ws.connect(CDP_URL)
    print("   ✓ 已连接到Chrome CDP")
    
    try:
        # 执行JavaScript来填入内容
        # 先导航到发布页面
        send_cmd(ws, "Page.navigate", {"url": "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"})
        time.sleep(4)
        
        # 获取DOM snapshot
        send_cmd(ws, "DOM.getDocument", {}, 1)
        resp = get_response(ws)
        
        # 使用Runtime.evaluate来操作页面
        # 在正文区域粘贴内容
        paste_js = f'''
(function() {{
    // 复制内容到剪贴板
    const text = `{content.replace('`', '\\`')}`;
    
    // 创建临时textarea来复制
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    
    // 找到可编辑元素并粘贴
    const editable = document.querySelector('[contenteditable="true"]');
    if (editable) {{
        editable.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('paste', false, null);
        return 'pasted to editable';
    }}
    
    // 尝试找到第一个input
    const inputs = document.querySelectorAll('input');
    for (const inp of inputs) {{
        if (inp.offsetWidth > 0 && inp.offsetHeight > 0) {{
            inp.focus();
            return 'found inputs';
        }}
    }}
    return 'no editable found';
}})();
'''
        
        send_cmd(ws, "Runtime.evaluate", {"expression": paste_js, "returnByValue": True}, 2)
        resp = get_response(ws, timeout=10)
        if resp:
            result = resp.get("result", {}).get("result", {})
            print(f"   粘贴结果: {result.get('value', 'unknown')}")
        
        # 等待页面稳定
        time.sleep(2)
        
        # 获取页面内容确认状态
        send_cmd(ws, "Runtime.evaluate", {"expression": "document.body.innerText.substring(0, 500)", "returnByValue": True}, 3)
        resp = get_response(ws, timeout=10)
        if resp:
            text = resp.get("result", {}).get("result", {}).get("value", "")
            print(f"   页面文本: {text[:200]}...")
        
        print("\n⚠️ CDP直接控制需要更复杂的实现，请检查浏览器窗口是否已打开发布页面")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        ws.close()

if __name__ == '__main__':
    main()