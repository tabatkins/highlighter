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

You can install this as a command-line script using `pipx`: `pipx install bs-highlighter`.
This will create a command `bs-highlighter` which invokes the CLI interface,
and a command `bs-highlighter-server` which starts an HTTP server
(useful if you're doing a lot of highlights and don't want to pay Python startup costs repeatedly; see below for details).

Basic usage requires you to pass the language you're highlighting as, followed by the text you want to highlight:

```bash
bs-highlighter webidl "interface Foo {};"
```

> [!TIP]
> The supported languages are [everything that Pygments supports](http://pygments.org/languages/),
> plus "webidl" for WebIDL.
> I also use a custom CSS highlighter that better handles arbitrary modern CSS.

If you want to highlight somethign that already contains markup, 
instead pass JSON-encoded HTML (see below), like:

```bash
bs-highlighter webidl '["pre", {}, "interface ", ["dfn", {"id":"dom-foo"}, "Foo"], " {};"]'
```

If you pass `-` as the text, it will instead read from STDIN.

By default, the command returns the highlighted HTML as JSON-encoded HTML (see below),
but you can also have it return the output as HTMl source text,
and/or include some useful CSS to be used with the HTML.
See the command-line options in the next section.

### Command-Line Options

Highlighter has a number of command-line options to customize its operation

<dl>
<dt><code>--input = auto | json | text</code>
<dd>

Defaults to `auto`.

Specifies whether the input value is JSON-encoded HTML or raw text.
The default value, `auto`, just checks if the first character of the input is a `"["`.

<dt><code>--output = json | html</code>
<dd>

Defaults to `json`.

Determines whether the highlighted output is returned as JSON-encoded HTML,
or HTML source text.

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

<dt><code>--just= html | css | both</code>
<dd>

Defaults to `html`.

Determines whether the output will be just the highlighted html,
just the CSS needed to format that HTML,
or a wrapping JSON object containing both, as `{"html":..., "css":...}`.

<dt><code>--unescape</code>
<dd>

Does a quick unescape pass over the input HTML, reverting one level of HTML escapes for the standard dangerous HTML characters `&<>'"`, and decimal/hex escapes. Use if your DOM implementation doesn't convert escapes to text. Won't unescape any other HTML escapes, so beware!
</dl>

## Using A Bunch In Quick Succession

Instead of the CLI interface, you can instead run the `bs-highlighter-server` command
to start up a simple local HTTP server.
This is useful if you're going to do a lot of highlights,
and don't want to pay Python startup times for every single one.

This server speaks simple `GET` requests,
interpreting the path as CLI arguments,
and the query as the text to highlight, like:

`localhost:8080/--output=html webidl?interface Foo {};`

If successful, it will return a 200 OK response,
whose body is the same output as the command line for the given output,
except that `--just=html` is always implicitly passed and can't be overridden.

If unsuccessful, it will return a 400 response,
whose body is the error message.

The `bs-highlighter-server` command-line args are simple:

```
  --quiet      Don't report informational messages.
  --host HOST  The server host. (default: localhost)
  --port PORT  The port number. (default: 8080)
```

## Using as a normal Python module

This can, of course, be used as an ordinary Python module in a Python script.
Import the module, then call the `highlight()` function with a JSON object, like:

```python
import highlighter

html,css = highlighter.highlight(["pre", {}, "interface Foo {};"], lang="webidl")
print(html)
# ['pre', {}, ['c-', {'b': ''}, 'interface'], ' ', ['c-', {'g': ''}, 'Foo'], ' {};']
# or, with `output="html"`:
# '<pre><c- b>interface</c-> <c- g>Foo</c-> {};</pre>'
```

The first required input is a JSON-encoded HTML object (see below for details),
where the text of the HTML is what's going to be highlighted,
*or* a string of source code that's going to be highlighted.
(In the example above, `"interface Foo {};` is what will be syntax-highlighted;
that string could also be passed by itself.)
The second is the language to highlight it as,
which can be [everything that Pygments supports](http://pygments.org/languages/),
plus "webidl" for WebIDL.

The output is a 2-tuple,
with the first being a JSON object for the highlighted markup as JSON-encoded HTML (see below)
or a string of HTML source (see the `output` argument),
and the second being a string of CSS you can use directly to style the highlighted markup.

Additional possible arguments:

* `lineNumbers: bool = False` - whether to add line numbers to the output or not. The root element gains a `class=line-numbered`, and the markup becomes alternating `<span class=line-no>1</span>` and `<span class=line>...</span>` elements, styled by default using CSS Grid. (Note, using line highlights also implicitly adds line numbers to the highlighted lines.)
* `lineStart: int = 1` - what line number the text starts at, for line numbering.
* `lineHighlights: set[int] | str | None = None` - which lines should be given a special `class=line-highlight`, on both the `.line-no` and `.line` elements. The highlighted lines are also automatically numbered, and the line numbers are relative to `lineStart`'s value (thus matching the displayed line number). If passed as a `str`, it's parsed as a comma-separated list of line numbers or ranges, like `"2-4, 6"`, equivalent to `set([2, 3, 4, 6])`.
* `output: Literal["json"] | Literal["html"] = "json"` - what format to return the highlighted markup in. By default it's a JSON object, but passing "html" causes it to instead be a string of HTML, useful if you're just going to drop the HTML directly into your output anyway. If HTML, it's automatically escaped to be safe.
* `unescape: bool = False` - if True, automatically processes *some* HTML escapes in the text nodes and attribute values of the input: any decimal (`&#123;`) or hex (`&#x123;`) escapes, or the five "canonical" named escapes (`&amp;`, `&lt;`, `&gt;`, `&apos;`, `&quot;`). No other named escapes are recognized. This should only be used if your markup pipeline is broken and auto-escapes things (unfortunately common).


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
> You *probably* want the root element of your input to be a `["pre", {}, ...]`,
> to preserve the linebreaks in your source.
> The highlighted output will still, generally, rely on your linebreaks.

# Output HTML

The output HTML structure retains all the markup you passed in
(or returns a `<pre>` wrapper element containing your text, if you passed a string),
and additionally adds the following markup:

* `<c->...</c->` custom elements to indicate colored text,
	with a one- or two-letter attribute indicating what category it's highlighted as.
	See [`styles.py`](https://github.com/tabatkins/highlighter/blob/main/highlighter/styles.py)
	(or the generated CSS)
	for the attributes and what each stands for.
	If there was existing markup in the input (links, etc),
	the `c-` elements are nested "tightly", directly around the text,
	and won't have any element children themselves,
	to avoid disrupting your markup structure.

	(These are valid HTML custom elements, as short as it is possible to generate,
	as highlighting can add significant amounts of markup.)
* If you are using line numbers and/or highlights,
	the root element has a `.line-numbered` class added to it.
	The root element's children are an alternating list of
	`<span class=line-no></span>`  elements
	(empty, but with a `data-line` attribute containing the line number
	if it should be displayed;
	inserted into the output via a CSS `::before` so it's not included in copy/paste)
	and `<span class=line>...</span>` elements containing the contents of that line.
	The default CSS lays these out using CSS Grid.
	If using line highlights, 
	the highlighted lines additionally have `.line-highlight` classes
	on both `.line-no` and `.line`.

	If there was existing markup in the input,
	and an element crosses two or more lines of the source,
	it will be preserved as-is,
	and the `.line` span will wrap around as many lines as needed to contain it
	(so `.line` only breaks on a top-level newline character, directly under the root element).
	The `.line-no` element preceding that `.line` 
	will additionally have a `data-line-end` attribute,
	so it can display the start and end of the span
	(so, if it's only two lines, you won't notice anything;
	if it's 3 or more, the "interior" lines won't receive numbers).

The returned CSS has all the styling you should need for all of these markup structures,
but you can of course use whatever styling you wish.