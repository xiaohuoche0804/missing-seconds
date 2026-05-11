#!/bin/bash
# 番茄小说发布脚本（调试版）
# 用法: ./publish.sh 6

NOVEL_ID="7637711913522056254"
WORKDIR="/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒"
CHAPTER_NUM=$1

if [ -z "$CHAPTER_NUM" ]; then
    echo "用法: $0 <章节号>"
    exit 1
fi

CHAPTER_FILE="$WORKDIR/第${CHAPTER_NUM}章.md"
if [ ! -f "$CHAPTER_FILE" ]; then
    echo "❌ 文件不存在: $CHAPTER_FILE"
    exit 1
fi

echo "📖 发布第${CHAPTER_NUM}章..."

# 复制内容到剪贴板
cat "$CHAPTER_FILE" | pbcopy

# 打开发布页
openclaw browser navigate "https://fanqienovel.com/main/writer/${NOVEL_ID}/publish/?enter_from=newchapter" >/dev/null 2>&1
sleep 2

SNAP=$(openclaw browser snapshot)
echo "$SNAP" | grep -oE 'textbox \[ref=[^]]+\]' | head -3

# 填章节号
FIRST_TEXTBOX=$(echo "$SNAP" | grep -oE 'textbox \[ref=[^]]+\]' | head -1 | sed 's/textbox \[ref=//' | sed 's/\]//')
[ -n "$FIRST_TEXTBOX" ] && openclaw browser type "$FIRST_TEXTBOX" "$CHAPTER_NUM" >/dev/null 2>&1

# 找正文区域 - paragraph标签包含"请输入正文"的ref
BODY_REF=$(echo "$SNAP" | grep -E "paragraph \[ref=[^]]+\]" | while read line; do
  ref=$(echo "$line" | sed -n 's/.*paragraph \[ref=\([^]]*\)\].*/\1/p')
  if [ -n "$ref" ]; then
    echo "$ref"
  fi
done | head -1)

echo "正文ref: $BODY_REF"

if [ -n "$BODY_REF" ]; then
    openclaw browser click "$BODY_REF" >/dev/null 2>&1
    sleep 0.5
    
    # 用AppleScript确保粘贴
    osascript -e 'tell application "System Events" to keystroke "v" using command down'
    sleep 2
fi

# 检查字数
SNAP2=$(openclaw browser snapshot)
WORD_COUNT=$(echo "$SNAP2" | grep -oE '"[0-9]+"' | grep -v "^[0-9]\{4,\}" | tail -1 | tr -d '"')
echo "当前字数: $WORD_COUNT"

# 如果字数不足，提示
if [ "$WORD_COUNT" -lt 1000 ] 2>/dev/null; then
    echo "⚠️ 字数不足1000，实际: $WORD_COUNT"
fi

# 检查风险检测
if echo "$SNAP2" | grep -q "风险检测"; then
    CANCEL_REF=$(echo "$SNAP2" | grep -oE 'button "取消" \[ref=[^]]+\]' | sed 's/.*ref=//' | sed 's/\]//' | head -1)
    [ -n "$CANCEL_REF" ] && openclaw browser click "$CANCEL_REF" >/dev/null 2>&1
fi

# 点下一步
NEXT_REF=$(echo "$SNAP2" | grep -oE 'button "下一步" \[ref=[^]]+\]' | sed 's/.*ref=//' | sed 's/\]//' | head -1)
[ -n "$NEXT_REF" ] && openclaw browser click "$NEXT_REF" >/dev/null 2>&1

# 等待发布设置
for i in {1..5}; do
    sleep 1
    SNAP3=$(openclaw browser snapshot)
    if echo "$SNAP3" | grep -q "发布设置"; then
        CONFIRM_REF=$(echo "$SNAP3" | grep -oE 'button "确认发布" \[ref=[^]]+\]' | sed 's/.*ref=//' | sed 's/\]//' | head -1)
        [ -n "$CONFIRM_REF" ] && openclaw browser click "$CONFIRM_REF" >/dev/null 2>&1
        sleep 3
        break
    fi
done

SNAP4=$(openclaw browser snapshot)
if echo "$SNAP4" | grep -q "已发布"; then
    echo "✅ 第${CHAPTER_NUM}章发布成功!"
else
    echo "⚠️ 发布完成，请检查页面状态"
fi