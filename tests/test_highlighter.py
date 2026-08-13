from __future__ import annotations

import json
import typing

import deepdiff
import pytest

import highlighter

if typing.TYPE_CHECKING:
    from typing import Any

    type JSONValue = dict[str, Any] | list[Any] | str | int | float | bool | None
    type Element = list[str | dict[str, str] | Node]
    type Node = Element | str


def format(data: JSONValue) -> str:
    if isinstance(data, str):
        data = json.loads(data)
    ret = json.dumps(data, indent=2, sort_keys=True)
    return ret


def compare(expected: JSONValue, actual: JSONValue) -> deepdiff.DeepDiff | None:
    return deepdiff.DeepDiff(expected, actual, view=deepdiff.helper.COLORED_COMPACT_VIEW)


def test_css() -> None:
    src = """.foo { bar: baz; }"""
    html, _ = highlighter.highlight(["pre", {}, src], lang="css")
    expected = [
        "pre",
        {},
        ["c-", {"f": ""}, ".foo "],
        ["c-", {"p": ""}, "{"],
        " ",
        ["c-", {"k": ""}, "bar"],
        ["c-", {"p": ""}, ":"],
        " baz",
        ["c-", {"p": ""}, ";"],
        " ",
        ["c-", {"p": ""}, "}"],
    ]
    diff = compare(expected, html)
    assert not diff, str(diff)


def test_css_multiline() -> None:
    src = """
	.foo {
		bar: baz;
	}
	"""
    html, _ = highlighter.highlight(["pre", {}, src], lang="css")
    expected = [
        "pre",
        {},
        "\n\t",
        ["c-", {"f": ""}, ".foo "],
        ["c-", {"p": ""}, "{"],
        "\n\t\t",
        ["c-", {"k": ""}, "bar"],
        ["c-", {"p": ""}, ":"],
        " baz",
        ["c-", {"p": ""}, ";"],
        "\n\t",
        ["c-", {"p": ""}, "}"],
        "\n\t",
    ]
    diff = compare(expected, html)
    assert not diff, str(diff)


def test_html() -> None:
    src = """
	<!doctype html>
	<title>foo <s>&lt;></title>
	<style>.foo { bar: baz; }</style>
	<script>function foo() { return "<p class='foo bar'>"; }</script>
	<p class="foo bar" style='content: "<p ">foo <i>bar</i>
	"""
    html, _ = highlighter.highlight(["pre", {}, src], lang="html")
    expected = [
        "pre",
        {},
        "\n\t",
        ["c-", {"cp": ""}, "<!doctype html>"],
        "\n\t",
        ["c-", {"p": ""}, "<"],
        ["c-", {"f": ""}, "title"],
        ["c-", {"p": ""}, ">"],
        "foo ",
        ["c-", {"p": ""}, "<"],
        ["c-", {"f": ""}, "s"],
        ["c-", {"p": ""}, ">"],
        ["c-", {"ni": ""}, "&lt;"],
        ">",
        ["c-", {"p": ""}, "</"],
        ["c-", {"f": ""}, "title"],
        ["c-", {"p": ""}, ">"],
        "\n\t",
        ["c-", {"p": ""}, "<"],
        ["c-", {"f": ""}, "style"],
        ["c-", {"p": ""}, ">."],
        ["c-", {"nc": ""}, "foo"],
        " ",
        ["c-", {"p": ""}, "{"],
        " ",
        ["c-", {"n": ""}, "bar"],
        ["c-", {"p": ""}, ":"],
        " ",
        ["c-", {"n": ""}, "baz"],
        ["c-", {"p": ""}, ";"],
        " ",
        ["c-", {"p": ""}, "}</"],
        ["c-", {"f": ""}, "style"],
        ["c-", {"p": ""}, ">"],
        "\n\t",
        ["c-", {"p": ""}, "<"],
        ["c-", {"f": ""}, "script"],
        ["c-", {"p": ""}, ">"],
        ["c-", {"a": ""}, "function"],
        " foo",
        ["c-", {"p": ""}, "()"],
        " ",
        ["c-", {"p": ""}, "{"],
        " ",
        ["c-", {"k": ""}, "return"],
        " ",
        ["c-", {"u": ""}, "\"<p class='foo bar'>\""],
        ["c-", {"p": ""}, ";"],
        " ",
        ["c-", {"p": ""}, "}</"],
        ["c-", {"f": ""}, "script"],
        ["c-", {"p": ""}, ">"],
        "\n\t",
        ["c-", {"p": ""}, "<"],
        ["c-", {"f": ""}, "p"],
        " ",
        ["c-", {"e": ""}, "class"],
        ["c-", {"o": ""}, "="],
        ["c-", {"s": ""}, '"foo bar"'],
        " ",
        ["c-", {"e": ""}, "style"],
        ["c-", {"o": ""}, "="],
        ["c-", {"s": ""}, "'content:"],
        ' "<',
        ["c-", {"e": ""}, "p"],
        ' "',
        ["c-", {"p": ""}, ">"],
        "foo ",
        ["c-", {"p": ""}, "<"],
        ["c-", {"f": ""}, "i"],
        ["c-", {"p": ""}, ">"],
        "bar",
        ["c-", {"p": ""}, "</"],
        ["c-", {"f": ""}, "i"],
        ["c-", {"p": ""}, ">"],
        "\n\t",
    ]
    diff = compare(expected, html)
    assert not diff, str(diff)


