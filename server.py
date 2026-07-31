#!/usr/bin/env python3
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import sys
import typing
import urllib.parse

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from highlighter import highlight

DEFAULT_PORT_NUMBER = 8080


# This class will handles any incoming request from
# the browser
class MyHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    def do_GET(self) -> None:
        input = urllib.parse.unquote(self.path[1:])
        lang, _, data = input.partition("?")
        if not data.startswith("["):
            do_404(self)
            return
        data = json.loads(data)

        try:
            html, css = highlight(data, lang=lang, output="html", unescape=True)
        except Exception as err:
            do_400(self, err)
            return
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_request(self, *args: typing.Any) -> None:
        return


def do_404(handler: MyHandler) -> None:
    handler.send_response(404)
    handler.send_header("Content-type", "text/plain")
    handler.end_headers()
    handler.wfile.write(b"Invalid request, must send JSON as the path.")


def do_400(handler: MyHandler, err: Exception) -> None:
    handler.send_response(400)
    handler.send_header("Content-type", "text/plain")
    handler.end_headers()
    if isinstance(err, SyntaxWarning):
        handler.wfile.write(str(err).encode("utf-8"))
    else:
        handler.wfile.write("Unexpected error:\n{0}".format(sys.exc_info()[0]).encode("utf-8"))


try:
    # Create a web server and define the handler to manage the
    # incoming request
    ap = argparse.ArgumentParser(
        description="Runs a simple HTTP server that receives GET requests at the root level, with command-line options passed as query args and the text to highlight as hash, and returns a highlighted response. Use this to avoid repeatedly paying the Python startup cost when you're doing a whole lot of small highlights. See the command-line help for details.",
    )
    ap.add_argument("--quiet", dest="quiet", action="store_true", help="Don't report informational messages.")
    ap.add_argument("--host", dest="host", default="", help="The server host. (default: localhost)")
    ap.add_argument("--port", dest="port", type=int, default=DEFAULT_PORT_NUMBER, help="The port number. (default: %(default)s)")
    options = vars(ap.parse_args())
    server = HTTPServer((options.host, options.port), MyHandler)
    if not options["quiet"]:
        print("Started httpserver on port ", options.port)

    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    if not options["quiet"]:
        print("^C received, shutting down the web server")
    server.socket.close()
