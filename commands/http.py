from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from base64 import b64encode
import settings
from statistics import Statistics

username = settings.getb(b'HTTP_USERNAME')
password = settings.getb(b'HTTP_PASSWORD')
statistics = Statistics()

def add_parser(subparsers):
    parser = subparsers.add_parser('http', help='start http server')
    parser.set_defaults(func=run)

def run(args):
    server_address = ('', 8000)
    print("Starting server")
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    httpd.serve_forever()

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        return self.do_GET_api()

    def do_GET_api(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        data = json.dumps(obj=statistics.get(), indent=2)
        self.wfile.write(bytes(data, "utf-8"))
