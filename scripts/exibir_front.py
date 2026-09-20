"""
Servidor local do Painel de Indicadores Socioeconomicos.

Uso:
    python scripts/exibir_front.py

Depois abra:
    http://localhost:8000
"""

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT / "front"

os.chdir(FRONT)

PORT = 8000

server = ThreadingHTTPServer(
    ("127.0.0.1", PORT),
    SimpleHTTPRequestHandler,
)

print("=" * 50)
print("PAINEL DE ÍNDICES SOCIOECONÔMICOS")
print("=" * 50)
print(f"Site: http://localhost:{PORT}")
print("Pressione Ctrl+C para encerrar.")
print()

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nServidor encerrado.")
finally:
    server.server_close()
