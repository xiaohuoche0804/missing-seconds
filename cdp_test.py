#!/usr/bin/env python3
"""Use CDP directly to interact with the browser"""
import json
import websocket

def send_cdp(ws, method, params=None):
    msg = {'id': 1, 'method': method}
    if params:
        msg['params'] = params
    ws.send(json.dumps(msg))
    result = ws.recv()
    return json.loads(result)

# Connect to the CDP endpoint
ws_url = "ws://127.0.0.1:18800/devtools/page/32B1A7F69009D3982F30BF71A06AE296"
ws = websocket.create_connection(ws_url, timeout=10)

# Get document
result = send_cdp(ws, "DOM.getDocument")
print("Got document:", result.get('root', {}).get('nodeId'))

# Query selector for title input
result = send_cdp(ws, "DOM.querySelector", {
    'nodeId': result['root']['nodeId'],
    'selector': 'input[placeholder*="标题"]'
})
print("Title input node:", result)

ws.close()