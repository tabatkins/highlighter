# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
import collections
from . import lexers
from .widlparser.widlparser import parser
from .pygments import pygments as pyg
from .pygments.pygments.lexers import get_lexer_by_name
from .pygments.pygments import formatters

customLexers = {
    "css": lexers.CSSLexer()
}

ColoredText = collections.namedtuple('ColoredText', ['text', 'color'])

def die(msg, *rargs, **kwargs):
    raise Exception(msg.format(*rargs, **kwargs))

def highlight(html, lang=None, lineNumbers=False, lineStart=1, lineHighlights=set()):
    styles = ""
    # Find whether to highlight, and what the lang is
    lang = determineHighlightLang(doc, el)
    if lang:
        html = highlightEl(html, lang)
        styles += highlightStyles
    # Find whether to add line numbers
    if lineNumbers or lineHighlights:
        html = addLineWrappers(html, numbers=lineNumbers, start=lineStart, highlights=lineHighlights)
        if lineNumbers:
            styles += lineNumberStyles
        if lineHighlights:
            if isinstance(lineHighlights, basestring):
                lineHighlights = parseHighlightString(lineHighlights)
            styles += lineHighlightingStyles
    return html, styles


def parseHighlightString(text):
    lineHighlights = set()
    text = re.sub(r"\s*", "", text)
    for item in text.split(","):
        if "-" in item:
            # Range, format of DDD-DDD
            low,_,high = item.partition("-")
            try:
                low = int(low)
                high = int(high)
            except ValueError:
                die("Error parsing line-highlight range '{0}' - must be `int-int`.", item)
            if low >= high:
                die("line-highlight ranges must be well-formed lo-hi - got '{0}'.", item)
            lineHighlights.update(range(low, high+1))
        else:
            try:
                item = int(item)
            except ValueError:
                die("Error parsing line-highlight value '{0}' - must be integers.", item)
            lineHighlights.add(item)

    return lineHighlights


def highlightEl(el, lang):
    text = textContent(el)
    if lang == "webidl":
        coloredText = highlightWithWebIDL(text)
    else:
        coloredText = highlightWithPygments(text, lang)
    return mergeHighlighting(el, coloredText)


def textContent(el):
    def textIterator(el):
        for item in children(el):
            if isinstance(item, basestring):
                yield item
            else:
                for ret in textIterator(item):
                    yield item
    return "".join(textIterator(el))


def highlightWithWebIDL(text, el):
    '''
    Trick the widlparser emitter,
    which wants to output HTML via wrapping with start/end tags,
    into instead outputting a stack-based text format.
    A \1 indicates a new stack push;
    the text between the \1 and the \2 is the class to be pushed.
    A \3 indicates a stack pop.
    All other text is colored with the class currently on top of the stack.
    '''
    class IDLUI(object):
        def warn(self, msg):
            die("{0}", msg.rstrip())
    class HighlightMarker(object):
        # Just applies highlighting classes to IDL stuff.
        def markupTypeName(self, text, construct):
            return ('\1n\2', '\3')
        def markupName(self, text, construct):
            return ('\1nv\2', '\3')
        def markupKeyword(self, text, construct):
            return ('\1kt\2', '\3')
        def markupEnumValue(self, text, construct):
            return ('\1s\2', '\3')

    widl = parser.Parser(text, IDLUI())
    return parseWidlIntoCT(unicode(widl.markup(HighlightMarker())))

def parseWidlIntoCT(widlText):
    coloredTexts = collections.deque()
    colors = []
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


def highlightWithPygments(text, lang, el):
    lexer = lexerFromLang(lang)
    if lexer is None:
        die("'{0}' isn't a known syntax-highlighting language. See http://pygments.org/docs/lexers/.", lang)
    rawTokens = pyg.highlight(text, lexer, formatters.RawTokenFormatter())
    coloredText = coloredTextFromRawTokens(rawTokens)
    return coloredText


