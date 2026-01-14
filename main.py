import network
import socket
import time
import machine
import neopixel
import uasyncio as asyncio
from controller import RingController
import secrets

# --- Hardware Setup ---
LED_PIN = 15
NUM_LEDS = 16
pin = machine.Pin(LED_PIN, machine.Pin.OUT)
np = neopixel.NeoPixel(pin, NUM_LEDS)

# --- Shared Logic ---
controller = RingController()

# --- Helper Functions ---
def apply_brightness(color, brightness):
    return tuple(int(c * brightness) for c in color)

def update_leds():
    """Writes the current pattern to the LEDs."""
    try:
        p_str = controller.state["disp"]
        for i in range(min(NUM_LEDS, len(p_str))):
            color_idx = int(p_str[i])
            raw_color = controller.palette[color_idx]
            # Map Counter-Clockwise: Index 1 is to the left of 0 (LED 15)
            phy_idx = (NUM_LEDS - i) % NUM_LEDS
            np[phy_idx] = apply_brightness(raw_color, controller.state["bri"])
        np.write()
    except Exception as e:
        print("LED Error:", e)

# --- WiFi Connection ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    
    print(f"Connecting to {secrets.SSID}...")
    max_wait = 15
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(1)
        
    if wlan.status() != 3:
        print("WiFi Connection Failed")
    else:
        status = wlan.ifconfig()
        print('Connected! IP = ' + status[0])

# --- Async Tasks ---

async def led_loop():
    """Background task to handle LED animation."""
    print("Starting LED loop...")
    while True:
        update_leds()
        
        if controller.state["running"]:
            await asyncio.sleep(controller.state["rate"])
            controller.advance()
        else:
            await asyncio.sleep(0.1)

async def handle_client(reader, writer):
    """Handles a single HTTP request."""
    try:
        request_line = await reader.readline()
        if not request_line:
            return

        request = request_line.decode().strip()
        method, path, _ = request.split(" ")
        
        # Consume headers
        while True:
            header = await reader.readline()
            if header == b'\r\n' or header == b'\n':
                break

        # print(f"Request: {method} {path}") # Uncomment for debug

        response_body = ""
        content_type = "text/html"

        # --- API Endpoints ---
        if path.startswith("/api/status"):
            import json
            content_type = "application/json"
            response_body = json.dumps(controller.state)

        elif path.startswith("/api/set"):
            # Simple query param parsing
            if "?" in path:
                query = path.split("?")[1]
                parts = query.split("&")
                bri = None
                rate = None
                for p in parts:
                    k, v = p.split("=")
                    if k == "bri": bri = v
                    elif k == "rate": rate = v
                controller.set_config(bri, rate)
            response_body = "OK"

        elif path.startswith("/api/pattern"):
            if "dir=1" in path: controller.manual_change(1)
            elif "dir=-1" in path: controller.manual_change(-1)
            response_body = "OK"

        elif path.startswith("/api/align"):
            if "?" in path:
                query = path.split("?")[1]
                parts = query.split("&")
                for p in parts:
                    k, v = p.split("=")
                    if k == "c":
                        controller.set_alignment(v)
            response_body = "OK"

        elif path.startswith("/api/toggle"):
            controller.toggle()
            response_body = "OK"

        # --- Serve HTML ---
        elif path == "/" or path == "/index.html":
            try:
                with open("index.html", "r") as f:
                    response_body = f.read()
            except OSError:
                response_body = "<h1>Error: index.html not found</h1>"
        
        else:
            response_body = "404 Not Found"

        # Send Response
        writer.write(f'HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}'.encode())
        await writer.drain()
        
    except Exception as e:
        print("Server Error:", e)
    finally:
        writer.close()
        await writer.wait_closed()

async def web_server():
    print("Starting Web Server...")
    server = await asyncio.start_server(handle_client, '0.0.0.0', 80)
    while True:
        await asyncio.sleep(3600)

async def main():
    connect_wifi()
    asyncio.create_task(led_loop())
    await web_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
