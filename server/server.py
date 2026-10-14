"""
SEMAFORO server - Python stdlib + pyserial opcional
Arduino UNO -> Serial "RED:20" -> GET /api/status -> web
Uso:
  pip install pyserial
  python server/server.py --port COM3
  python server/server.py --simulate
Web: http://localhost:8000
"""
import argparse, glob, json, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DUR = {"RED": 20, "YELLOW": 5, "GREEN": 25}
PINS = {"RED": 2, "YELLOW": 3, "GREEN": 4}
ORDER = ["RED", "GREEN", "YELLOW"]
state = {"light": "RED", "pin": 2, "remaining": 20, "durations": DUR, "source": "simulacion", "port": None, "updated_at": time.time()}
lock = threading.Lock()

def set_state(light, remaining, source, port):
    with lock:
        state.update({"light": light, "pin": PINS.get(light, 2), "remaining": int(remaining), "source": source, "port": port, "updated_at": time.time()})

def parse_line(line: str):
    line = line.strip().upper().removeprefix("STATE:")
    if not line: return None
    parts = line.replace(",", " ").replace(":", " ").split()
    if len(parts) >= 2 and parts[0] in DUR:
        try: return parts[0], int(parts[1])
        except: return None
    return None

def serial_reader(port: str):
    import serial
    ser = serial.Serial(port, 9600, timeout=1)
    time.sleep(2)
    while True:
        p = parse_line(ser.readline().decode(errors="ignore"))
        if p: set_state(p[0], p[1], "arduino", port)

def sim_loop():
    while True:
        for light in ORDER:
            for r in range(DUR[light], 0, -1):
                with lock:
                    fresh = state["source"] == "arduino" and (time.time() - state["updated_at"] < 2)
                if fresh:
                    time.sleep(0.5); continue
                set_state(light, r, state.get("source") if state.get("source") == "arduino" else "simulacion", state.get("port"))
                time.sleep(1)

BASE = Path(__file__).parent
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body: bytes, ctype: str):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body))); self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (BASE.parent / "web" / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/status":
            with lock: payload = dict(state)
            self._send(200, json.dumps(payload).encode(), "application/json")
        else: self._send(404, b"Not found", "text/plain")
    def do_POST(self):
        if self.path == "/api/arduino":
            n = int(self.headers.get("Content-Length", 0))
            try:
                d = json.loads(self.rfile.read(n) or b"{}")
                light = str(d.get("light", "")).upper()
                if light in DUR:
                    set_state(light, int(d.get("remaining", DUR[light])), "arduino", d.get("port", "http"))
                    self._send(200, b'{"ok":true}', "application/json"); return
            except: pass
            self._send(400, b'{"ok":false}', "application/json")
        else: self._send(404, b"Not found", "text/plain")

def autodetect():
    try:
        import serial
        for p in ["COM3","COM4","COM5","COM6","COM7","COM8"]:
            try: s=serial.Serial(p,9600,timeout=0.5); s.close(); return p
            except: continue
    except: pass
    for p in glob.glob("/dev/ttyACM*")+glob.glob("/dev/ttyUSB*"): return p
    return None

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default=None); ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--web-port", type=int, default=8000)
    a = ap.parse_args()
    port = a.port or autodetect()
    if a.simulate or port is None:
        threading.Thread(target=sim_loop, daemon=True).start()
    else:
        threading.Thread(target=serial_reader, args=(port,), daemon=True).start()
        with lock: state["port"] = port
    print(f"Web en http://localhost:{a.web_port} (Arduino: {port})")
    ThreadingHTTPServer(("0.0.0.0", a.web_port), H).serve_forever()