def mergeHighlighting(el, coloredText):
    # Merges a tree of Pygment-highlighted HTML
    # into the original element's markup.
    # This works because Pygment effectively colors each character with a highlight class,
    # merging them together into runs of text for convenience/efficiency only;
    # the markup structure is a flat list of sibling elements containing raw text
    # (and maybe some un-highlighted raw text between them).
    def createEl(color, text):
        return ["span", {"class":color}, text]

    def colorizeEl(el, coloredText):
        elChildren = children(el)
        el = clearChildren(el)
        for node in elChildren:
            if isElement(node):
                appendChild(el, colorizeEl(node, coloredText))
            else:
                appendChild(el, *colorizeText(node, coloredText))
        return el

    def colorizeText(text, coloredText):
        nodes = []
        while text and coloredText:
            nextColor = coloredText.popleft()
            if len(nextColor.text) <= len(text):
                if nextColor.color is None:
                    nodes.append(nextColor.text)
                else:
                    nodes.append(createEl(nextColor.color, nextColor.text))
                text = text[len(nextColor.text):]
            else:  # Need to use only part of the nextColor node
                if nextColor.color is None:
                    nodes.append(text)
                else:
                    nodes.append(createEl(nextColor.color, text))
                # Truncate the nextColor text to what's unconsumed,
                # and put it back into the deque
                nextColor = ColoredText(nextColor.text[len(text):], nextColor.color)
                coloredText.appendleft(nextColor)
                text = ''
        return nodes
    return colorizeEl(el, coloredText)

def isElement(node):
    return isinstance(node, list)

def hasChildElements(node):
    return any(isElement(x) for x in node[2:])

def children(node, clear=False):
    if isElement(node):
        return node[2:]
    else:
        return []

def clearChilden(node):
    if isElement(node):
        return node[:2]
    else:
        return node

def attrs(node):
    if isElement(node):
        return node[1]
    else:
        return {}

def addClass(node, cls):
    a = attrs(node)
    if "class" in attrs:
        attrs["class"] += " " + cls
    else:
        attrs["class"] = cls
    return node

def appendChild(node, *children):
    node.extend(children)
    return node

def isEmpty(node):
    return len(node) == 2

def coloredTextFromRawTokens(text):
    colorFromName = {
        "Token.Comment": "c",
        "Token.Keyword": "k",
        "Token.Literal": "l",
        "Token.Name": "n",
        "Token.Operator": "o",
        "Token.Punctuation": "p",
        "Token.Comment.Multiline": "cm",
        "Token.Comment.Preproc": "cp",
        "Token.Comment.Single": "c1",
        "Token.Comment.Special": "cs",
        "Token.Keyword.Constant": "kc",
        "Token.Keyword.Declaration": "kd",
        "Token.Keyword.Namespace": "kn",
        "Token.Keyword.Pseudo": "kp",
        "Token.Keyword.Reserved": "kr",
        "Token.Keyword.Type": "kt",
        "Token.Literal.Date": "ld",
        "Token.Literal.Number": "m",
        "Token.Literal.String": "s",
        "Token.Name.Attribute": "na",
        "Token.Name.Class": "nc",
        "Token.Name.Constant": "no",
        "Token.Name.Decorator": "nd",
        "Token.Name.Entity": "ni",
        "Token.Name.Exception": "ne",
        "Token.Name.Function": "nf",
        "Token.Name.Label": "nl",
        "Token.Name.Namespace": "nn",
        "Token.Name.Property": "py",
        "Token.Name.Tag": "nt",
        "Token.Name.Variable": "nv",
        "Token.Operator.Word": "ow",
        "Token.Literal.Number.Bin": "mb",
        "Token.Literal.Number.Float": "mf",
        "Token.Literal.Number.Hex": "mh",
        "Token.Literal.Number.Integer": "mi",
        "Token.Literal.Number.Oct": "mo",
        "Token.Literal.String.Backtick": "sb",
        "Token.Literal.String.Char": "sc",
        "Token.Literal.String.Doc": "sd",
        "Token.Literal.String.Double": "s2",
        "Token.Literal.String.Escape": "se",
        "Token.Literal.String.Heredoc": "sh",
        "Token.Literal.String.Interpol": "si",
        "Token.Literal.String.Other": "sx",
        "Token.Literal.String.Regex": "sr",
        "Token.Literal.String.Single": "s1",
        "Token.Literal.String.Symbol": "ss",
        "Token.Name.Variable.Class": "vc",
        "Token.Name.Variable.Global": "vg",
        "Token.Name.Variable.Instance": "vi",
        "Token.Literal.Number.Integer.Long": "il"
    }
    def addCtToList(list, ct):
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
    textList = collections.deque()
    currentCT = None
    for line in text.split("\n"):
        if not line:
            continue
        tokenName,_,tokenTextRepr = line.partition("\t")
        color = colorFromName.get(tokenName, None)
        text = eval(tokenTextRepr)
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