def test_css_line_numbers() -> None:
    src = """
    .foo {
        bar: baz;
    }
    """
    html, _ = highlighter.highlight(["pre", {}, src], lang="css", lineNumbers=True)
    expected = [
        "pre",
        {"class": "line-numbered"},
        ["span", {"class": "line-no", "data-line": "1"}],
        ["span", {"class": "line"}],
        ["span", {"class": "line-no", "data-line": "2"}],
        ["span", {"class": "line"}, "    ", ["c-", {"f": ""}, ".foo "], ["c-", {"p": ""}, "{"]],
        ["span", {"class": "line-no", "data-line": "3"}],
        [
            "span",
            {"class": "line"},
            "        ",
            ["c-", {"k": ""}, "bar"],
            ["c-", {"p": ""}, ":"],
            " baz",
            ["c-", {"p": ""}, ";"],
        ],
        ["span", {"class": "line-no", "data-line": "4"}],
        ["span", {"class": "line"}, "    ", ["c-", {"p": ""}, "}"]],
        ["span", {"class": "line-no", "data-line": "5"}],
        ["span", {"class": "line"}, "    "],
    ]

    diff = compare(expected, html)
    assert not diff, str(diff)


def test_css_line_start() -> None:
    src = """
    .foo {
        bar: baz;
    }
    """
    html, _ = highlighter.highlight(["pre", {}, src], lang="css", lineNumbers=True, lineStart=5)
    expected = [
        "pre",
        {"class": "line-numbered"},
        ["span", {"class": "line-no", "data-line": "5"}],
        ["span", {"class": "line"}],
        ["span", {"class": "line-no", "data-line": "6"}],
        ["span", {"class": "line"}, "    ", ["c-", {"f": ""}, ".foo "], ["c-", {"p": ""}, "{"]],
        ["span", {"class": "line-no", "data-line": "7"}],
        [
            "span",
            {"class": "line"},
            "        ",
            ["c-", {"k": ""}, "bar"],
            ["c-", {"p": ""}, ":"],
            " baz",
            ["c-", {"p": ""}, ";"],
        ],
        ["span", {"class": "line-no", "data-line": "8"}],
        ["span", {"class": "line"}, "    ", ["c-", {"p": ""}, "}"]],
        ["span", {"class": "line-no", "data-line": "9"}],
        ["span", {"class": "line"}, "    "],
    ]
    diff = compare(expected, html)
    assert not diff, str(diff)


def test_css_line_highlight() -> None:
    src = """
    .foo {
        bar: baz;
    }
    """
    html, _ = highlighter.highlight(["pre", {}, src], lang="css", lineHighlights="3,4")
    expected = [
        "pre",
        {"class": "line-numbered"},
        ["span", {"class": "line-no"}],
        ["span", {"class": "line"}],
        ["span", {"class": "line-no"}],
        ["span", {"class": "line"}, "    ", ["c-", {"f": ""}, ".foo "], ["c-", {"p": ""}, "{"]],
        ["span", {"class": "line-no highlight-line", "data-line": "3"}],
        [
            "span",
            {"class": "line highlight-line"},
            "        ",
            ["c-", {"k": ""}, "bar"],
            ["c-", {"p": ""}, ":"],
            " baz",
            ["c-", {"p": ""}, ";"],
        ],
        ["span", {"class": "line-no highlight-line", "data-line": "4"}],
        ["span", {"class": "line highlight-line"}, "    ", ["c-", {"p": ""}, "}"]],
        ["span", {"class": "line-no"}],
        ["span", {"class": "line"}, "    "],
    ]

    diff = compare(expected, html)
    assert not diff, str(diff)


