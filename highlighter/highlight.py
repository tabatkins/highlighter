# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
import collections
import itertools
import re

import pygments
import widlparser
from pygments import formatters
from pygments.lexers import get_lexer_by_name

from . import dom, styles, t
from .lexers import CSSLexer

if t.TYPE_CHECKING:
    from pygments.lexer import Lexer

customLexers: dict[str, t.Callable[[], Lexer]] = {
    "css": CSSLexer,
}

ColoredText = collections.namedtuple("ColoredText", ["text", "color"])


def die(msg: str, *rargs: t.Any, **kwargs: dict[t.Any, t.Any]) -> t.NoReturn:
    raise Exception(msg.format(*rargs, **kwargs))


def warn(msg: str, *rargs: t.Any, **kwargs: dict[t.Any, t.Any]) -> t.NoReturn:
    raise SyntaxWarning(msg.format(*rargs, **kwargs))


def highlight(
    html: t.Element,
    lang: str,
    lineNumbers: bool = False,
    lineStart: int = 1,
    lineHighlights: str | set[int] | None = None,
    output: str = "json",
    unescape: bool = False,
) -> tuple[t.Element, str] | tuple[str, str]:
    if lineHighlights is None:
        lineHighlights = set()
    assert dom.isElement(html)
    if unescape:
        html = dom.unescapeElement(html)
    html = highlightEl(html, lang)
    css = styles.highlight

    # Find whether to add line numbers
    if lineNumbers or lineHighlights:
        if lineNumbers:
            css += styles.lineNumber
        if lineHighlights is not None:
            if isinstance(lineHighlights, str):
                lineHighlights = parseHighlightString(lineHighlights)
            css += styles.lineHighlight
        html = addLineWrappers(html, numbers=lineNumbers, start=lineStart, highlights=lineHighlights)

    if output == "json":
        return html, css
    elif output == "html":
        return serializeToHtml(html), css
    else:
        die("Unknown output mode '{0}', should be 'json' or 'html'.", output)


def parseHighlightString(text: str) -> set[int]:
    lineHighlights: set[int] = set()
    text = re.sub(r"\s*", "", text)
    for item in text.split(","):
        if "-" in item:
            # Range, format of DDD-DDD
            low, _, high = item.partition("-")
            try:
                low = int(low)
                high = int(high)
            except ValueError:
                die("Error parsing line-highlight range '{0}' - must be `int-int`.", item)
            if low >= high:
                die("line-highlight ranges must be well-formed lo-hi - got '{0}'.", item)
            lineHighlights.update(range(low, high + 1))
        else:
            try:
                item = int(item)
            except ValueError:
                die("Error parsing line-highlight value '{0}' - must be integers.", item)
            lineHighlights.add(item)

    return lineHighlights


def highlightEl(el: t.Element, lang: str) -> t.Element:
    text = dom.textContent(el)
    if lang == "webidl":
        coloredText = highlightWithWebIDL(text)
    else:
        coloredText = highlightWithPygments(text, lang)
    return mergeHighlighting(el, coloredText)


def highlightWithWebIDL(text: str) -> t.Deque[ColoredText]:
    """
    Trick the widlparser emitter,
    which wants to output HTML via wrapping with start/end tags,
    into instead outputting a stack-based text format.
    A \1 indicates a new stack push;
    the text between the \1 and the \2 is the class to be pushed.
    A \3 indicates a stack pop.
    All other text is colored with the class currently on top of the stack.
    """

    class IDLUI:
        def warn(self, msg: str) -> None:
            warn("{0}", msg.rstrip())

        def note(self, msg: str) -> None:
            pass

    class HighlightMarker:
        # Just applies highlighting classes to IDL stuff.
        def markup_type_name(
            self,
            text: str,  # pylint: disable=unused-argument
            construct: widlparser.constructs.Construct,  # pylint: disable=unused-argument
        ) -> tuple[str | None, str | None]:
            return ("\1n\2", "\3")

        def markup_name(
            self,
            text: str,  # pylint: disable=unused-argument
            construct: widlparser.constructs.Construct,  # pylint: disable=unused-argument
        ) -> tuple[str | None, str | None]:
            return ("\1g\2", "\3")

        def markup_keyword(
            self,
            text: str,  # pylint: disable=unused-argument
            construct: widlparser.constructs.Construct,  # pylint: disable=unused-argument
        ) -> tuple[str | None, str | None]:
            return ("\1b\2", "\3")

        def markup_enum_value(
            self,
            text: str,  # pylint: disable=unused-argument
            construct: widlparser.constructs.Construct,  # pylint: disable=unused-argument
        ) -> tuple[str | None, str | None]:
            return ("\1s\2", "\3")

    if "\1" in text or "\2" in text or "\3" in text:
        die(
            "WebIDL text contains some U+0001-0003 characters, which are used by the highlighter. This block can't be highlighted. :(",
        )
        return

    widl = widlparser.parser.Parser(text, IDLUI())
    widlStack = str(widl.markup(t.cast("widlparser.protocols.Marker", HighlightMarker())))
    return coloredTextFromWidlStack(widlStack)


