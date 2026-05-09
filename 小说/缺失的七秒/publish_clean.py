#!/usr/bin/env python3
"""
清理小说章节文件，移除发布用元数据
只保留正文内容
"""
import re
import os
import sys

CHAPTER_DIR = os.path.dirname(os.path.abspath(__file__))

# 需要移除的内容模式（从后往前匹配）
REMOVE_PATTERNS = [
    r'\n---\s*\n章节标签：.+',
    r'\n【本章完】\s*',
    r'\n\*\*本章摘要\*\*：?\s*\n[\s\S]+',
    r'\n\*\*本章字数\*\*：.+',
]

def clean_chapter(filepath):
    """清理单个章节文件的元数据"""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 移除标题行的 # 号（publisher会自己生成标题）
    content = re.sub(r'^# ', '', content, count=1)
    
    for pattern in REMOVE_PATTERNS:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # 清理多余空行（末尾超过2个换行缩为1个）
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    if len(sys.argv) < 2:
        print("用法: python3 publish_clean.py 第X章.md")
        print("  或: python3 publish_clean.py all（清理所有章节）")
        return
    
    if sys.argv[1] == 'all':
        files = sorted([f for f in os.listdir(CHAPTER_DIR) 
                       if re.match(r'第\d+章\.md', f)])
    else:
        files = [sys.argv[1]]
    
    for f in files:
        filepath = os.path.join(CHAPTER_DIR, f)
        if os.path.isfile(filepath):
            changed = clean_chapter(filepath)
            status = "已清理" if changed else "无需清理"
            print(f"{f}: {status}")

if __name__ == '__main__':
    main()
