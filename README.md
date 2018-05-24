Highlighter
===========

This project extracts and abstracts [Bikeshed's](https://www.github.com/tabatkins/bikeshed) syntax-highlighting functionality for usage by other tools.

To use, clone this git repo into your project folder,
and then:

```python
import highlighter
html,css = highlighter.highlight(elementGoesHere, lang="whatever")
```

-----

The `elementGoesHere` argument needs to be a chunk of HTML,
converted into JSON using the following transformation:

```
<p class=foo>text<span>nested text</span></p>
=> becomes =>
["p", {"class":"foo"}, "text", ["span", {}, "nested text"]]
```

That is, each element is encoded as an array,
with the first item being the tagname,
the second being an object containing the attributes,
and the remaining items being the children of the element,
either straight text or further nested elements.

It's generally assumed that the root element will be a `["pre"]`,
but that's not strictly necessary;
the default styling uses CSS Grid,
and doesn't depend on newlines being preserved.

-----

The supported languages are [everything that Pygments supports](http://pygments.org/languages/),
plus "webidl" for WebIDL.

-----

The return value is a 2-tuple `(html, css)`:
`html` is the highlighted HTML
(also formatted as JSON);
`css` is the accompanying CSS that supports the highlighting,
which you can use or replace as you wish.

Alternately, if you pass `output=html` to the `highlight()` function,
the `html` return value will be a string containing HTML,
rather than JSON.

Line Numbers or Highlights
--------------------------

You can also add line numbers to the outputted HTML,
or highlight specific lines.

To add line numbers,
pass `lineNumbers=True` to `highlight()`.
By default the numbers start at 1;
to change that, pass `lineStart=5` or whatever you need.

To highlight *specific* lines,
pass `lineHighlights=...`,
where the `...` is either a `set()` containing the line numbers you want highlighted,
or a comma-separated string containing line numbers and/or ranges, like `1, 3-5`
(equivalent to `set(1, 3, 4, 5)`).
Again, it defaults to assuming the first line is line 1,
and you can change this by passing `lineStart`.

The two options can be combined for both numbering and highlighting.