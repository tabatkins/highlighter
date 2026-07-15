from __future__ import annotations

import pytest

import highlighter

def test_markup():
	text = """
<!doctype html>
<title>foo <s>bar</s></title>
<meta charset=utf-8>
<body>
<ul>
	<li>I'm a list item
	<li>Two
</ul>
"""
	html,css = highlighter.highlight(["pre", {}, text], lang="markup")
	print(html)