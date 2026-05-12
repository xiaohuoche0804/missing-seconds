#!/bin/bash

# Get snapshot and immediately fill - all in one shot
(openclaw browser --json snapshot | python3 -c "
import sys, json
data = json.load(sys.stdin)
refs = data.get('refs', {})
# Find textboxes
chapter_ref = None
title_ref = None
for ref, info in refs.items():
    if info.get('role') == 'textbox':
        name = info.get('name', '')
        if name == '?':
            chapter_ref = ref
        elif '标题' in name:
            title_ref = ref

print(f'CHAPTER_REF={chapter_ref}')
print(f'TITLE_REF={title_ref}')
" > /tmp/refs.txt) 2>&1

source /tmp/refs.txt
echo "Chapter ref: $CHAPTER_REF, Title ref: $TITLE_REF"

if [ -n "$CHAPTER_REF" ] && [ -n "$TITLE_REF" ]; then
    openclaw browser fill --fields "[{\"ref\":\"$CHAPTER_REF\",\"value\":\"11\"},{\"ref\":\"$TITLE_REF\",\"value\":\"第11章 电话\"}]" 2>&1
fi