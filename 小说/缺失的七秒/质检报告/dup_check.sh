#!/bin/bash
cd "/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒"

echo "=== 跨章内容重复检测（过滤对话短句，行级相似度）==="
echo ""

# Common dialogue tags to ignore (short patterns)
IGNORE='^[[:space:]]*(他|她|宋鹤年|方桐|林晚|陈劲松|龙哥|老马|陆远征|钱多多|周文博|孟宪民|苏敏|王建国|老郑|方旭|阿辉)(停顿了一下|没说话|看着他|看着她|沉默了|叹了口气|笑了一下|点了点头|摇了摇头|没有回答|没有回头|转过来|转回去|站起来|坐下来|走出去|走进来|关上门|打开门|挂了电话|接了电话|放下杯子|端起杯子)[[:space:]]*$'

prev=""
for f in $(ls 第*.md | sort -V); do
  if [ -n "$prev" ]; then
    # Extract lines with content (>20 chars, not dialogue tags), unique per file
    f1_lines=$(grep -v '^\s*$' "$prev" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
      | awk 'length>20' | grep -vE "$IGNORE" | sort -u | wc -l | tr -d ' ')
    f2_lines=$(grep -v '^\s*$' "$f" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
      | awk 'length>20' | grep -vE "$IGNORE" | sort -u | wc -l | tr -d ' ')
    
    common=$(comm -12 \
      <(grep -v '^\s*$' "$prev" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | awk 'length>20' | grep -vE "$IGNORE" | sort -u) \
      <(grep -v '^\s*$' "$f" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | awk 'length>20' | grep -vE "$IGNORE" | sort -u) \
      2>/dev/null | wc -l | tr -d ' ')
    
    min_lines=$f1_lines
    [ "$f2_lines" -lt "$min_lines" ] 2>/dev/null && min_lines=$f2_lines
    
    if [ "$min_lines" -gt 0 ] 2>/dev/null && [ "$common" -gt 0 ] 2>/dev/null; then
      pct=$(( common * 100 / min_lines ))
      if [ "$pct" -gt 25 ]; then
        # Show actual shared lines
        shared=$(comm -12 \
          <(grep -v '^\s*$' "$prev" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | awk 'length>20' | grep -vE "$IGNORE" | sort -u) \
          <(grep -v '^\s*$' "$f" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | awk 'length>20' | grep -vE "$IGNORE" | sort -u) \
          2>/dev/null | head -3 | tr '\n' ' | ')
        echo "⚠️  $prev ↔ $f: ${pct}% 重叠 ($common/$min_lines): $shared"
      fi
    fi
  fi
  prev="$f"
done

echo ""
echo "=== 单章内实质性重复检测 ==="
echo ""

for f in $(ls 第*.md | sort -V); do
  # Content-bearing lines (>25 chars), not dialogue tags, that repeat
  dups=$(grep -v '^\s*$' "$f" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
    | awk 'length>25' | grep -vE "$IGNORE" \
    | sort | uniq -d | wc -l | tr -d ' ')
  if [ "$dups" -gt 1 ]; then
    echo "⚠️  $f: $dups 行实质性重复"
    grep -v '^\s*$' "$f" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
      | awk 'length>25' | grep -vE "$IGNORE" \
      | sort | uniq -d | while read line; do
        echo "   → $line"
      done
  fi
done

echo ""
echo "=== 全章md5完整性检查 ==="
md5 -q 第*.md | sort | uniq -d | while read h; do
  echo "❌ MD5重复: $h"
  grep -l "$(echo $h)" 第*.md
done
echo "---done---"
