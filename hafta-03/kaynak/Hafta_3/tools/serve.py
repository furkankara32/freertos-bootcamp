"""Local-only server for Web Serial UI. Open http://localhost:8766/."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import webbrowser
if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    server=ThreadingHTTPServer(('127.0.0.1',8766),partial(SimpleHTTPRequestHandler,directory=str(root)))
    print('Hafta 3: http://localhost:8766/ — Ctrl+C ile durdurun.')
    webbrowser.open('http://localhost:8766/')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