def coloredTextFromWidlStack(widlText: str) -> t.Deque[ColoredText]:
    coloredTexts: t.Deque[ColoredText] = collections.deque()
    colors: list[str] = []
    currentText = ""
    mode = "text"
    for char in widlText:
        if mode == "text":
            if char == "\1":
                if colors:
                    coloredTexts.append(ColoredText(currentText, colors[-1]))
                else:
                    coloredTexts.append(ColoredText(currentText, None))
                currentText = ""
                mode = "color"
                continue
            elif char == "\2":
                assert False, r"Encountered a \2 while in text mode"
                continue
            elif char == "\3":
                assert colors, r"Encountered a \3 without any colors on stack."
                coloredTexts.append(ColoredText(currentText, colors.pop()))
                currentText = ""
                continue
            else:
                currentText += char
        elif mode == "color":
            if char == "\1":
                assert False, r"Encountered a \1 while in color mode."
                continue
            elif char == "\2":
                colors.append(currentText)
                currentText = ""
                mode = "text"
                continue
            elif char == "\3":
                assert False, r"Encountered a \3 while in color mode."
                continue
            else:
                currentText += char
                continue
    assert len(colors) == 0, r"Colors stack wasn't empty at end, \1 and \3s aren't balanced?"
    if currentText:
        coloredTexts.append(ColoredText(currentText, None))
    return coloredTexts


def highlightWithPygments(text: str, lang: str) -> t.Deque[ColoredText]:
    lexer = lexerFromLang(lang)
    if lexer is None:
        die("'{0}' isn't a known syntax-highlighting language. See http://pygments.org/docs/lexers/.", lang)
        return
    rawTokens = str(pygments.highlight(text, lexer, formatters.RawTokenFormatter()), encoding="utf-8")
    coloredText = coloredTextFromRawTokens(rawTokens)
    return coloredText


def mergeHighlighting(el: t.Element, coloredText: t.Deque[ColoredText]) -> t.Element:
    # Merges a tree of Pygment-highlighted HTML
    # into the original element's markup.
    # This works because Pygment effectively colors each character with a highlight class,
    # merging them together into runs of text for convenience/efficiency only;
    # the markup structure is a flat list of sibling elements containing raw text
    # (and maybe some un-highlighted raw text between them).
    def createEl(color: str, text: str) -> t.Element:
        return dom.createElement("c-", {color: ""}, text)

    def colorizeEl(el: t.Element, coloredText: t.Deque[ColoredText]) -> t.Element:
        elChildren = dom.children(el)
        el = dom.withoutChildren(el)
        for node in elChildren:
            if dom.isElement(node):
                dom.appendChild(el, colorizeEl(node, coloredText))
            else:
                dom.appendChild(el, *colorizeText(node, coloredText))
        return el

    def colorizeText(text: str, coloredText: t.Deque[ColoredText]) -> list[t.Node]:
        nodes = []
        while text and coloredText:
            nextColor = coloredText.popleft()
            if len(nextColor.text) <= len(text):
                if nextColor.color is None:
                    nodes.append(nextColor.text)
                else:
                    nodes.append(createEl(nextColor.color, nextColor.text))
                text = text[len(nextColor.text) :]
            else:  # Need to use only part of the nextColor node
                if nextColor.color is None:
                    nodes.append(text)
                else:
                    nodes.append(createEl(nextColor.color, text))
                # Truncate the nextColor text to what's unconsumed,
                # and put it back into the deque
                nextColor = ColoredText(nextColor.text[len(text) :], nextColor.color)
                coloredText.appendleft(nextColor)
                text = ""
        return nodes

    # Remove empty colored texts
    coloredText = collections.deque(x for x in coloredText if x.text)
    return colorizeEl(el, coloredText)