def normalizeLanguageName(lang):
    # Translates some names to ones Pygment understands
    if lang == "aspnet":
        return "aspx-cs"
    if lang in ["markup", "svg"]:
        return "html"
    if lang == "idl":
        return "webidl"
    return lang


def lexerFromLang(lang):
    if lang in customLexers:
        return customLexers[lang]
    try:
        return get_lexer_by_name(lang, encoding="utf-8", stripAll=True)
    except pyg.util.ClassNotFound:
        return None


def addLineWrappers(el, numbers=True, start=1, highlights=None):
    # Wrap everything between each top-level newline with a line tag.
    # Add an attr for the line number, and if needed, the end line.
    if highlights is None:
        highlights = set()
    lineWrapper = ["div", {"class": "line"}]
    elChildren = children(el)
    el = clearChildren(el)
    for node in elChildren:
        if isElement(node):
            appendChild(lineWrapper, node)
        else:
            while True:
                if "\n" in node:
                    pre, _, post = node.partition("\n")
                    appendChild(lineWrapper, pre)
                    appendChild(el, lineWrapper)
                    lineWrapper = ["div", {"class": "line"}]
                    node = post
                else:
                    appendChild(lineWrapper, node)
                    break
    if len(lineWrapper):
        appendChild(el, lineWrapper)
    # Number the lines
    lineNumber = start
    for node in children(el):
        if isElement(node):
            if isEmpty(node):
                # Blank line; since I removed the \n from the source
                # and am relying on <div> for lines now,
                # this'll collapse to zero-height and mess things up.
                # Add a single space to keep it one line tall.
                appendChild(node, " ")
            if numbers:
                attrs(node).set("line", unicode(lineNumber))
            if lineNumber in highlights:
                attrs(node).set("line", unicode(lineNumber))
                addClass(node, "highlight-line")
            internalNewlines = countInternalNewlines(node)
            if internalNewlines:
                for i in range(1, internalNewlines+1):
                    if (lineNumber + i) in highlights:
                        addClass(node, "highlight-line")
                        attrs(node).set("line", unicode(lineNumber))
                lineNumber += internalNewlines
                if numbers:
                    attrs(node).set("line-end", unicode(lineNumber))
            lineNumber += 1
    return el

def countInternalNewlines(el):
    count = 0
    for node in children(el):
        if isElement(node):
            count += countInternalNewlines(node)
        else:
            count += node.count("\n")
    return count


