def isElement(node):
    return isinstance(node, list)

def hasChildElements(node):
    return any(isElement(x) for x in node[2:])

def children(node, clear=False):
    if isElement(node):
        return node[2:]
    else:
        return []

def textContent(el):
    def textIterator(el):
        for item in children(el):
            if isinstance(item, str):
                yield item
            else:
                yield from textIterator(item)
    return "".join(textIterator(el))

def mapTextNodes(node, fn):
    if isElement(node):
        ret = copyNode(clearChildren(node))
        for child in children(node):
            ret.append(mapTextNodes(child, fn))
        return ret
    else:
        return fn(node)

def copyNode(node):
    if isElement(node):
        return [node[0], node[1].copy()] + list(map(copyNode, node[2:]))
    else:
        return node

def clearChildren(node):
    if isElement(node):
        return node[:2]
    else:
        return node

def tagName(node):
    if isElement(node):
        return node[0]
    else:
        return None

def attrs(node):
    if isElement(node):
        if len(node) == 1:
            a = {}
            node.append(a)
            return a
        return node[1]
    else:
        return {}

def addClass(node, cls):
    a = attrs(node)
    if "class" in a:
        a["class"] += " " + cls
    else:
        a["class"] = cls
    return node

def appendChild(node, *children):
    node.extend(children)
    return node

def isEmpty(node):
    return len(node) == 2

def escapeHtml(str):
    return (str
        .replace("&", "&amp;")
        .replace("'", "&apos;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def unescapeHtml(str):
    return (str
        .replace("&gt;", ">")
        .replace("&lt;", "<")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
        .replace("&amp;", "&")
    )

class ElementCreationHelper:
    def __getattr__(self, name):
        name = name.replace("_", "-")
        def _creater(*children):
            children = list(children)
            if children and isinstance(children[0], dict):
                attrs = children[0]
                children = children[1:]
            else:
                attrs = {}
            return [name, attrs] + children
        return _creater
E = ElementCreationHelper()
