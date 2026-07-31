from __future__ import annotations

import argparse
import json
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

from . import t
from .cli import parseArgs
from .highlight import highlight

DEFAULT_PORT_NUMBER = 8080


# This class will handles any incoming request from
# the browser
class MyHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    def do_GET(self) -> None:
        input = urllib.parse.unquote(self.path[1:])
        args, _, data = input.partition("?")
        if not data:
            do_400(self, "Nothing to highlight - pass it as the query string.")
            return

        try:
            options = parseArgs(re.split(r"\s+", args) + [data], apArgs={"exit_on_error": False})
        except Exception as err:
            do_400(self, f"Error parsing path as arguments: {err}")
            return

        if options.inputType == "auto":
            inputType = "json" if data[0] == "[" else "text"
        else:
            inputType = options.inputType
        inVal: t.Element
        if inputType == "json":
            try:
                inVal = json.loads(data)
            except Exception as err:
                do_400(self, f"Error parsing query string as JSON: {err}")
                return
        else:
            inVal = ["pre", {}, data]

        try:
            outVal, _ = highlight(
                inVal,
                options.lang,
                output=options.output,
                lineNumbers=options.lineNumbers,
                lineHighlights=options.lineHighlights,
                lineStart=options.lineStart,
                unescape=options.unescape,
            )
            if options.output == "json":
                outVal = json.dumps(outVal)
            outVal += "\n"
            # html, css = highlight(data, lang=lang, output="html", unescape=True)
        except Exception as err:
            do_400(self, str(err))
            return
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(outVal.encode("utf-8"))

    def log_request(self, *args: t.Any) -> None:  # pylint: disable=unused-argument
        return


def do_400(handler: MyHandler, msg: str) -> None:
    handler.send_response(400)
    handler.send_header("Content-type", "text/plain")
    handler.end_headers()
    handler.wfile.write(msg.encode("utf-8"))


def server() -> None:
    try:
        # Create a web server and define the handler to manage the
        # incoming request
        ap = argparse.ArgumentParser(
            description="Runs a simple HTTP server that receives GET requests at the root level, with command-line options passed as path and the text to highlight as query, and returns a highlighted response. Use this to avoid repeatedly paying the Python startup cost when you're doing a whole lot of small highlights. See bs-highlight command-line help for details.",
        )
        ap.add_argument("--quiet", dest="quiet", action="store_true", help="Don't report informational messages.")
        ap.add_argument("--host", dest="host", default="localhost", help="The server host. (default: localhost)")
        ap.add_argument(
            "--port",
            dest="port",
            type=int,
            default=DEFAULT_PORT_NUMBER,
            help="The port number. (default: %(default)s)",
        )
        options = ap.parse_args()
        httpd = HTTPServer((options.host, options.port), MyHandler)
        if not options.quiet:
            print(f"Started httpserver on {options.host}:{options.port}")  # noqa: T201

        # Wait forever for incoming http requests
        httpd.serve_forever()

    except KeyboardInterrupt:
        if not options.quiet:
            print("^C received, shutting down the web server")  # noqa: T201
        httpd.socket.close()
