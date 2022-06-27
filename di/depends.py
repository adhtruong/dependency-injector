from typing import Callable, Generic, Iterator, overload

from di.types import FactoryType, RType


class _Depends(Generic[RType]):
    def __init__(
        self,
        dependency: FactoryType[RType],
        *,
        use_cache: bool = True,
    ):
        self.dependency = dependency
        self.use_cache = use_cache


@overload
def Depends(
    dependency: Callable[..., Iterator[RType]],
    *,
    use_cache: bool = True,
) -> RType:
    ...


@overload
def Depends(
    dependency: Callable[..., RType],
    *,
    use_cache: bool = True,
) -> RType:
    ...


def Depends(
    dependency: FactoryType[RType],
    *,
    use_cache: bool = True,
) -> RType:
    return _Depends(dependency, use_cache=use_cache)  # type: ignore
