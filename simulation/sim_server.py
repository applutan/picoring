import http.server
import socketserver
import json
import threading
import time
import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from controller import RingController
except ImportError:
    print("Error: Could not import controller. Make sure you are running this from the project root or simulation folder.")
    sys.exit(1)

# --- Shared Logic ---
controller = RingController()

# --- Animation Loop (Threaded for Sim) ---
def animation_loop():
    while True:
        if controller.state["running"]:
            time.sleep(controller.state["rate"])
            controller.advance()
        else:
            time.sleep(0.1)

thread = threading.Thread(target=animation_loop, daemon=True)
thread.start()

class SimHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # API: Status
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(controller.state).encode())
            return

        # API: Set Settings
        if self.path.startswith('/api/set'):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            bri = query.get('bri', [None])[0]
            rate = query.get('rate', [None])[0]
            controller.set_config(bri, rate)
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # API: Change Pattern
        if self.path.startswith('/api/pattern'):
            if 'dir=1' in self.path: controller.manual_change(1)
            elif 'dir=-1' in self.path: controller.manual_change(-1)
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # API: Align to Color
        if self.path.startswith('/api/align'):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            if 'c' in query:
                controller.set_alignment(query['c'][0])
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # API: Toggle
        if self.path == '/api/toggle':
            controller.toggle()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # Serve the MAIN index.html (the single source of truth)
        if self.path == '/' or self.path == '/index.html':
            # We need to serve the file from the PARENT directory
            try:
                # Assuming this script is running from project root via 'python3 simulation/sim_server.py'
                with open('index.html', 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
                return
            except FileNotFoundError:
                self.send_error(404, "index.html not found in root")
                return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

PORT = 8008
print(f"Simulation running at http://localhost:{PORT}")
print("Press Ctrl+C to stop.")

# Allow reuse of address to avoid "Address already in use" errors on restart
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), SimHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass