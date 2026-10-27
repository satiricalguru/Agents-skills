#!/usr/bin/env python3
"""Generate a gradient hero banner SVG. No dependencies.
Usage: banner.py --title NAME --tagline "One line" --out assets/banner.svg [--accent "#7c3aed"] [--accent2 "#06b6d4"]
"""
import argparse
from html import escape
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--title", required=True)
ap.add_argument("--tagline", default="")
ap.add_argument("--out", default="assets/banner.svg")
ap.add_argument("--accent", default="#7c3aed")
ap.add_argument("--accent2", default="#06b6d4")
a = ap.parse_args()

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 320" width="1280" height="320">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{a.accent}"/><stop offset="1" stop-color="{a.accent2}"/>
    </linearGradient>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.5" fill="#fff" opacity=".12"/>
    </pattern>
  </defs>
  <rect width="1280" height="320" rx="24" fill="url(#g)"/>
  <rect width="1280" height="320" rx="24" fill="url(#dots)"/>
  <circle cx="1130" cy="60" r="140" fill="#fff" opacity=".08"/>
  <circle cx="1210" cy="290" r="90" fill="#fff" opacity=".06"/>
  <text x="80" y="170" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif" font-size="84" font-weight="800" fill="#fff">{escape(a.title)}</text>
  <text x="84" y="225" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif" font-size="30" fill="#fff" opacity=".9">{escape(a.tagline)}</text>
</svg>
'''
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
Path(a.out).write_text(svg)
print(f"saved {a.out}")
