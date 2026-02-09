#!/usr/bin/env python3
"""Main site: serves static files + config API for project access management."""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

CONFIG_FILE = os.environ.get('CONFIG_FILE', '/data/config.json')
VIP_KEY = os.environ.get('VIP_KEY', 'VIP')
STATIC_DIR = '/app/static'
PORT = int(os.environ.get('PORT', '80'))


def read_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"free": [], "order": []}


def write_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/api/config':
            config = read_config()
            self._json_response(200, config)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/config':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length))
            except (ValueError, json.JSONDecodeError):
                self._json_response(400, {"error": "bad request"})
                return

            if body.get('key') != VIP_KEY:
                self._json_response(403, {"error": "forbidden"})
                return

            config = read_config()
            if 'free' in body:
                config['free'] = list(body['free'])
            if 'order' in body:
                config['order'] = list(body['order'])
            write_config(config)

            self._json_response(200, {"ok": True})
        else:
            self._json_response(405, {"error": "method not allowed"})

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Only log errors
        if args and str(args[0]).startswith(('4', '5')):
            super().log_message(format, *args)


if __name__ == '__main__':
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Main site running on port {PORT}')
    server.serve_forever()
