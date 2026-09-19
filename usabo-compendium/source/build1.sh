#!/bin/bash
# Build one volume. $1 = driver path relative to source/
set -u
cd "$(dirname "$0")"
src="$1"; base=$(basename "$src" .tex)
wd="build/$(echo "$src" | tr '/' '_')"
mkdir -p "$wd"
for i in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error=0 -output-directory="$wd" "$src" >/dev/null 2>&1
done
[ -f "$wd/$base.idx" ] && makeindex -q "$wd/$base.idx" >/dev/null 2>&1
pdflatex -interaction=nonstopmode -output-directory="$wd" "$src" >/dev/null 2>&1
err=$(grep -c "^!" "$wd/$base.log" 2>/dev/null); err=${err:-0}
if [ -f "$wd/$base.pdf" ]; then
  pg=$(pdfinfo "$wd/$base.pdf" 2>/dev/null | awk '/^Pages/{print $2}')
  echo "OK   err=${err:-0} pages=${pg:-?}  $src"
else
  echo "FAIL err=${err:-?}  $src"
fi
