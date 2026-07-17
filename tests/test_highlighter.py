from __future__ import annotations

import json

import pytest

import highlighter


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


def format(data: list | str) -> str:
    if isinstance(data, str):
        data = json.loads(data)
    ret = json.dumps(data, indent=2, sort_keys=True)
    return ret
