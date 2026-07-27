#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "beautifulsoup4",
#   "bottle",
#   "requests",
#   "simple-websocket-server",
# ]
# ///
"""
Persistent Browser Bridge master.

Keep this process running to avoid the cold-start cost of invoking browser.py
directly for every command. Regular browser.py calls detect the HTTP link on
port+1 and forward commands to this process.
"""

import argparse
import json
import threading

from tmwd_bridge.TMWebDriver import TMWebDriver


def main():
    parser = argparse.ArgumentParser(description="Run a persistent Browser Bridge master")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18765)
    args = parser.parse_args()

    TMWebDriver(host=args.host, port=args.port)
    print(
        json.dumps(
            {
                "status": "success",
                "msg": "browser bridge master started",
                "ws": f"ws://{args.host}:{args.port}",
                "http": f"http://{args.host}:{args.port + 1}/link",
            }
        ),
        flush=True,
    )

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print(json.dumps({"status": "stopped"}), flush=True)


if __name__ == "__main__":
    main()
