#!/usr/bin/env sh
cd "$(dirname "$0")" || exit 1

if [ ! -x ".venv/bin/python" ]; then
    echo "run setup.sh first"
    exit 1
fi

if [ "$(uname)" = "Darwin" ]; then
    # mac gets a .app, zipped so it survives being sent around
    .venv/bin/python -m PyInstaller --windowed --noconfirm --name escoba \
        --paths . --add-data "escoba/assets:escoba/assets" escoba/__main__.py || exit 1
    ditto -c -k --keepParent dist/escoba.app dist/escoba-mac.zip
    echo "built dist/escoba-mac.zip"
else
    .venv/bin/python -m PyInstaller --onefile --windowed --noconfirm --name escoba \
        --paths . --add-data "escoba/assets:escoba/assets" escoba/__main__.py || exit 1
    echo "built dist/escoba"
fi
