# To regen the styles, edit and run the below
#from pygments import token
#from pygments import style
#class PrismStyle(style.Style):
#    default_style = "#000000"
#    styles = {
#        token.Name: "#007299",
#        token.Name.Tag: "#008000",
#        token.Name.Builtin: "noinherit",
#        token.Name.Variable: "#222222",
#        token.Name.Other: "noinherit",
#        token.Operator: "#008000",
#        token.Punctuation: "#545454",
#        token.Keyword: "#d91e18",
#        token.Literal: "#000000",
#        token.Literal.Number: "#000000",
#        token.Literal.String: "#aa5d00",
#        token.Comment: "#696969"
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
c-[a] { color: #d91e18 } /* Keyword.Declaration */
c-[b] { color: #d91e18 } /* Keyword.Type */
c-[c] { color: #696969 } /* Comment */
c-[d] { color: #696969 } /* Comment.Multiline */
c-[e] { color: #007299 } /* Name.Attribute */
c-[f] { color: #008000 } /* Name.Tag */
c-[g] { color: #222222 } /* Name.Variable */
c-[k] { color: #d91e18 } /* Keyword */
c-[l] { color: #000000 } /* Literal */
c-[m] { color: #000000 } /* Literal.Number */
c-[n] { color: #007299 } /* Name */
c-[o] { color: #008000 } /* Operator */
c-[p] { color: #545454 } /* Punctuation */
c-[s] { color: #aa5d00 } /* Literal.String */
c-[t] { color: #aa5d00 } /* Literal.String.Single */
c-[u] { color: #aa5d00 } /* Literal.String.Double */
c-[cp] { color: #696969 } /* Comment.Preproc */
c-[c1] { color: #696969 } /* Comment.Single */
c-[cs] { color: #696969 } /* Comment.Special */
c-[kc] { color: #d91e18 } /* Keyword.Constant */
c-[kn] { color: #d91e18 } /* Keyword.Namespace */
c-[kp] { color: #d91e18 } /* Keyword.Pseudo */
c-[kr] { color: #d91e18 } /* Keyword.Reserved */
c-[ld] { color: #000000 } /* Literal.Date */
c-[nc] { color: #007299 } /* Name.Class */
c-[no] { color: #007299 } /* Name.Constant */
c-[nd] { color: #007299 } /* Name.Decorator */
c-[ni] { color: #007299 } /* Name.Entity */
c-[ne] { color: #007299 } /* Name.Exception */
c-[nf] { color: #007299 } /* Name.Function */
c-[nl] { color: #007299 } /* Name.Label */
c-[nn] { color: #007299 } /* Name.Namespace */
c-[py] { color: #007299 } /* Name.Property */
c-[ow] { color: #008000 } /* Operator.Word */
c-[mb] { color: #000000 } /* Literal.Number.Bin */
c-[mf] { color: #000000 } /* Literal.Number.Float */
c-[mh] { color: #000000 } /* Literal.Number.Hex */
c-[mi] { color: #000000 } /* Literal.Number.Integer */
c-[mo] { color: #000000 } /* Literal.Number.Oct */
c-[sb] { color: #aa5d00 } /* Literal.String.Backtick */
c-[sc] { color: #aa5d00 } /* Literal.String.Char */
c-[sd] { color: #aa5d00 } /* Literal.String.Doc */
c-[se] { color: #aa5d00 } /* Literal.String.Escape */
c-[sh] { color: #aa5d00 } /* Literal.String.Heredoc */
c-[si] { color: #aa5d00 } /* Literal.String.Interpol */
c-[sx] { color: #aa5d00 } /* Literal.String.Other */
c-[sr] { color: #aa5d00 } /* Literal.String.Regex */
c-[ss] { color: #aa5d00 } /* Literal.String.Symbol */
c-[vc] { color: #007299 } /* Name.Variable.Class */
c-[vg] { color: #007299 } /* Name.Variable.Global */
c-[vi] { color: #007299 } /* Name.Variable.Instance */
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
