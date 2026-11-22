#!/usr/bin/env python3
"""Servidor de pruebas para esta app (solo biblioteca estándar).

Sirve los ficheros de esta carpeta y reenvía la API de TeleHome a un servicio en marcha,
imitando lo que hace Apache en el servidor (la app busca la API en /rafa/telehome/api/).

    python3 servir.py                          # app en http://127.0.0.1:8080/, servicio en 127.0.0.1:8765
    python3 servir.py --api http://127.0.0.1:8765 --port 8080
    python3 servir.py --host 0.0.0.0           # visible desde el iPad de la misma red Wi-Fi

El servicio se arranca aparte (en simulación, sin dispositivos reales):
    cd ../../../../code/telemetria/home/telehome-enchufes && python3 -m telehome_enchufes serve --simulate 3 --no-browser

Aviso: con --host 0.0.0.0 cualquiera de tu red puede abrir la app y, a través de ella, el servicio.
Úsalo solo para probar y con el servicio en simulación o con contraseña.
"""
import argparse
import http.client
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

AQUI = Path(__file__).resolve().parent
PREFIJO = "/rafa/telehome/"          # ruta bajo la que Apache publica el servicio
SALTAR = {"host", "origin", "referer", "connection", "content-length", "accept-encoding"}


class Manejador(BaseHTTPRequestHandler):
    api = ("127.0.0.1", 8765)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, self.path))

    # ---- reenvío al servicio ------------------------------------------------
    def _proxy(self):
        ruta = self.path[len(PREFIJO) - 1:] or "/"      # /rafa/telehome/api/state -> /api/state
        n = int(self.headers.get("Content-Length") or 0)
        cuerpo = self.rfile.read(n) if n else None
        cabeceras = {k: v for k, v in self.headers.items() if k.lower() not in SALTAR}
        try:
            c = http.client.HTTPConnection(self.api[0], self.api[1], timeout=20)
            c.request(self.command, ruta, body=cuerpo, headers=cabeceras)
            r = c.getresponse()
            datos = r.read()
        except OSError as exc:
            self.send_error(502, "No se puede hablar con el servicio: %s" % exc)
            return
        self.send_response(r.status)
        for k, v in r.getheaders():
            if k.lower() not in ("transfer-encoding", "connection", "content-length"):
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(datos)

    # ---- ficheros de esta carpeta -------------------------------------------
    def _fichero(self):
        nombre = urlsplit(self.path).path.lstrip("/") or "index.html"
        destino = (AQUI / nombre).resolve()
        if AQUI not in destino.parents and destino != AQUI or not destino.is_file():
            self.send_error(404, "No encontrado")
            return
        datos = destino.read_bytes()
        tipo = mimetypes.guess_type(destino.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", tipo + ("; charset=utf-8" if tipo.startswith("text/") else ""))
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(datos)

    def _enruta(self):
        if self.path.startswith(PREFIJO):
            self._proxy()
        elif self.command in ("GET", "HEAD"):
            self._fichero()
        else:
            self.send_error(405, "Método no permitido")

    do_GET = do_HEAD = do_POST = do_PUT = do_DELETE = do_OPTIONS = _enruta


def main() -> int:
    p = argparse.ArgumentParser(description="Sirve la app de iPad y reenvía la API de TeleHome.")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--host", default="127.0.0.1", help="0.0.0.0 para verla desde el iPad (solo para probar)")
    p.add_argument("--api", default="http://127.0.0.1:8765", help="servicio TeleHome al que reenviar")
    a = p.parse_args()
    u = urlsplit(a.api)
    Manejador.api = (u.hostname or "127.0.0.1", u.port or 8765)
    ThreadingHTTPServer.allow_reuse_address = True
    ThreadingHTTPServer.daemon_threads = True
    s = ThreadingHTTPServer((a.host, a.port), Manejador)
    print("App en http://%s:%d/   API -> %s%s" % (a.host, a.port, a.api, PREFIJO))
    print("Pulsa Ctrl+C para salir.")
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
