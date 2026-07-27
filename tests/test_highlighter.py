from __future__ import annotations

import json

import pytest

import highlighter


def format(data: list | str) -> str:
    if isinstance(data, str):
        data = json.loads(data)
    ret = json.dumps(data, indent=2, sort_keys=True)
    return ret


def test_css():
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
    assert format(html) == format(expected)


def test_css_multiline():
    src = """
	.foo {
		bar: baz;
	}
	"""
    html, _ = highlighter.highlight(["pre", {}, src], lang="css")
    expected = [
        "pre",
        {},
        "\t",
        ["c-", {"f": ""}, ".foo "],
        ["c-", {"p": ""}, "{"],
        "\n",
        "\t\t",
        ["c-", {"k": ""}, "bar"],
        ["c-", {"p": ""}, ":"],
        " baz",
        ["c-", {"p": ""}, ";"],
        "\n",
        "\t",
        ["c-", {"p": ""}, "}"],
        "\n",
        "\t",
        "\n",
    ]
    assert format(html) == format(expected)


def test_html():
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
        "\t",
        ["c-", {"cp": ""}, "<!doctype html>"],
        "\n",
        "\t",
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
        "\n",
        "\t",
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
        "\n",
        "\t",
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
        "\n",
        "\t",
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
        "\n",
        "\t",
        "\n",
    ]
    assert format(html) == format(expected)


def test_css_line_numbers():
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
        ["span", {"class": "line"}, "    ", ["c-", {"f": ""}, ".foo "], ["c-", {"p": ""}, "{"], ""],
        ["span", {"class": "line-no", "data-line": "2"}],
        [
            "span",
            {"class": "line"},
            "",
            "        ",
            ["c-", {"k": ""}, "bar"],
            ["c-", {"p": ""}, ":"],
            " baz",
            ["c-", {"p": ""}, ";"],
            "",
        ],
        ["span", {"class": "line-no", "data-line": "3"}],
        ["span", {"class": "line"}, "", "    ", ["c-", {"p": ""}, "}"], ""],
        ["span", {"class": "line-no", "data-line": "4"}],
        ["span", {"class": "line"}, "", "    ", ""],
        ["span", {"class": "line-no", "data-line": "5"}],
        ["span", {"class": "line"}, ""],
    ]
    assert format(html) == format(expected)


def test_css_line_start():
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
        ["span", {"class": "line"}, "    ", ["c-", {"f": ""}, ".foo "], ["c-", {"p": ""}, "{"], ""],
        ["span", {"class": "line-no", "data-line": "6"}],
        [
            "span",
            {"class": "line"},
            "",
            "        ",
            ["c-", {"k": ""}, "bar"],
            ["c-", {"p": ""}, ":"],
            " baz",
            ["c-", {"p": ""}, ";"],
            "",
        ],
        ["span", {"class": "line-no", "data-line": "7"}],
        ["span", {"class": "line"}, "", "    ", ["c-", {"p": ""}, "}"], ""],
        ["span", {"class": "line-no", "data-line": "8"}],
        ["span", {"class": "line"}, "", "    ", ""],
        ["span", {"class": "line-no", "data-line": "9"}],
        ["span", {"class": "line"}, ""],
    ]
    assert format(html) == format(expected)


def test_css_line_highlight():
    src = """
    .foo {
        bar: baz;
    }
    """
    html, _ = highlighter.highlight(["pre", {}, src], lang="css", lineHighlights="2,3")
    expected = [
        "pre",
        {"class": "line-numbered"},
        ["span", {"class": "line-no"}],
        ["span", {"class": "line"}, "    ", ["c-", {"f": ""}, ".foo "], ["c-", {"p": ""}, "{"], ""],
        ["span", {"class": "line-no highlight-line", "data-line": "2"}],
        [
            "span",
            {"class": "line highlight-line"},
            "",
            "        ",
            ["c-", {"k": ""}, "bar"],
            ["c-", {"p": ""}, ":"],
            " baz",
            ["c-", {"p": ""}, ";"],
            "",
        ],
        ["span", {"class": "line-no highlight-line", "data-line": "3"}],
        ["span", {"class": "line highlight-line"}, "", "    ", ["c-", {"p": ""}, "}"], ""],
        ["span", {"class": "line-no"}],
        ["span", {"class": "line"}, "", "    ", ""],
        ["span", {"class": "line-no"}],
        ["span", {"class": "line"}, ""],
    ]

    assert format(html) == format(expected)


if __name__ == "__main__":
    pass

