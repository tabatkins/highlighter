# -*- coding: utf-8 -*-

from __future__ import annotations

import collections
import dataclasses
import re

import pygments
import widlparser
from pygments.lexers import get_lexer_by_name

from . import dom, styles, t
from .lexers import CSSLexer

if t.TYPE_CHECKING:
    from pygments.lexer import Lexer

customLexers: dict[str, t.Callable[..., Lexer]] = {
    "css": CSSLexer,
}


@dataclasses.dataclass
class ColoredText:
    text: str
    # None indicates uncolored text
    color: str | None


def die(msg: str, *rargs: t.Any, **kwargs: dict[t.Any, t.Any]) -> t.NoReturn:
    raise Exception(msg.format(*rargs, **kwargs))


def warn(msg: str, *rargs: t.Any, **kwargs: dict[t.Any, t.Any]) -> t.NoReturn:
    raise SyntaxWarning(msg.format(*rargs, **kwargs))

@t.overload
def highlight(
    html: t.Element | str,
    lang: str,
    lineNumbers: bool = False,
    lineStart: int = 1,
    lineHighlights: str | set[int] | None = None,
    output: t.Literal["json"] = "json",
    unescape: bool = False,
) -> tuple[t.Element, str]: ...

@t.overload
def highlight(
    html: t.Element | str,
    lang: str,
    lineNumbers: bool = False,
    lineStart: int = 1,
    lineHighlights: str | set[int] | None = None,
    output: t.Literal["html"] = "html",
    unescape: bool = False,
) -> tuple[str, str]: ...

def highlight(
    html: t.Element | str,
    lang: str,
    lineNumbers: bool = False,
    lineStart: int = 1,
    lineHighlights: str | set[int] | None = None,
    output: str = "json",
    unescape: bool = False,
) -> tuple[t.Element, str] | tuple[str, str]:
    if lineHighlights is None:
        lineHighlights = set()
    if isinstance(html, str):
        html = t.cast("t.Element", ["pre", {}, html])
    dom.normalizeElement(html)
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
    coloredText = mergeColors(coloredText)
    coloredText = readdWhitespacePrefix(text, coloredText)
    return mergeHighlighting(el, coloredText)


def mergeColors(coloredText: t.Deque[ColoredText]) -> t.Deque[ColoredText]:
    """
    Some highlighters gratuitously emit multiple tokens in a row with the same color,
    which makes other modifications I perform annoying.
    This does a pass to merge those together.
    """
    ret: t.Deque[ColoredText] = collections.deque()
    for token in coloredText:
        if token.text == "":
            # Drop empty tokens
            continue
        if ret and ret[-1].color == token.color:
            ret[-1].text += token.text
        else:
            ret.append(token)
    return ret


def readdWhitespacePrefix(rawText: str, coloredText: t.Deque[ColoredText]) -> t.Deque[ColoredText]:
    """
    If the raw text starts with whitespace, Pygments auto-strips it >:(
    So, we need to add it back in, as an uncolored chunk of text.
    But also, it doesn't... always strip whitespace. So check for that.
    """
    if not coloredText:
        # Empty colored text, nothing to do
        return coloredText
    coloredMatch = re.match(r"\s+", coloredText[0].text)
    if coloredMatch:
        # whitespace was kept by the formatter, so nothing to do
        return coloredText
    textMatch = re.match(r"\s+", rawText)
    if not textMatch:
        # No whitespace on the text, nothing to do
        return coloredText
    prefix = ColoredText(textMatch[0], None)
    coloredText.appendleft(prefix)
    return coloredText


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
    rawTokens = [(str(ttype), val) for (ttype, val) in pygments.lex(text, lexer)]
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
        nodes: list[t.Node] = []
        while text and coloredText:
            nextColor = coloredText.popleft()
            if len(nextColor.text) <= len(text):
                # Use the entire nextColor node, only part of text
                if nextColor.color is None:
                    nodes.append(nextColor.text)
                else:
                    nodes.append(createEl(nextColor.color, nextColor.text))
                text = text[len(nextColor.text) :]
            else:
                # Use all of text, only part of the nextColor node
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


def coloredTextFromRawTokens(rawTokens: t.Sequence[tuple[str, str]]) -> t.Deque[ColoredText]:
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
    for tokenName, text in rawTokens:
        if not text:
            continue
        color = colorFromName.get(tokenName)
        addCtToList(textList, ColoredText(text, color))
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
        return customLexers[lang](encoding="utf-8", stripnl=False)
    try:
        return get_lexer_by_name(lang, encoding="utf-8", stripnl=False)
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

    # Split text nodes on newlines, grouping elements and text between
    # each linebreak into a line array.
    lines: list[list[t.Node]] = [[]]
    for node in dom.children(el):
        if dom.isElement(node):
            lines[-1].append(node)
        else:
            while "\n" in node:
                pre, _, node = node.partition("\n")
                dom.appendText(lines[-1], pre)
                lines.append([])
            dom.appendText(lines[-1], node)

    # Clear el so we can fill it with line numbers instead.
    el = dom.withoutChildren(el)

    # Fill el with new elements, and add attrs for line-numbering as appropraite
    lineNumber = start
    for line in lines:
        lineNo = dom.E.span({"class": "line-no"})
        lineWrapper = dom.E.span({"class": "line"}, *line)
        dom.appendChild(el, lineNo, lineWrapper)
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
