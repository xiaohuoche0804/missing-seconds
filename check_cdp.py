#!/usr/bin/env python3
"""Use CDP to connect to real Chrome and publish chapter 10"""

import json
import subprocess
import time

CHAPTER_ID = "7638477068807701054"
WRITER_ID = "7637711913522056254"
URL = f"https://fanqienovel.com/main/writer/{WRITER_ID}/publish/{CHAPTER_ID}?enter_from=modifychapter"

def cdp_cmd(sock, cmd):
    result = subprocess.run(["curl", "-s", "--unix-socket", sock, "-X", "POST", 
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps(cmd),
                            "http://localhost/json/" + cmd["method"] if "method" in cmd else f"http://localhost/json/{cmd[0]}"],
                           capture_output=True, text=True)
    return result.stdout

def find_chrome_sock():
    import glob
    socks = glob.glob("/tmp/.X*-unix/presentation/sock")
    return socks[0] if socks else None

def main():
    # Find Chrome CDP socket
    import glob
    import os
    
    # Common Chrome socket locations
    candidates = [
        "/tmp/.org.chromium.Chromium*/Socket",
        "/tmp/.chrome-user-data/sock",
        os.path.expanduser("~/Library/Application Support/Google/Chrome/Socket"),
    ]
    
    # Find via lsof
    result = subprocess.run(["lsof", "-c", "Chromium", "-t"], capture_output=True, text=True)
    if result.stdout.strip():
        print(f"Chrome processes: {result.stdout.strip()}")
    
    # Try Chrome DevTools port
    result = subprocess.run(["curl", "-s", "http://localhost:9222/json"], capture_output=True, text=True)
    if result.stdout and "Chromium" in result.stdout:
        print(f"Chrome DevTools available at localhost:9222")
        print(f"Result: {result.stdout[:500]}")
    else:
        print(f"Chrome DevTools not at 9222: {result.stderr or 'empty'}")
    
    print("\nManual check needed: Chrome browser has the logged-in session.")
    print(f"Need to navigate to: {URL}")
    print("And click 下一步 → confirm")

if __name__ == "__main__":
    main()