#!/bin/bash

# Get the chapter content
CHAPTER_FILE="/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第11章.md"
CONTENT=$(python3 << 'PYEOF'
import sys
with open("/Users/ganghonghai/Documents/openclaw-novel-workspace/小说/缺失的七秒/第11章.md", "r") as f:
    content = f.read()
    # Remove front matter
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end+3:].strip()
    print(content[:500])
PYEOF
)

echo "Content preview: $CONTENT"

# Create a JSON with the content
# The content input might be a paragraph with placeholder "请输入正文"
openclaw browser --json snapshot 2>&1 | python3 -c "
import sys, json
data = json.load(sys.stdin)
refs = data.get('refs', {})
for ref, info in refs.items():
    role = info.get('role', '')
    name = info.get('name', '')
    print(f'{ref}: {role} - {name}')
" | head -40