# To regen the styles, edit and run the below
#from pygments import token
#from pygments import style
#class PrismStyle(style.Style):
#    default_style = "#000000"
#    styles = {
#        token.Name: "#0077aa",
#        token.Name.Tag: "#669900",
#        token.Name.Builtin: "noinherit",
#        token.Name.Variable: "#222222",
#        token.Name.Other: "noinherit",
#        token.Operator: "#999999",
#        token.Punctuation: "#999999",
#        token.Keyword: "#990055",
#        token.Literal: "#000000",
#        token.Literal.Number: "#000000",
#        token.Literal.String: "#a67f59",
#        token.Comment: "#708090"
#    }
#print formatters.HtmlFormatter(style=PrismStyle).get_style_defs('.highlight')
highlightStyles = '''
.highlight:not(.idl) { background: hsl(24, 20%, 95%); }
code.highlight { padding: .1em; border-radius: .3em; }
pre.highlight, pre > code.highlight { display: block; padding: 1em; margin: .5em 0; overflow: auto; border-radius: 0; }
.highlight .c { color: #708090 } /* Comment */
.highlight .k { color: #990055 } /* Keyword */
.highlight .l { color: #000000 } /* Literal */
.highlight .n { color: #0077aa } /* Name */
.highlight .o { color: #999999 } /* Operator */
.highlight .p { color: #999999 } /* Punctuation */
.highlight .cm { color: #708090 } /* Comment.Multiline */
.highlight .cp { color: #708090 } /* Comment.Preproc */
.highlight .c1 { color: #708090 } /* Comment.Single */
.highlight .cs { color: #708090 } /* Comment.Special */
.highlight .kc { color: #990055 } /* Keyword.Constant */
.highlight .kd { color: #990055 } /* Keyword.Declaration */
.highlight .kn { color: #990055 } /* Keyword.Namespace */
.highlight .kp { color: #990055 } /* Keyword.Pseudo */
.highlight .kr { color: #990055 } /* Keyword.Reserved */
.highlight .kt { color: #990055 } /* Keyword.Type */
.highlight .ld { color: #000000 } /* Literal.Date */
.highlight .m { color: #000000 } /* Literal.Number */
.highlight .s { color: #a67f59 } /* Literal.String */
.highlight .na { color: #0077aa } /* Name.Attribute */
.highlight .nc { color: #0077aa } /* Name.Class */
.highlight .no { color: #0077aa } /* Name.Constant */
.highlight .nd { color: #0077aa } /* Name.Decorator */
.highlight .ni { color: #0077aa } /* Name.Entity */
.highlight .ne { color: #0077aa } /* Name.Exception */
.highlight .nf { color: #0077aa } /* Name.Function */
.highlight .nl { color: #0077aa } /* Name.Label */
.highlight .nn { color: #0077aa } /* Name.Namespace */
.highlight .py { color: #0077aa } /* Name.Property */
.highlight .nt { color: #669900 } /* Name.Tag */
.highlight .nv { color: #222222 } /* Name.Variable */
.highlight .ow { color: #999999 } /* Operator.Word */
.highlight .mb { color: #000000 } /* Literal.Number.Bin */
.highlight .mf { color: #000000 } /* Literal.Number.Float */
.highlight .mh { color: #000000 } /* Literal.Number.Hex */
.highlight .mi { color: #000000 } /* Literal.Number.Integer */
.highlight .mo { color: #000000 } /* Literal.Number.Oct */
.highlight .sb { color: #a67f59 } /* Literal.String.Backtick */
.highlight .sc { color: #a67f59 } /* Literal.String.Char */
.highlight .sd { color: #a67f59 } /* Literal.String.Doc */
.highlight .s2 { color: #a67f59 } /* Literal.String.Double */
.highlight .se { color: #a67f59 } /* Literal.String.Escape */
.highlight .sh { color: #a67f59 } /* Literal.String.Heredoc */
.highlight .si { color: #a67f59 } /* Literal.String.Interpol */
.highlight .sx { color: #a67f59 } /* Literal.String.Other */
.highlight .sr { color: #a67f59 } /* Literal.String.Regex */
.highlight .s1 { color: #a67f59 } /* Literal.String.Single */
.highlight .ss { color: #a67f59 } /* Literal.String.Symbol */
.highlight .vc { color: #0077aa } /* Name.Variable.Class */
.highlight .vg { color: #0077aa } /* Name.Variable.Global */
.highlight .vi { color: #0077aa } /* Name.Variable.Instance */
.highlight .il { color: #000000 } /* Literal.Number.Integer.Long */
'''

lineNumberStyles = '''
.line {
    padding-left: 1.4em;
    position: relative;
}
.line:hover {
    background: rgba(0,0,0,.05);
}
.line[line]::before {
    content: attr(line);
    position: absolute;
    top: 0;
    left: 1px;
    color: gray;
}
.line[line-end]::after {
    content: attr(line-end);
    position: absolute;
    bottom: 0;
    left: 1px;
    color: gray;
}
'''

lineHighlightingStyles = '''
.line {
    padding-left: 1.4em;
    position: relative;
}
.line.highlight-line {
    background: rgba(0,0,0,.05);
}
.line.highlight-line[line]::before {
    content: attr(line);
    position: absolute;
    top: 0;
    left: 1px;
    color: gray;
}
.line.highlight-line[line-end]::after {
    content: attr(line-end);
    position: absolute;
    bottom: 0;
    left: 1px;
    color: gray;
}
'''
