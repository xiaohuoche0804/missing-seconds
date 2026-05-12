#!/bin/bash

# Get fresh snapshot and immediately use the title ref
snapshot=$(openclaw browser --json snapshot)
echo "$snapshot" | python3 -c "
import sys, json
data = json.load(sys.stdin)
refs = data.get('refs', {})
# Find title textbox
for ref, info in refs.items():
    if info.get('role') == 'textbox' and info.get('name') and '标题' in info.get('name'):
        print(ref)
        break
" > /tmp/title_ref.txt

title_ref=$(cat /tmp/title_ref.txt)
echo "Title ref: $title_ref"

if [ -n "$title_ref" ]; then
    echo "Filling title..."
    openclaw browser fill --fields "[{\"ref\":\"$title_ref\",\"value\":\"第11章 电话\"}]" 2>&1
else
    echo "Could not find title ref"
fi