#!/bin/bash
# Build the two deliverable zips from the staged trees.
set -e
cd "$(dirname "$0")/.."
OUT="${1:-$PWD/dist}"
mkdir -p "$OUT"
cd stage
rm -f "$OUT/USABO-Biology-Concepts.zip" "$OUT/USABO-Biology-Formulas.zip"
zip -rq "$OUT/USABO-Biology-Concepts.zip" USABO-Biology-Concepts
zip -rq "$OUT/USABO-Biology-Formulas.zip" USABO-Biology-Formulas
ls -lh "$OUT"