def serializeToHtml(el: t.Element) -> str:
    voidEls = frozenset(
        [
            "area",
            "base",
            "br",
            "col",
            "command",
            "embed",
            "hr",
            "img",
            "input",
            "keygen",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        ],
    )
    html = "<{0}".format(dom.tagName(el))
    for attrName, attrValue in dom.attrs(el).items():
        if attrValue == "":
            html += " {0}".format(attrName)
        else:
            html += " {0}='{1}'".format(attrName, dom.escapeHtml(attrValue))
    html += ">"
    if dom.tagName(el) in voidEls:
        return html
    for child in dom.children(el):
        if dom.isElement(child):
            html += serializeToHtml(child)
        else:
            html += dom.escapeHtml(child)
    html += "</{0}>".format(dom.tagName(el))
    return html


def coloredTextFromRawTokens(text: str) -> t.Deque[ColoredText]:
    colorFromName = {
        "Token.Comment": "c",
        "Token.Keyword": "k",
        "Token.Literal": "l",
        "Token.Name": "n",
        "Token.Operator": "o",
        "Token.Punctuation": "p",
        "Token.Comment.Multiline": "d",
        "Token.Comment.Preproc": "cp",
        "Token.Comment.Single": "c1",
        "Token.Comment.Special": "cs",
        "Token.Keyword.Constant": "kc",
        "Token.Keyword.Declaration": "a",
        "Token.Keyword.Namespace": "kn",
        "Token.Keyword.Pseudo": "kp",
        "Token.Keyword.Reserved": "kr",
        "Token.Keyword.Type": "b",
        "Token.Literal.Date": "ld",
        "Token.Literal.Number": "m",
        "Token.Literal.String": "s",
        "Token.Name.Attribute": "e",
        "Token.Name.Class": "nc",
        "Token.Name.Constant": "no",
        "Token.Name.Decorator": "nd",
        "Token.Name.Entity": "ni",
        "Token.Name.Exception": "ne",
        "Token.Name.Function": "nf",
        "Token.Name.Label": "nl",
        "Token.Name.Namespace": "nn",
        "Token.Name.Property": "py",
        "Token.Name.Tag": "f",
        "Token.Name.Variable": "g",
        "Token.Operator.Word": "ow",
        "Token.Literal.Number.Bin": "mb",
        "Token.Literal.Number.Float": "mf",
        "Token.Literal.Number.Hex": "mh",
        "Token.Literal.Number.Integer": "mi",
        "Token.Literal.Number.Oct": "mo",
        "Token.Literal.String.Backtick": "sb",
        "Token.Literal.String.Char": "sc",
        "Token.Literal.String.Doc": "sd",
        "Token.Literal.String.Double": "u",
        "Token.Literal.String.Escape": "se",
        "Token.Literal.String.Heredoc": "sh",
        "Token.Literal.String.Interpol": "si",
        "Token.Literal.String.Other": "sx",
        "Token.Literal.String.Regex": "sr",
        "Token.Literal.String.Single": "t",
        "Token.Literal.String.Symbol": "ss",
        "Token.Name.Variable.Class": "vc",
        "Token.Name.Variable.Global": "vg",
        "Token.Name.Variable.Instance": "vi",
        "Token.Literal.Number.Integer.Long": "il",
    }

    def addCtToList(list: t.Deque[ColoredText], ct: ColoredText) -> None:
        if "\n" in ct.text:
            # Break apart the formatting so that the \n is plain text,
            # so it works better with line numbers.
            textBits = ct.text.split("\n")
            list.append(ColoredText(textBits[0], ct.color))
            for bit in textBits[1:]:
                list.append(ColoredText("\n", None))
                list.append(ColoredText(bit, ct.color))
        else:
            list.append(ct)

    textList: t.Deque[ColoredText] = collections.deque()
    currentCT: ColoredText | None = None
    for line in text.split("\n"):
        if not line:
            continue
        tokenName, _, tokenTextRepr = line.partition("\t")
        color = colorFromName.get(tokenName)
        text = ast.literal_eval(tokenTextRepr)
        if not text:
            continue
        if not currentCT:
            currentCT = ColoredText(text, color)
        elif currentCT.color == color:
            # Repeated color, merge into current
            currentCT = currentCT._replace(text=currentCT.text + text)
        else:
            addCtToList(textList, currentCT)
            currentCT = ColoredText(text, color)
    if currentCT:
        addCtToList(textList, currentCT)
    return textList


