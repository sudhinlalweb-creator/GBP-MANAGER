#!/usr/bin/env python3
"""Fail CI if any source file exceeds MAX_LINES lines.

Usage:
    python scripts/check_file_length.py [path ...]

Defaults to scanning backend/app and frontend/app,components,contexts,lib,hooks.
"""
import sys
from pathlib import Path

MAX_LINES = 300
EXTENSIONS = {".py", ".ts", ".tsx"}

SCAN_ROOTS = [
    "backend/app",
    "frontend/app",
    "frontend/components",
    "frontend/contexts",
    "frontend/lib",
    "frontend/hooks",
    "frontend/features",
    "frontend/providers",
]

repo_root = Path(__file__).parent.parent
paths = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else [repo_root / r for r in SCAN_ROOTS]

violations: list[tuple[Path, int]] = []
for root in paths:
    for f in root.rglob("*"):
        if f.suffix in EXTENSIONS and f.is_file():
            lines = len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
            if lines > MAX_LINES:
                violations.append((f.relative_to(repo_root), lines))

if violations:
    print(f"\n❌  Files exceeding {MAX_LINES}-line limit:\n")
    for path, count in sorted(violations, key=lambda x: -x[1]):
        print(f"  {count:>5}  {path}")
    print(f"\nSplit each file so no module exceeds {MAX_LINES} lines.\n")
    sys.exit(1)

print(f"✅  All files are within the {MAX_LINES}-line limit.")
