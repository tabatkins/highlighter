def isElement(node):
    return isinstance(node, list)

def hasChildElements(node):
    return any(isElement(x) for x in node[2:])

def children(node, clear=False):
    if isElement(node):
        return node[2:]
    else:
        return []

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
        return node[1]
    else:
        return {}

def addClass(node, cls):
    a = attrs(node)
    if "class" in attrs:
        attrs["class"] += " " + cls
    else:
        attrs["class"] = cls
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
        .replace(">", "&gt;"))

class ElementCreationHelper:
    def __getattr__(self, name):
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