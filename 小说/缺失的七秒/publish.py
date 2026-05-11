#!/usr/bin/env python3
"""
番茄小说发布脚本 - 优化版 v4
关键修复：标题字段留空，让平台自动生成"第X章 副标题"格式
"""
import subprocess
import time
import re
import os

NOVEL_ID = "7637711913522056254"
WORKDIR = "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒"

def run(cmd, wait=0.5):
    subprocess.run(cmd, shell=True)
    if wait:
        time.sleep(wait)

def snap():
    out = subprocess.run('openclaw browser snapshot', shell=True, capture_output=True, text=True)
    return out.stdout

def click(ref, wait=0.5):
    subprocess.run(f'openclaw browser click {ref}', shell=True)
    time.sleep(wait)

def type_text(ref, text):
    subprocess.run(f'openclaw browser click {ref}', shell=True)
    time.sleep(0.3)
    subprocess.run(f'openclaw browser type {ref} "{text}"', shell=True)
    time.sleep(0.3)

def press(key):
    subprocess.run(f'openclaw browser press "{key}"', shell=True)
    time.sleep(0.3)

def extract_ref(text, pattern):
    m = re.search(pattern, text)
    return m.group(1) if m else None

def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 publish.py <章节号>")
        print("  例: python3 publish.py 7")
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
    
    # 解析标题：提取副标题（章节号由平台自动生成）
    lines = content.split('\n')
    raw_title = lines[0].strip()
    subtitle = raw_title.lstrip('#').strip() if raw_title.startswith('#') else raw_title
    
    # 如果标题包含"第X章"，去掉它，只保留副标题
    m = re.match(r'^第\d+章\s*(.*)', subtitle)
    if m:
        subtitle = m.group(1).strip()
    
    # 如果副标题为空或太短，使用默认
    if not subtitle or len(subtitle) < 2:
        subtitle = ""
    
    print(f"   章节号: {chapter_num}")
    print(f"   副标题: {subtitle or '(由平台生成)'}")
    print(f"   字数: {len(content)}")
    
    # 打开发布页
    print("   打开发布页...")
    run('openclaw browser navigate "https://fanqienovel.com/main/writer/7637711913522056254/publish/?enter_from=newchapter"', 2)
    
    snap_out = snap()
    
    # 1. 填章节号
    ref = extract_ref(snap_out, r'textbox \[ref=(\w+)\]')
    if ref:
        click(ref)
        press("Meta+a")
        type_text(ref, chapter_num)
        print("   ✓ 章节号已填")
    
    # 2. 【关键修复】标题字段留空，让平台自动生成
    # 不再填副标题到标题字段，避免"第7章 第7章 副标题"问题
    print("   ✓ 标题字段留空（由平台自动生成）")
    
    # 3. 点击正文区域并粘贴
    m = re.search(r'paragraph \[ref=(\w+)\]:\s*[^"]*请输入正文', snap_out, re.DOTALL)
    if not m:
        m = re.search(r'paragraph \[ref=(\w+)\]:', snap_out)
    
    if m:
        body_ref = m.group(1)
        click(body_ref, 0.5)
        
        # 复制内容到剪贴板
        subprocess.run(f'cat "{chapter_file}" | pbcopy', shell=True)
        time.sleep(0.3)
        press("Meta+v")
        time.sleep(2)
        
        snap2 = snap()
        counts = [int(x) for x in re.findall(r'"(\d+)"', snap2)]
        valid_counts = [c for c in counts if 500 < c < 50000]
        if valid_counts:
            print(f"   ✓ 字数显示: {max(valid_counts)}")
    
    # 4. 处理风险检测弹窗
    snap2 = snap()
    if "风险检测" in snap2:
        ref = extract_ref(snap2, r'button "取消" \[ref=(\w+)\]')
        if ref:
            click(ref)
            print("   ✓ 关闭风险检测")
    
    # 5. 点下一步
    ref = extract_ref(snap(), r'button "下一步" \[ref=(\w+)\]')
    if ref:
        click(ref, 1)
        print("   ✓ 点击下一步")
    
    # 6. 处理错别字提示 或 发布设置
    for i in range(15):
        time.sleep(1)
        snap3 = snap()
        
        if "错别字" in snap3 and "确定提交" in snap3:
            ref = extract_ref(snap3, r'button "提交" \[ref=(\w+)\]')
            if ref:
                click(ref, 0.5)
                print("   ✓ 确认提交")
            break
        
        if "发布设置" in snap3:
            ref = extract_ref(snap3, r'button "确认发布" \[ref=(\w+)\]')
            if ref:
                click(ref, 0.5)
                print("   ✓ 确认发布")
            time.sleep(3)
            break
    
    # 7. 验证结果
    time.sleep(3)
    result = snap()
    if "已发布" in result or "发布成功" in result:
        print(f"\n✅ 第{chapter_num}章发布成功!")
    else:
        print("\n⚠️ 发布完成，请手动检查页面")

if __name__ == '__main__':
    main()