#!/bin/bash

# Get fresh snapshot
snapshot=$(openclaw browser --json snapshot)
echo "$snapshot" | python3 -c "
import sys, json
data = json.load(sys.stdin)
refs = data.get('refs', {})
print('URL:', data.get('url'))
# Find all textboxes
for ref, info in refs.items():
    if info.get('role') == 'textbox':
        print(f'{ref}: {info.get(\"name\", \"chapter number\")} value={info.get(\"value\", \"\")}')
" > /tmp/textboxes.txt

cat /tmp/textboxes.txt