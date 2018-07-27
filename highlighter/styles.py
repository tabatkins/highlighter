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

# Following classes were renamed to single-character names,
# as they're common and this'll save us a single character of output.
'''
na
nt
nv
kd
kt
s1
s2
cm
'''

highlight = '''
.highlight:not(.idl) { background: hsl(24, 20%, 95%); }
code.highlight { padding: .1em; border-radius: .3em; }
pre.highlight, pre > code.highlight { display: block; padding: 1em; margin: .5em 0; overflow: auto; border-radius: 0; }
c-[a] { color: #990055 } /* Keyword.Declaration */
c-[b] { color: #990055 } /* Keyword.Type */
c-[c] { color: #708090 } /* Comment */
c-[d] { color: #708090 } /* Comment.Multiline */
c-[e] { color: #0077aa } /* Name.Attribute */
c-[f] { color: #669900 } /* Name.Tag */
c-[g] { color: #222222 } /* Name.Variable */
c-[k] { color: #990055 } /* Keyword */
c-[l] { color: #000000 } /* Literal */
c-[m] { color: #000000 } /* Literal.Number */
c-[n] { color: #0077aa } /* Name */
c-[o] { color: #999999 } /* Operator */
c-[p] { color: #999999 } /* Punctuation */
c-[s] { color: #a67f59 } /* Literal.String */
c-[t] { color: #a67f59 } /* Literal.String.Single */
c-[u] { color: #a67f59 } /* Literal.String.Double */
c-[cp] { color: #708090 } /* Comment.Preproc */
c-[c1] { color: #708090 } /* Comment.Single */
c-[cs] { color: #708090 } /* Comment.Special */
c-[kc] { color: #990055 } /* Keyword.Constant */
c-[kn] { color: #990055 } /* Keyword.Namespace */
c-[kp] { color: #990055 } /* Keyword.Pseudo */
c-[kr] { color: #990055 } /* Keyword.Reserved */
c-[ld] { color: #000000 } /* Literal.Date */
c-[nc] { color: #0077aa } /* Name.Class */
c-[no] { color: #0077aa } /* Name.Constant */
c-[nd] { color: #0077aa } /* Name.Decorator */
c-[ni] { color: #0077aa } /* Name.Entity */
c-[ne] { color: #0077aa } /* Name.Exception */
c-[nf] { color: #0077aa } /* Name.Function */
c-[nl] { color: #0077aa } /* Name.Label */
c-[nn] { color: #0077aa } /* Name.Namespace */
c-[py] { color: #0077aa } /* Name.Property */
c-[ow] { color: #999999 } /* Operator.Word */
c-[mb] { color: #000000 } /* Literal.Number.Bin */
c-[mf] { color: #000000 } /* Literal.Number.Float */
c-[mh] { color: #000000 } /* Literal.Number.Hex */
c-[mi] { color: #000000 } /* Literal.Number.Integer */
c-[mo] { color: #000000 } /* Literal.Number.Oct */
c-[sb] { color: #a67f59 } /* Literal.String.Backtick */
c-[sc] { color: #a67f59 } /* Literal.String.Char */
c-[sd] { color: #a67f59 } /* Literal.String.Doc */
c-[se] { color: #a67f59 } /* Literal.String.Escape */
c-[sh] { color: #a67f59 } /* Literal.String.Heredoc */
c-[si] { color: #a67f59 } /* Literal.String.Interpol */
c-[sx] { color: #a67f59 } /* Literal.String.Other */
c-[sr] { color: #a67f59 } /* Literal.String.Regex */
c-[ss] { color: #a67f59 } /* Literal.String.Symbol */
c-[vc] { color: #0077aa } /* Name.Variable.Class */
c-[vg] { color: #0077aa } /* Name.Variable.Global */
c-[vi] { color: #0077aa } /* Name.Variable.Instance */
c-[il] { color: #000000 } /* Literal.Number.Integer.Long */
'''

lineNumber = '''
.line-numbered {
    display: grid !important;
    grid-template-columns: min-content 1fr;
    grid-auto-flow: row;
}
.line-numbered > *,
.line-numbered::before,
.line-numbered::after {
    grid-column: 1/-1;
}
.line-no {
    grid-column: 1;
    color: gray;
}
.line {
    grid-column: 2;
}
.line:hover {
    background: rgba(0,0,0,.05);
}
.line-no[data-line]::before {
    padding: 0 .5em 0 .1em;
    content: attr(data-line);
}
.line-no[data-line-end]::after {
    padding: 0 .5em 0 .1em;
    content: attr(data-line-end);
}
'''

lineHighlight = '''
.line-numbered {
    display: grid !important;
    grid-template-columns: min-content 1fr;
    grid-auto-flow: rows;
}
.line-numbered > *,
.line-numbered::before,
.line-numbered::after {
    grid-column: 1/-1;
}
.line-no {
    grid-column: 1;
    color: gray;
}
.line {
    grid-column: 2;
}
.line.highlight-line {
    background: rgba(0,0,0,.05);
}
.line-no.highlight-line {
    background: rgba(0,0,0,.05);
    color: #444;
    font-weight: bold;
}
.line-no.highlight-line[data-line]::before {
    padding: 0 .5em 0 .1em;
    content: attr(data-line);
}
.line-no.highlight-line[data-line-end]::after {
    padding: 0 .5em 0 .1em;
    content: attr(data-line-end);
}
'''
