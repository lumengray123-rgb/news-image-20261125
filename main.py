#!/usr/bin/env python3
"""Entry point for the news-image-20261125 bounty.

Copies the pre-rendered front page (entry.png, in this repository's
root) to /output/entry.png. The image sums up Wednesday 25 November
2026's world news as "THE WORLD TODAY" newspaper front page.
Standard library only; no network access."""

import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    with open(src, "rb") as f:
        data = f.read()
    if data[:8] != PNG_MAGIC:
        print("error: entry.png is not a PNG file", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print(f"error: entry.png is {len(data)} bytes, over the 1 MiB limit",
              file=sys.stderr)
        return 1
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as f:
        f.write(data)
    print(f"wrote {dst} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
