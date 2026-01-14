# Pico 2W LED Ring Project

## Overview
This project runs on a Raspberry Pi Pico 2W to control a 16-element WS2812B RGB LED ring. It features a web interface for controlling brightness, animation speed, pattern selection, and **global pattern alignment**.

A local **Simulation Mode** allows developing and testing the UI and logic on a PC without the hardware.

## Architecture
The project uses a split architecture to maximize code reuse between the Pico and the PC Simulation:
- **`controller.py` (Shared):** Contains the "Business Logic". Manages state, pattern rotation/alignment, and palette mapping.
- **`index.html` (Shared):** The frontend dashboard. Includes a JS/Canvas visualizer that works for both the Simulation and the real Pico.
- **`patterns.py` (Shared):** Contains the list of 192 encoded patterns.

## Hardware Driver (`main.py`)
- **Platform:** Raspberry Pi Pico 2W (MicroPython).
- **Function:** Handles Wi-Fi connection, runs the async web server, and drives the physical WS2812B LEDs using `machine` and `neopixel`.
- **Mapping:** LEDs are mapped **Counter-Clockwise**, with Index 0 at the top.

## Simulation Driver (`simulation/sim_server.py`)
- **Platform:** PC / Linux (Python 3).
- **Function:** Runs a standard `http.server` to host the API and UI. Uses a background thread to mimic the Pico's animation loop.
- **Visuals:** Rely entirely on the `index.html` canvas visualizer.

## API Endpoints
All state is managed by `controller.py`.
- `GET /api/status`: Returns JSON with current state (`idx`, `disp`, `bri`, `rate`, `align_target`).
- `GET /api/set?bri=X&rate=Y`: Updates brightness and rate.
- `GET /api/pattern?dir=1`: Navigates to next/prev pattern.
- `GET /api/toggle`: Pauses/Resumes auto-cycling.
- `GET /api/align?c=N`: Sets the **Global Alignment Target**. The controller automatically rotates all patterns so the first occurrence of color digit `N` is at Index 0.

## Setup
1.  **Pico:** Upload `main.py`, `controller.py`, `patterns.py`, `secrets.py`, and `index.html`.
2.  **Simulation:** Run `python3 simulation/sim_server.py` and visit `http://localhost:8008`.