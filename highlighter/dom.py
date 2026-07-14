from __future__ import annotations

from . import t


def isElement(node: t.Node) -> t.TypeIs[t.Element]:
    return isinstance(node, list)


def isNode(node: t.Any) -> t.TypeIs[t.Node]:
    return isinstance(node, (list, str))


def hasChildElements(node: t.Node) -> bool:
    return any(isElement(x) for x in node[2:])


def children(node: t.Node) -> list[t.Node]:
    if isElement(node):
        return t.cast("list[t.Node]", node[2:])
    else:
        return []


def textContent(el: t.Element) -> str:
    def textIterator(el: t.Element) -> t.Iterator[str]:
        for item in children(el):
            if isinstance(item, str):
                yield item
            else:
                yield from textIterator(item)

    return "".join(textIterator(el))


def mapTextNodes(el: t.Element, fn: t.Callable[[str], t.Node]) -> t.Element:
    ret = t.cast("list[t.Any]", copyNode(clearChildren(el)))
    for child in children(el):
        if isElement(child):
            ret.append(mapTextNodes(child, fn))
        else:
            ret.append(fn(child))
    return t.cast("t.Element", ret)


@t.overload
def copyNode(node: t.Element) -> t.Element: ...
@t.overload
def copyNode(node: str) -> str: ...
@t.overload
def copyNode(node: t.Node) -> t.Node: ...
def copyNode(node: t.Node) -> t.Node:
    if isElement(node):
        if len(node) == 1:
            return t.cast("t.Element", [node[0], {}])
        return t.cast("t.Element", [node[0], node[1].copy()] + list(map(copyNode, children(node))))
    else:
        return node


@t.overload
def clearChildren(node: t.Element) -> t.Element: ...
@t.overload
def clearChildren(node: str) -> str: ...
@t.overload
def clearChildren(node: t.Node) -> t.Node: ...
def clearChildren(node: t.Node) -> t.Node:
    if isElement(node):
        return node[:2]
    else:
        return node


def tagName(node: t.Node) -> str | None:
    if isElement(node):
        return node[0]
    else:
        return None


def attrs(node: t.Node) -> dict[str, str]:
    if isElement(node):
        if len(node) == 1:
            a: dict[str, str] = {}
            t.cast("list[t.Any]", node).append(a)
            return a
        return node[1]
    else:
        return {}


def addClass(node: t.Element, cls: str) -> t.Element:
    a = attrs(node)
    if "class" in a:
        a["class"] += " " + cls
    else:
        a["class"] = cls
    return node


def appendChild(node: t.Element, *childNodes: t.Node) -> t.Element:
    t.cast("list[t.Any]", node).extend(childNodes)
    return node


def isEmpty(node: t.Element) -> bool:
    return len(node) <= 2


def escapeHtml(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("'", "&apos;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
    )


def unescapeHtml(s: str) -> str:
    return (
        s.replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")
    )


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
