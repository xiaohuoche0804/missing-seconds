#!/usr/bin/env python3
"""Use CDP via websocket to fill content"""
import json
import websocket
import sys

def send_cdp(ws, method, params=None):
    msg = {'id': 1, 'method': method}
    if params:
        msg['params'] = params
    ws.send(json.dumps(msg))
    result = ws.recv()
    return json.loads(result)

# Connect to the current active page
ws_url = "ws://127.0.0.1:18800/devtools/page/E313F4F95C271546CCD7EBAF94666BC0"
ws = websocket.create_connection(ws_url, timeout=30)

# Get page info
result = send_cdp(ws, "Page.getFrameTree")
print("Frame tree:", json.dumps(result, indent=2)[:500])

ws.close()