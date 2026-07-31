from __future__ import annotations

import argparse
import json
import sys

from . import t
from .highlight import highlight


def cli(argv: list[str] | None = None) -> None:
    options = parseArgs(argv)
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

    outVal, css = highlight(
        inVal,
        options.lang,
        output=options.output,
        lineNumbers=options.lineNumbers,
        lineHighlights=options.lineHighlights,
        lineStart=options.lineStart,
        unescape=options.unescape,
    )

    print(formatOutput(outVal, css, options))  # noqa: T201


def formatOutput(outVal: t.Element | str, css: str, options: argparse.Namespace) -> str:
    if options.just == "html":
        if isinstance(outVal, str):
            return outVal
        else:
            return json.dumps(outVal)
    elif options.just == "css":
        return css
    else:
        # No need to switch on options.output here;
        # outval will already either be an HTML string or a JSON object,
        # both of which will serialize property with dumps here.
        return json.dumps({"html": outVal, "css": css})


def parseArgs(argv: list[str] | None = None, apArgs: dict[str, t.Any] | None = None) -> argparse.Namespace:
    """
    Parses the args from argv, or the sys.argv is not passed.
    If `throw` is true, will throw errors;
    othewise, will print to stderr and exit.
    """
    if apArgs is None:
        apArgs = {}
    ap = argparse.ArgumentParser(description="Syntax-highlights JSON-encoded HTML.", **apArgs)
    ap.add_argument(
        "lang",
        help="What language the input should be highlighted as. Accepts all Pygments languages, plus 'webidl'.",
    )
    ap.add_argument(
        "src",
        default="-",
        help="The input text/markup to be highlighted. Should be either source text, or JSON-encoded HTML of a (possibly marked-up) element whose text should be highlighted. Pass - to take from STDIN.",
    )
    ap.add_argument(
        "--input",
        dest="inputType",
        choices=["auto", "json", "text"],
        default="auto",
        help="Chooses whether the input is source text, or JSON-encoded HTML whose text should be highlighted. 'auto' chooses based on if the first character is [ (json) or not (text). (default: %(default)s)",
    )
    ap.add_argument(
        "--output",
        dest="output",
        choices=["json", "html"],
        default="json",
        help="Pass 'json' to output the highlighted results as JSON-encoded HTML, or 'html' to output as an HTML string. (default: %(default)s)",
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
        help="Specifies what line number the first line of output should be considered as, affecting --numbers and --highlights. (default: %(default)s)",
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
        choices=["both", "html", "css"],
        default="html",
        help="Specifies whether you want just the highlighted html, just the CSS needed for that HTML, or both wrapped in a {'html':..., 'css':...} JSON object. (default: %(default)s)",
    )
    options = ap.parse_args(argv)
    return options
