# Escoba del 15

## Project Description

Escoba del 15 is a desktop version of the traditional Spanish card game, built in Python with pygame. It uses the 40-card Spanish deck (oros, copas, espadas, bastos). On each turn, players try to capture cards from the table whose values add up to 15.

## Installation Instructions

You need **Python 3.10+** and `pip`.

```bash
git clone https://github.com/cis3296-f26/escoba-del-15.git
cd escoba-del-15
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Build Instructions

You can run the game straight from source with no build step. To make a standalone executable with PyInstaller:

```bash
pyinstaller --onefile --windowed --paths . --name escoba escoba/__main__.py
```

The executable is written to `dist/`.

## Run Instructions

From the project root, with the virtual environment active:

```bash
python -m escoba
```

A game window opens. To quit, close the window or press **Esc**.

To run the tests:

```bash
python -m pytest
```

## Release Instructions

Releases are built automatically by GitHub Actions (`.github/workflows/release.yml`). Pushing a tag that starts with `v` runs the tests, builds executables for Linux, Windows, and macOS, and attaches them to a GitHub Release.

```bash
git checkout main
git pull

git tag v0.1.0
git push origin v0.1.0
```
