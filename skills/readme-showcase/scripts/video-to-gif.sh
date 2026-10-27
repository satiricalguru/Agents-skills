#!/usr/bin/env bash
# Usage: video-to-gif.sh <in.mp4|mov> <out.gif> [width=900] [fps=15]
set -euo pipefail
in=$1; out=$2; w=${3:-900}; fps=${4:-15}
command -v ffmpeg >/dev/null || { echo "ffmpeg required (brew install ffmpeg)"; exit 1; }
f="fps=$fps,scale=$w:-1:flags=lanczos"
ffmpeg -v error -y -i "$in" -vf "$f,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5" "$out"
echo "saved $out ($(du -h "$out" | cut -f1))"
