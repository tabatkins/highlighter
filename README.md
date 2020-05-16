Highlighter
===========

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

(See [Command-Line Options](#command-line-options)
or run `highlighter/__init__.py -h` to see all the command-line options.)

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

Command-Line Options
====================

Highlighter has a number of command-line options to customize its operation
(many inspired by its first major user,
if they seem oddly ideosyncratic).

<dl>
<dt><code>--output=json</code> or <code>--output=html</code>
<dd>

Defaults to `json`.

Determines whether the highlighted output is returned as JSON-encoded HTML
(like the input),
or just as a plain string of HTML.

<dt><code>--numbers</code>
<dd>

If passed, adds line numbers to the output.

Defaults to treating the first line as "1";
use in conjunction with `--start` for more customization.

<dt><code>--highlights=&lt;range></code>
<dd>

Tells the processor which lines to specially highlight,
by default giving them a darker background to draw the eye.

The `<range>` is a list of comma-separated line ranges,
each of which is either a single number
or a hyphenated range,
like `1, 3-5` to highlight the lines 1, 3, 4, and 5.

The highlighted lines will be numbered automatically,
even if `--numbers` isn't passed.

Same as `--numbers`,
defaults to treating the first line as "1";
use in conjunction with `--start` for more customization.

<dt><code>--start=&lt;number></code>
<dd>

Defaults to `1`.

Tells the highlighter what number the first line should be treated as.

For example, if you're showing a small fragment of code from a larger file,
you can tell it that the code actually starts on, say, line 1500
with `--start=1500`,
so the displayed line numbers will match up with those of the source file you're excerpting.

<dt><code>--just=html</code> or <code>--just=css</code>
<dd>

If passed, the output will be *just* the HTML or CSS for the highlighting,
rather than a JSON object containing both.
There will be no overall wrapping JSON object.
</dl>