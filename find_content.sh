#!/bin/bash

# Get fresh snapshot
snapshot=$(openclaw browser --json snapshot)
echo "$snapshot" | python3 -c "
import sys, json
data = json.load(sys.stdin)
refs = data.get('refs', {})
print('URL:', data.get('url'))
# Find all elements that might be content area
for ref, info in refs.items():
    name = info.get('name', '')
    role = info.get('role', '')
    if role in ['textbox', 'input'] or '正文' in name or '内容' in name or 'editor' in name.lower():
        print(f'{ref}: {role} - {name}')
"