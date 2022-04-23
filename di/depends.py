from typing import Callable, Generic, Iterator, TypeVar, Union, overload

_RType = TypeVar("_RType")


class _Depends(Generic[_RType]):
    def __init__(
        self,
        dependency: Union[Callable[..., _RType], Callable[..., Iterator[_RType]]],
        *,
        use_cache: bool = True,
    ):
        self.dependency = dependency
        self.use_cache = use_cache


@overload
def Depends(
    dependency: Callable[..., Iterator[_RType]],
    *,
    use_cache: bool = True,
) -> _RType:
    ...


@overload
def Depends(
    dependency: Callable[..., _RType],
    *,
    use_cache: bool = True,
) -> _RType:
    ...


def Depends(
    dependency: Union[Callable[..., _RType], Callable[..., Iterator[_RType]]],
    *,
    use_cache: bool = True,
) -> _RType:
    return _Depends(dependency, use_cache=use_cache)  # type: ignore
