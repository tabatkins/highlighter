Highlighter
===========

**(Important, see the note at the end about Pygments, or else this project won't work.)**

This project extracts and abstracts [Bikeshed's](https://www.github.com/tabatkins/bikeshed) syntax-highlighting functionality for usage by other tools.

To use, clone this git repo into your project folder,
and then:

```python
import highlighter
html,css = highlighter.highlight(elementGoesHere, lang="whatever")
```

Alternately, you can invoke it directly from the command line,
passing it a string of JSON on stdin,
and it will output via stdout:

```bash
echo '["pre", {}, "interface Foo {};"]' | ./__init__.py webidl
```

When invoked this way,
it will return a string containing a JSON object with `html` and `css` keys:
the `html` value will be the marked-up HTML, still in JSON form;
the `css` value will be a string containing CSS.

(Run `highlighter/__init__.py -h` to see all the command-line options.)

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
the second being an object containing the attributes
(if no attributes, an empty object is still required),
and the remaining items being the children of the element,
either straight text or further nested elements.

It's generally assumed that the root element will be a `["pre", {}]`,
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

Pygments Errors
===============

This project relies on the Pygments library for most of its highlighting.
In an attempt to make this library standalone,
I include a local copy of Pygments.
As documented in [this Pygments issue](https://bitbucket.org/birkenfeld/pygments-main/issues/1448/pygments-relies-on-global-imports-of-its),
however,
Pygments actually *can't* be used stand-alone,
as it is written to pervasively use global imports of its own code.

I'm in the process of fixing this in my local copy of the Pygments source
(and hope to upstream it eventually),
but it's a decent chunk of work.
In the meantime,
you should `pip install pygments` to get a global install of the library as well,
or else this project won't work.
(Or otherwise install it with whatever tools you have,
as documented [on the Pygments site](http://pygments.org/).)
