#!/bin/bash
# Try using Python to control the browser via CDP
python3 << 'PYEOF'
import subprocess
import json

# Use openclaw browser evaluate to execute JavaScript
result = subprocess.run([
    'openclaw', 'browser', 'evaluate'
], input=json.dumps({"expression": "document.querySelector('input[placeholder*=\"输入标题\"]').value = 'test'"}),
   capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
PYEOF