# pylint: skip-file
# Module for holding types, for easy importing into the rest of the codebase
from __future__ import annotations

# The only things that should be available during runtime.
from typing import TYPE_CHECKING, Generic, NewType, TypedDict, TypeVar, assert_never, assert_type, cast, overload

if TYPE_CHECKING:
    from typing import (
        AbstractSet,
        Any,
        AnyStr,
        Awaitable,
        Callable,
        Collection,
        Container,
        DefaultDict,
        Deque,
        FrozenSet,
        Generator,
        Iterable,
        Iterator,
        Literal,
        LiteralString,
        Mapping,
        MutableMapping,
        MutableSequence,
        NamedTuple,
        NoReturn,
        Protocol,
        Sequence,
        TextIO,
        Type,
        TypeAlias,
        TypeGuard,
    )

    from typing_extensions import TypeIs

    type Element = tuple[str] | tuple[str, dict[str, str], *tuple[Node, ...]]
    type Node = Element | str