def test_css_markup() -> None:
    src: list[Node] = [
        """
    .foo {
        bar: """,
        ["b", {}, "baz"],
        """;
    }
    """,
    ]
    html, _ = highlighter.highlight(["pre", {}, *src], lang="css")
    expected = [
        "pre",
        {},
        "\n    ",
        ["c-", {"f": ""}, ".foo "],
        ["c-", {"p": ""}, "{"],
        "\n        ",
        ["c-", {"k": ""}, "bar"],
        ["c-", {"p": ""}, ":"],
        " ",
        ["b", {}, "baz"],
        ["c-", {"p": ""}, ";"],
        "\n    ",
        ["c-", {"p": ""}, "}"],
        "\n    ",
    ]

    diff = compare(expected, html)
    assert not diff, str(diff)


def test_css_markup_crossing_lines() -> None:
    src: list[Node] = [
        """
    .foo {
        bar: """,
        ["b", {}, "baz;\n  qux:"],
        """ foo2;
    }
    """,
    ]
    html, _ = highlighter.highlight(["pre", {}, *src], lang="css")
    expected = [
        "pre",
        {},
        "\n    ",
        ["c-", {"f": ""}, ".foo "],
        ["c-", {"p": ""}, "{"],
        "\n        ",
        ["c-", {"k": ""}, "bar"],
        ["c-", {"p": ""}, ":"],
        " ",
        [
            "b",
            {},
            "baz",
            ["c-", {"p": ""}, ";"],
            "\n  ",
            ["c-", {"k": ""}, "qux"],
            ["c-", {"p": ""}, ":"],
        ],
        " foo2",
        ["c-", {"p": ""}, ";"],
        "\n    ",
        ["c-", {"p": ""}, "}"],
        "\n    ",
    ]

    diff = compare(expected, html)
    assert not diff, str(diff)


def test_webidl() -> None:
    src = ["""
    interface Foo {
      undefined bar(DOMString baz, optional long qux);
    };
    """]
    html, _ = highlighter.highlight(["pre", {}, *src], lang="webidl")
    expected = [
        "pre",
        {},
        "\n    ",
        ["c-", {"b": ""}, "interface"],
        " ",
        ["c-", {"g": ""}, "Foo"],
        " {\n      ",
        ["c-", {"b": ""}, "undefined"],
        " ",
        ["c-", {"g": ""}, "bar"],
        "(",
        ["c-", {"b": ""}, "DOMString"],
        " ",
        ["c-", {"g": ""}, "baz"],
        ", ",
        ["c-", {"b": ""}, "optional"],
        " ",
        ["c-", {"b": ""}, "long"],
        " ",
        ["c-", {"g": ""}, "qux"],
        ");\n    };\n    ",
    ]

    diff = compare(expected, html)
    assert not diff, str(diff)


def test_unescape() -> None:
    src = ["""interface Foo { Promise&lt;undefined> foo(); };"""]
    html, _ = highlighter.highlight(["pre", {}, *src], lang="webidl", unescape=True)
    expected = [
        "pre",
        {},
        ["c-", {"b": ""}, "interface"],
        " ",
        ["c-", {"g": ""}, "Foo"],
        " { ",
        ["c-", {"b": ""}, "Promise"],
        "<",
        ["c-", {"b": ""}, "undefined"],
        "> ",
        ["c-", {"g": ""}, "foo"],
        "(); };",
    ]

    diff = compare(expected, html)
    assert not diff, str(diff)


def test_needs_unescape() -> None:
    src = ["""interface Foo { Promise&lt;undefined> foo(); };"""]
    try:
        html, _ = highlighter.highlight(["pre", {}, *src], lang="webidl")
        assert False, "Without unescape, the IDL highlighter should choke."
    except SyntaxWarning:
        assert True, "Without unescape, the IDL highlighter should choke."


if __name__ == "__main__":
    pass
    src = ["""interface Foo { Promise&lt;undefined> foo(); };"""]
    html, _ = highlighter.highlight(["pre", {}, *src], lang="webidl", unescape=True)
    print(repr(html))
