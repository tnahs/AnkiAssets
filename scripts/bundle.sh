#! /bin/zsh

# https://unix.stackexchange.com/a/115431
root=${0:A:h:h}

cd "$root/addon"

zip  \
    --recurse-paths ../bundle/anki-assets.ankiaddon . \
    --exclude "**/.*" \
    --include \
        "./src/**.py" \
        "./src/assets/**" \
        "./__init__.py" \
        "./user_files/**" \
        "./manifest.json"