from typing import Callable, Iterator, TypeVar, Union

RType = TypeVar("RType")
FactoryType = Union[
    Callable[..., RType],
    Callable[..., Iterator[RType]],
]
