#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

# Pull all the highlighter imports up,
# so this folder can be used directly as a module
# if it's not installed the normal way.
from highlighter import *


def cli():
	import argparse
	import io
	import json
	import sys

	ap = argparse.ArgumentParser(description="Syntax-highlights JSON-encoded HTML.")
	ap.add_argument("lang",
	                help="What language the input should be highlighted as. Accepts all Pygments languages, plus 'webidl'.")
	ap.add_argument("--output", dest="output", choices=["json", "html"], default="json",
	                help="Pass 'json' to output the highlighted results as JSON-encoded HTML, or 'html' to output as an HTML string.")
	ap.add_argument("--numbers", dest="lineNumbers", action="store_true",
	                help="Include line numbers in the output.")
	ap.add_argument("--highlights", dest="lineHighlights", default=None,
	                help="A comma-separated list of line numbers and ranges, like '1, 3-5', which should be specially highlighted in the output.")
	ap.add_argument("--start", dest="lineStart", type=int, default=1,
	                help="Dictates what line number the first line of output should be considered as, affecting --numbers and --highlights.")
	options = vars(ap.parse_args())

	input = json.loads(sys.stdin.read(), encoding="utf-8")
	html,css = highlight(input, **options)
	print json.dumps({"html":html, "css":css})

if __name__ == '__main__':
	cli()
else:
	raise Exception("This is the CLI interface. Just import the module itself if using this from within Python.")
