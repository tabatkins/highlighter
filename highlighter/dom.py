from __future__ import annotations

import re

from . import t


def isElement(node: t.Node) -> t.TypeIs[t.Element]:
    return isinstance(node, list)


def isNode(node: t.Any) -> t.TypeIs[t.Node]:
    return isinstance(node, (list, str))


def textContent(el: t.Element) -> str:
    def textIterator(el: t.Element) -> t.Iterator[str]:
        for item in children(el):
            if isinstance(item, str):
                yield item
            else:
                yield from textIterator(item)

    return "".join(textIterator(el))


def tagName(el: t.Element) -> str:
    return el[0]


def attrs(el: t.Element) -> dict[str, str]:
    if len(el) == 1:
        a: dict[str, str] = {}
        t.cast("list[t.Any]", el).append(a)
        return a
    return el[1]


def children(el: t.Element) -> list[t.Node]:
    return t.cast("list[t.Node]", el[2:])


def withoutChildren(el: t.Element) -> t.Element:
    return t.cast("t.Element", el[0:2])


def addClass(node: t.Element, cls: str) -> t.Element:
    a = attrs(node)
    if "class" in a:
        a["class"] += " " + cls
    else:
        a["class"] = cls
    return node


def appendChild(el: t.Element, *childNodes: t.Node) -> t.Element:
    t.cast("list[t.Any]", el).extend(childNodes)
    return el


def setChild(el: t.Element, index: int, childNode: t.Node) -> t.Element:
    if index + 2 >= len(el):
        raise IndexError
    t.cast("list[t.Any]", el)[index + 2] = childNode
    return el


def isEmpty(el: t.Element) -> bool:
    return len(el) <= 2


def hasChildElements(node: t.Node) -> bool:
    return any(isElement(x) for x in node[2:])


def escapeHtml(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("'", "&apos;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
    )


def unescapeElement(el: t.Element) -> t.Element:
    for key, val in attrs(el).items():
        el[1][key] = unescapeHtml(val)
    for i, child in enumerate(children(el)):
        if isElement(child):
            setChild(el, i, unescapeElement(child))
        else:
            setChild(el, i, unescapeHtml(child))
    return el


def unescapeHtml(s: str) -> str:
    ret = s.replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&apos;", "'")
    ret = re.sub(r"&#(\d+);?", lambda match: chr(int(match[1])), ret)
    ret = re.sub(r"&#x([\da-fA-F]+);?", lambda match: chr(int(match[1], 16)), ret)
    ret = ret.replace("&amp;", "&")
    return ret


if t.TYPE_CHECKING:

    class ElementCreatorFnT(t.Protocol):
        def __call__(
            self,
            attrsOrChild: t.Mapping[str, str | None] | t.Node,
            *childNodes: t.Node,
        ) -> t.Element: ...


def createElement(tag: str, attr: dict[str, str], *childNodes: t.Node) -> t.Element:
    return t.cast("t.Element", [tag, attr, *childNodes])


class ElementCreationHelper:
    def __getattr__(self, name: str) -> ElementCreatorFnT:
        name = name.replace("_", "-")

        def _creater(
            attrsOrChild: t.Mapping[str, str | None] | t.Node,
            *childNodes: t.Node,
        ) -> t.Element:
            if isNode(attrsOrChild):
                return createElement(name, {}, attrsOrChild, *childNodes)
            else:
                assert isinstance(attrsOrChild, dict) or attrsOrChild is None
                return createElement(name, attrsOrChild, *childNodes)

        return _creater


E = ElementCreationHelper()
