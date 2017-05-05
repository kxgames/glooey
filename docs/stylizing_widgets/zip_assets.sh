#!/usr/bin/env bash
set -euo pipefail

zip label_assets.zip    \
    label.py            \
    Lato-Regular.ttf    \

zip background_assets.zip   \
    background.py           \
    bottom_left.png         \
    bottom.png              \
    bottom_right.png        \
    center.png              \
    left.png                \
    right.png               \
    top_left.png            \
    top.png                 \
    top_right.png           \

zip button_assets.zip       \
    button.py               \
    base.png                \
    over.png                \
    down.png                \
