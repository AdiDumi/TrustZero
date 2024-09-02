#!/usr/bin/env python3
import sys
import json


def main():
    if len(sys.argv) < 2:
        sys.stdout.write("error")  # if there is no ip
    else:
        try:
            with open("/app/ip_blocked.txt", 'r') as f:
                ips = json.load(f)
                if sys.argv[1] not in ips:
                    ips.append(sys.argv[1])
        except json.JSONDecodeError:
            ips = [sys.argv[1]]
        with open("/app/ip_blocked.txt", 'w') as f:
            json.dump(ips, f, indent=4)
        sys.stdout.write("ip logged")


if __name__ == "__main__":
    main()
