#!/bin/bash
# Build every driver. $1 = parallel jobs (default 3)
cd "$(dirname "$0")"
J=${1:-3}
python3 - << 'PY' > /tmp/drivers.txt
from tools_build_drivers import volume_map
for folder, base, driver in volume_map():
    print(driver)
print('main-index-concepts.tex')
print('main-index-formulas.tex')
print('how-to-learn.tex')
print('how-to-use-formulas.tex')
PY
xargs -P "$J" -I{} ./build1.sh {} < /tmp/drivers.txt
