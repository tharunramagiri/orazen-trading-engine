#!/usr/bin/env python3
import http.server, socketserver, os

PORT = int(os.getenv('PORT', 3000))
os.chdir('/app/web')
handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(('', PORT), handler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
