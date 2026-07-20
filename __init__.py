#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pull all the highlighter imports up,
# so this folder can be used directly as a module
# if it's not installed the normal way.
from . import highlighter


def cli() -> None:
    import argparse
    import io
    import json
    import sys

    ap = argparse.ArgumentParser(description="Syntax-highlights JSON-encoded HTML.")
    ap.add_argument(
        "src",
        help="The input text/markup to be highlighted. Should be either source text, or JSON-encoded HTML of a (possibly marked-up) element whose text should be highlighted. Pass - to take from STDIN.",
    )
    ap.add_argument(
        "lang", help="What language the input should be highlighted as. Accepts all Pygments languages, plus 'webidl'."
    )
    ap.add_argument(
        "--input",
        dest="inputType",
        choices=["auto", "json", "text"],
        default="auto",
        help="Chooses whether the input is source text, or JSON-encoded HTML whose text should be highlighted. The default 'auto' chooses based on if the first character is [ (json) or not (text).",
    )
    ap.add_argument(
        "--output",
        dest="output",
        choices=["json", "html"],
        default="json",
        help="Pass 'json' to output the highlighted results as JSON-encoded HTML, or 'html' to output as an HTML string. Defaults to json.",
    )
    ap.add_argument("--numbers", dest="lineNumbers", action="store_true", help="Include line numbers in the output.")
    ap.add_argument(
        "--highlights",
        dest="lineHighlights",
        default=None,
        help="A comma-separated list of line numbers and ranges, like '1, 3-5', which should be specially highlighted in the output.",
    )
    ap.add_argument(
        "--start",
        dest="lineStart",
        type=int,
        default=1,
        help="Dictates what line number the first line of output should be considered as, affecting --numbers and --highlights.",
    )
    ap.add_argument(
        "--unescape",
        dest="unescape",
        action="store_true",
        help="Does a quick unescape pass over the input HTML, reverting one level of HTML escapes for &<>'\", and decimal/hex escapes. Use if your DOM implementation doesn't convert escapes to text. Won't unescape any other HTML escapes, so beware!",
    )
    ap.add_argument(
        "--just",
        dest="just",
        choices=["html", "css"],
        default=None,
        help="Returns just the HTML or CSS value (no wrapping JSON object). Default is a JSON wrapper object with 'html' and 'css' keys.",
    )
    options = ap.parse_args()

    if options.src == "-":
        inText = sys.stdin.read()
    else:
        inText = options.src

    if options.inputType == "auto":
        inputType = "json" if inText[0] == "[" else "text"
    else:
        inputType = options.inputType

    if inputType == "json":
        inVal = json.loads(inText, encoding="utf-8")
    else:
        inVal = ["pre", {}, inText]

    outVal, css = highlighter.highlight(
        inVal,
        options.lang,
        output=options.output,
        lineNumbers=options.lineNumbers,
        lineHighlights=options.lineHighlights,
        lineStart=options.lineStart,
        unescape=options.unescape,
    )

    if options.just == "html":
        if isinstance(outVal, str):
            print(outVal.encode("utf-8"))
        else:
            print(json.dumps(outVal).encode("utf-8"))
    elif options.just == "css":
        print(css.encode("utf-8"))
    else:
        print(json.dumps({"html": outVal, "css": css}).encode("utf-8"))


if __name__ == "__main__":
    cli()
else:
    raise Exception("This is the CLI interface. Just import the module itself if using this from within Python.")
