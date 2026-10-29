#!/usr/bin/env bash
# foto_html.sh <arquivo.html> <largura> <altura> — PNG do HTML no Edge headless, com 9 s de tempo virtual (animações no fim)
set -e
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
f=$(cygpath -m "$(realpath "$1")"); png=$(cygpath -w "$(realpath "$1" | sed 's/\.html$/.png/')")
"$EDGE" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=9000 --user-data-dir="$(cygpath -w "$TEMP")\edge_foto_$$" --window-size="$2,$3" --screenshot="$png" "file:///$f" >/dev/null 2>&1
echo "$png"
