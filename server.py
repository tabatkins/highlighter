#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import json
import os
import sys
import urllib2

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from highlighter import highlight

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):
	#Handler for the GET requests
	def do_GET(self):
		input = urllib2.unquote(self.path[1:])
		if not input.startswith("["):
			do_404(self)
			return
		input = json.loads(input)

		html,css = highlight(input, lang="html", output="html")
		self.send_response(200)
		self.send_header('Content-type',"text/plain")
		self.end_headers()
		self.wfile.write(html)

def do_404(handler):
	handler.send_response(404)
	handler.send_headers('Content-type','text/plain')
	handler.end_headers()
	handler.wfile.write("Invalid request, must send JSON as the path.")

try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER

	#Wait forever for incoming http requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
