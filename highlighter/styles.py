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
highlight = '''
.highlight:not(.idl) { background: hsl(24, 20%, 95%); }
code.highlight { padding: .1em; border-radius: .3em; }
pre.highlight, pre > code.highlight { display: block; padding: 1em; margin: .5em 0; overflow: auto; border-radius: 0; }
.highlight .c { color: #708090 } /* Comment */
.highlight .k { color: #990055 } /* Keyword */
.highlight .l { color: #000000 } /* Literal */
.highlight .n { color: #0077aa } /* Name */
.highlight .o { color: #999999 } /* Operator */
.highlight .p { color: #999999 } /* Punctuation */
.highlight .cm { color: #708090 } /* Comment.Multiline */
.highlight .cp { color: #708090 } /* Comment.Preproc */
.highlight .c1 { color: #708090 } /* Comment.Single */
.highlight .cs { color: #708090 } /* Comment.Special */
.highlight .kc { color: #990055 } /* Keyword.Constant */
.highlight .kd { color: #990055 } /* Keyword.Declaration */
.highlight .kn { color: #990055 } /* Keyword.Namespace */
.highlight .kp { color: #990055 } /* Keyword.Pseudo */
.highlight .kr { color: #990055 } /* Keyword.Reserved */
.highlight .kt { color: #990055 } /* Keyword.Type */
.highlight .ld { color: #000000 } /* Literal.Date */
.highlight .m { color: #000000 } /* Literal.Number */
.highlight .s { color: #a67f59 } /* Literal.String */
.highlight .na { color: #0077aa } /* Name.Attribute */
.highlight .nc { color: #0077aa } /* Name.Class */
.highlight .no { color: #0077aa } /* Name.Constant */
.highlight .nd { color: #0077aa } /* Name.Decorator */
.highlight .ni { color: #0077aa } /* Name.Entity */
.highlight .ne { color: #0077aa } /* Name.Exception */
.highlight .nf { color: #0077aa } /* Name.Function */
.highlight .nl { color: #0077aa } /* Name.Label */
.highlight .nn { color: #0077aa } /* Name.Namespace */
.highlight .py { color: #0077aa } /* Name.Property */
.highlight .nt { color: #669900 } /* Name.Tag */
.highlight .nv { color: #222222 } /* Name.Variable */
.highlight .ow { color: #999999 } /* Operator.Word */
.highlight .mb { color: #000000 } /* Literal.Number.Bin */
.highlight .mf { color: #000000 } /* Literal.Number.Float */
.highlight .mh { color: #000000 } /* Literal.Number.Hex */
.highlight .mi { color: #000000 } /* Literal.Number.Integer */
.highlight .mo { color: #000000 } /* Literal.Number.Oct */
.highlight .sb { color: #a67f59 } /* Literal.String.Backtick */
.highlight .sc { color: #a67f59 } /* Literal.String.Char */
.highlight .sd { color: #a67f59 } /* Literal.String.Doc */
.highlight .s2 { color: #a67f59 } /* Literal.String.Double */
.highlight .se { color: #a67f59 } /* Literal.String.Escape */
.highlight .sh { color: #a67f59 } /* Literal.String.Heredoc */
.highlight .si { color: #a67f59 } /* Literal.String.Interpol */
.highlight .sx { color: #a67f59 } /* Literal.String.Other */
.highlight .sr { color: #a67f59 } /* Literal.String.Regex */
.highlight .s1 { color: #a67f59 } /* Literal.String.Single */
.highlight .ss { color: #a67f59 } /* Literal.String.Symbol */
.highlight .vc { color: #0077aa } /* Name.Variable.Class */
.highlight .vg { color: #0077aa } /* Name.Variable.Global */
.highlight .vi { color: #0077aa } /* Name.Variable.Instance */
.highlight .il { color: #000000 } /* Literal.Number.Integer.Long */
'''

lineNumber = '''
.line {
    padding-left: 1.4em;
    position: relative;
}
.line:hover {
    background: rgba(0,0,0,.05);
}
.line[line]::before {
    content: attr(line);
    position: absolute;
    top: 0;
    left: 1px;
    color: gray;
}
.line[line-end]::after {
    content: attr(line-end);
    position: absolute;
    bottom: 0;
    left: 1px;
    color: gray;
}
'''

lineHighlight = '''
.line {
    padding-left: 1.4em;
    position: relative;
}
.line.highlight-line {
    background: rgba(0,0,0,.05);
}
.line.highlight-line[line]::before {
    content: attr(line);
    position: absolute;
    top: 0;
    left: 1px;
    color: gray;
}
.line.highlight-line[line-end]::after {
    content: attr(line-end);
    position: absolute;
    bottom: 0;
    left: 1px;
    color: gray;
}
'''