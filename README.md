# Pico 2W RGB LED Ring Controller

A MicroPython-based controller for a 16-element WS2812 (NeoPixel) RGB LED ring, featuring a responsive web interface and a local development simulator.

## Features

- **192 Built-in Patterns:** Optimized patterns using 8 high-contrast colors.
- **Web Dashboard:** Mobile-friendly UI to control the device over Wi-Fi.
- **Global Alignment:** "Pin" any color to the 12 o'clock position; patterns automatically rotate to maintain that alignment.
- **Real-time Controls:** Adjustable brightness and animation rate.
- **Hardware Simulator:** Test the UI and logic on your PC without hardware using a Python-based server and HTML5 Canvas visualizer.
- **Shared Logic:** Uses a unified controller for both hardware and simulation to ensure identical behavior.

## Project Structure

- `main.py`: The entry point for the Raspberry Pi Pico 2W.
- `controller.py`: The core logic managing pattern rotation, state, and alignment.
- `index.html`: The web dashboard (served by the Pico or the Simulator).
- `patterns.py`: 192 encoded pattern strings.
- `simulation/`: Local simulation environment for PC testing.

## Hardware Setup

1. **Microcontroller:** Raspberry Pi Pico 2W.
2. **LED Ring:** 16-element WS2812B (5050 SMD).
3. **Wiring:**
   - **VCC:** Connect to VBUS (Pin 40) or an external 5V supply.
   - **GND:** Connect to any GND pin.
   - **Data:** Connect to GPIO 15 (Pin 20).

## Installation (Pico 2W)

1. Create a `secrets.py` file on your Pico:
   ```python
   SSID = "Your_WiFi_Name"
   PASSWORD = "Your_WiFi_Password"
   ```
2. Upload the following files to the root of the Pico:
   - `main.py`
   - `controller.py`
   - `patterns.py`
   - `index.html`
3. Run `main.py` and check the console for the IP address.

## Local Simulation

To test the patterns and interface on your computer:

```bash
python3 simulation/sim_server.py
```
Then visit **http://localhost:8008** in your browser.

## Pattern Encoding

Patterns are stored as 16-character strings (e.g., `0014156742352637`). Each digit (0-7) represents a color in the palette and appears exactly twice per pattern, ensuring balanced color distribution.
