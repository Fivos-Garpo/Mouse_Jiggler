# Mouse Jiggler

A lightweight Windows mouse jiggler reconstructed from the original GUI executable and redesigned as a modular Python application.

## Features

- Randomized mouse movement
- Configurable maximum delay between movements
- Configurable runtime
- Pause / Resume without losing elapsed runtime
- Stop at any time
- Prevents Windows system/display sleep while active
- Modern, compact Tkinter GUI
- Background worker so the GUI remains responsive
- Windows executable named Mouse.exe

## Project structure

    Mouse_Jiggler/
    ├── Mouse.py
    ├── core/
    │   ├── __init__.py
    │   ├── jiggler.py
    │   └── windows.py
    ├── ui/
    │   ├── __init__.py
    │   └── app.py
    ├── requirements.txt
    ├── Mouse.spec
    ├── build.ps1
    └── .github/workflows/build.yml

## Run from source

Use Python 3.12 on Windows:

    python -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1
    pip install -r requirements.txt
    python Mouse.py

## Build Mouse.exe

On Windows:

    .\\build.ps1

The executable is created as dist\\Mouse.exe. GitHub Actions also builds the same executable and publishes it as a workflow artifact named Mouse.

## Controls

- Start — starts the jiggler with the selected settings.
- Pause — freezes mouse movement and the runtime counter.
- Resume — continues the same session from the paused state.
- Stop — terminates the current session.
