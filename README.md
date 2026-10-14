# SEMAFORO · Arduino UNO + Web en vivo

Replica tu diseno de Figma **SEMAFORO** como pagina web que refleja el estado real de un Arduino UNO conectado por USB.

Figma: https://www.figma.com/design/8uEs15QedrEqrG7UgYjhTV/SEMAFORO
Repo: https://github.com/a01068064-lgtm/semaforo-arduino-uno

## 1. Que hace
- Arduino UNO prende en secuencia: **ROJO 20s → VERDE 25s → AMARILLO 5s** en loop.
- Cada segundo manda por Serial: `RED:20`, `GREEN:25`, `YELLOW:5`...
- El servidor lee ese Serial y expone `GET /api/status`.
- La web (estilo Figma) muestra foco activo, **PIN activo** y **cuenta regresiva**.

## 2. Hardware
| Luz | Pin Arduino UNO | Tiempo |
|-----|----------------|--------|
| Roja | 2 | 20 s |
| Amarilla | 3 | 5 s |
| Verde | 4 | 25 s |

Conexion LED: Pin → resistencia 220Ω → anodo LED, catodo → GND.
Serial: 9600 baud.

## 3. Estructura
```
arduino-uno/semaforo.ino  → codigo para Arduino UNO (Serial RED:/GREEN:/YELLOW:)
web/index.html            → pagina estilo Figma, lee /api/status cada 500ms
server/server.py          → servidor Python (serial + simulacion)
server/servidor.ps1       → servidor Windows sin dependencias (HttpListener)
docs/figma.md             → tokens del diseno Figma
```

## 4. Uso rapido (Windows)
1. Sube `arduino-uno/semaforo.ino` desde Arduino IDE al UNO.
2. Opcion A sin instalar nada:
```powershell
powershell -ExecutionPolicy Bypass -File server/servidor.ps1 -Puerto 8000
```
3. Opcion B con Python:
```bash
pip install pyserial
python server/server.py --port COM3
# sin Arduino:
python server/server.py --simulate
```
4. Abre http://localhost:8000

## 5. API
`GET /api/status` →
```json
{"light":"GREEN","pin":4,"remaining":13,"durations":{"RED":20,"YELLOW":5,"GREEN":25},"source":"arduino","port":"COM3"}
```
`POST /api/arduino` → `{"light":"RED","remaining":12}` (push manual)

## 6. Figma
Ver `docs/figma.md` para colores y medidas exactas.
