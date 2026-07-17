Highlighter
===========

This project extracts and abstracts [Bikeshed's](https://www.github.com/tabatkins/bikeshed) syntax-highlighting functionality for usage by other tools.

This is intended for use by non-Python tools
(namely, spec processors written in other languages)
that want to use the same highlighting as Bikeshed-using specs.
This informs some oddities of its design,
like using JSON to transmit markup,
as that is easy to produce and consume across languages.

Note that, like Bikeshed, this tool allows you to highlight text
that already contains markup;
the highlights are merged into the existing markup,
pushed as deeply as possible to directly wrap the highlighted text.
This is why the tool both consumes and emits *markup*,
not the text directly.

## Using As a Single-Shot

You can install this as a command-line script using `pip`: `pip install bs-highlighter`.
This will create a command `highlight` which invokes the CLI interface.
Or, without installing, you can directly run the `__init__.py` script in this folder,
though that does still require you to install the prereqs;
see `requirements.txt`.

When invoked, you must pass the markup to be highlighted as a string of JSON (see below) as STDIN, and the desired highlighting language as the first argument, like:

```bash
echo '["pre", {}, "interface Foo {};"]' | ./__init__.py webidl
```

> [!TIP]
> The supported languages are [everything that Pygments supports](http://pygments.org/languages/),
> plus "webidl" for WebIDL.

The return value is, by default, 
a JSON object containing two keys:
`html`, which contains the highlighted markup as JSON-encoded HTML (see below),
and `css` which is a string of CSS you can use directly to style the highlighted markup.

### Command-Line Options

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

## Using A Bunch In Quick Succession

Instead of the CLI interface, you can instead invoke the `server.py` script in this folder
to start up a simple local HTTP server on port 8080.
This is useful if you're going to do a lot of highlights,
and don't want to pay Python startup times for every single one.

This server speaks simple `GET` requests,
with a path equal to the desired highlight language
and a query param of the json data, like:

`localhost:8080/webidl?["pre", {}, "interface Foo {};"]`

If successful, it will return a 200 OK response,
whose body is the highlighted markup as JSON.

There is not currently any way to pass additional options to the server script.
Since you have to be running the script directly anyway,
just modify the `highlighter.highlight()` invocation
with your desired options.

## Using as a normal Python module

This can, of course, be used as an ordinary Python module in a Python script.
Import the module, then call the `highlight()` function with a JSON object, like:

```python
import highlighter

html,css = highlighter.highlight(["pre", {}, "interface Foo {};"], lang="webidl")
```

The default output is a 2-tuple,
with the first being a JSON object for the highlighted markup as JSON-encoded HTML (see below),
and the second being a string of CSS you can use directly to style the highlighted markup.

Additional possible arguments:

* `lineNumbers: bool = False` - whether to add line numbers to the output or not. The root element gains a `class=line-numbered`, and the markup becomes alternating `<span class=line-no>1</span>` and `<span class=line>...</span>` elements, styled by default using CSS Grid. (Note, using line highlights also implicitly adds line numbers to the highlighted lines.)
* `lineStart: int = 1` - what line number the text starts at, for line numbering.
* `lineHighlights: set[int] | str | None = None` - which lines should be given a special `class=line-highlight`, on both the `.line-no` and `.line` elements. The highlighted lines are also automatically numbered, and the line numbers are relative to `lineStart`'s value (thus matching the displayed line number). If passed as a `str`, it's parsed as a comma-separated list of line numbers or ranges, like `"2-4, 6"`, equivalent to `set([2, 3, 4, 6])`.
* `output: Literal["json"] | Literal["html"] = "json"` - what format to return the highlighted markup in. By default it's a JSON object, but passing "html" causes it to instead be a string of HTML, useful if you're just going to drop the HTML directly into your output anyway. If HTML, it's automatically escaped to be safe.
* `unescape: bool = False` - if True, automatically processes *some* HTML escapes in the text nodes of the input: any decimal (`&#123;`) or hex (`&#x123;`) escapes, or the five "canonical" named escapes (`&amp;`, `&lt;`, `&gt;`, `&apos;`, `&quot;`). No other named escapes are recognized. This should only be used if your markup pipeline is broken and auto-escapes things (unfortunately common).


# HTML as JSON

Because this tool can highlight text that already contains markup,
merging the highlight markup into the existing elements,
both its input and output are trees of HTML markup
instead of simple text.
However, HTML is non-trivial to parse in most languages,
so to maximize the ease of use,
this tool instead takes html-in-json,
a trivial encoding of HTML trees into a simple JSON structure.

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

HTML escapes (like &amp;lt;) are not recognized here;
attribute values and text children are taken exacly as written.
The same applies to the output;
if rendering back to HTML,
remember to correctly escape attribute values and text nodes.

> [!NOTE]
> It's generally assumed that the root element will be a `["pre", {}]`,
> to preserve the linebreaks in your source.


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