def normalizeLanguageName(lang: str) -> str:
    # Translates some names to ones Pygment understands
    if lang == "aspnet":
        return "aspx-cs"
    if lang in ["markup", "svg"]:
        return "html"
    if lang == "idl":
        return "webidl"
    return lang


def lexerFromLang(lang: str) -> Lexer | None:
    if lang in customLexers:
        return customLexers[lang]()
    try:
        return get_lexer_by_name(lang, encoding="utf-8", stripAll=True)
    except:
        return None


def addLineWrappers(
    el: t.Element,
    numbers: bool = True,
    start: int = 1,
    highlights: set[int] | None = None,
) -> t.Element:
    # Wrap everything between each top-level newline with a line tag.
    # Add an attr for the line number, and if needed, the end line.
    if highlights is None:
        highlights = set()
    lineWrapper = dom.E.span({"class": "line"})
    elChildren = dom.children(el)
    el = dom.withoutChildren(el)
    for node in elChildren:
        if dom.isElement(node):
            dom.appendChild(lineWrapper, node)
        else:
            while True:
                if "\n" in node:
                    pre, _, post = node.partition("\n")
                    dom.appendChild(lineWrapper, pre)
                    dom.appendChild(el, dom.E.span({"class": "line-no"}))
                    dom.appendChild(el, lineWrapper)
                    lineWrapper = dom.E.span({"class": "line"})
                    node = post
                else:
                    dom.appendChild(lineWrapper, node)
                    break
    if len(lineWrapper):
        dom.appendChild(el, dom.E.span({"class": "line-no"}))
        dom.appendChild(el, lineWrapper)
    # Number the lines
    lineNumber = start
    for lineNo, lineWrapper in grouper(dom.children(el), 2):
        assert lineNo is not None
        assert dom.isElement(lineNo)
        assert lineWrapper is not None
        assert dom.isElement(lineWrapper)
        if numbers or lineNumber in highlights:
            dom.attrs(lineNo)["data-line"] = str(lineNumber)
        if lineNumber in highlights:
            dom.addClass(lineNo, "highlight-line")
            dom.addClass(lineWrapper, "highlight-line")
        internalNewlines = countInternalNewlines(lineWrapper)
        if internalNewlines:
            for i in range(1, internalNewlines + 1):
                if (lineNumber + i) in highlights:
                    dom.addClass(lineNo, "highlight-line")
                    dom.addClass(lineWrapper, "highlight-line")
                    dom.attrs(lineNo)["data-line"] = str(lineNumber)
            lineNumber += internalNewlines
            if numbers:
                dom.attrs(lineNo)["data-line-end"] = str(lineNumber)
        lineNumber += 1
    dom.addClass(el, "line-numbered")
    return el


def countInternalNewlines(el: t.Element) -> int:
    count = 0
    for node in dom.children(el):
        if dom.isElement(node):
            count += countInternalNewlines(node)
        else:
            count += node.count("\n")
    return count


def grouper[T](
    iterable: t.Sequence[T],
    n: int,
    fillvalue: T | None = None,
) -> itertools.zip_longest[tuple[T | None, ...]]:
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)


if __name__ == "__main__":

    def main() -> t.NoReturn:
        msg = "Not intended to be run at command-line; run ../__init__.py."
        raise Exception(msg)

    main()
