from __future__ import annotations

import argparse
import os

import httpx

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=["rag_slow", "tool_fail", "cost_spike"])
    parser.add_argument("--disable", action="store_true")
    args = parser.parse_args()

    path = f"/incidents/{args.scenario}/disable" if args.disable else f"/incidents/{args.scenario}/enable"
    r = httpx.post(f"{BASE_URL}{path}", timeout=10.0)
    print(r.status_code, r.json())


if __name__ == "__main__":
    main()
