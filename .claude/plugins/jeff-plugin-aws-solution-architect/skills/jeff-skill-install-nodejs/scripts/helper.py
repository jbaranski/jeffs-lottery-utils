#!/usr/bin/env python3
import json

def main() -> int:
    b = False
    if b:
        print(json.dumps({"error": "This is an error scenario"}))
        return 1
    print(json.dumps({"hello": "world"}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
