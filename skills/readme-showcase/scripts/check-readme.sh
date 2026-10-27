#!/usr/bin/env bash
# Usage: check-readme.sh [README.md]. Verifies local media exists, flags big files, lists external links.
set -uo pipefail
f=${1:-README.md}; dir=$(dirname "$f"); fail=0
refs=$(grep -oE '(src|srcset|href)="[^"]+"|\]\([^)]+\)' "$f" | sed -E 's/^(src|srcset|href)="//; s/"$//; s/^\]\(//; s/\)$//; s/ .*//')
while IFS= read -r r; do
  [ -z "$r" ] && continue
  case "$r" in http*|mailto:*|\#*) continue;; esac
  r=${r%%#*}; p="$dir/$(printf '%b' "${r//%/\\x}")"
  if [ ! -e "$p" ]; then echo "MISSING  $r"; fail=1
  elif [ -f "$p" ]; then
    kb=$(( $(wc -c <"$p") / 1024 ))
    [ "$kb" -gt 5120 ] && echo "LARGE    $r (${kb} KB; aim for <5 MB)"
  fi
done <<< "$refs"
grep -q '<img[^>]*src=' "$f" && grep -oE '<img[^>]*>' "$f" | grep -v 'alt=' | sed 's/^/NO-ALT   /'
grep -c 'TODO' "$f" >/dev/null && grep -n 'TODO' "$f" | sed 's/^/TODO     /'
echo "External links: $(grep -oE 'https?://[^ )"]+' "$f" | sort -u | wc -l | tr -d ' ')"
[ $fail -eq 0 ] && echo "OK: all local references exist" || exit 1
