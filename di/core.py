import functools
import inspect
from contextlib import suppress
from email.generator import DecodedGenerator
from logging import getLogger
from typing import Any, Callable, Generic, Iterator, TypeVar, Union, overload

logger = getLogger(__name__)

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


class Resolver:
    def __init__(self) -> None:
        self._cache: dict[Callable, Any] = {}

    def __call__(self, f: Callable[..., _RType]) -> _RType:
        result, teardowns = _resolve(f, self._cache)
        for teardown in reversed(teardowns):
            with suppress(StopIteration):
                next(teardown)

        return result


DecoratedFunc = TypeVar("DecoratedFunc", bound=Callable)


def auto_use(*dependency: Callable[..., _RType]) -> Callable[[DecoratedFunc], DecoratedFunc]:
    def wrapper(f: DecoratedFunc) -> DecoratedFunc:
        f.__dependencies__ = dependency
        return f

    return wrapper


def resolve(f: Callable[..., _RType]) -> _RType:
    resolver = Resolver()
    return resolver(f)


def _resolve(f: Callable[..., _RType], cache: dict[Callable, Any]) -> tuple[_RType, list[Iterator]]:
    for dependency in getattr(f, "__dependencies__", ()):
        _resolve(dependency, cache)

    function_signature = inspect.signature(f)
    resolved_parameters: dict[str, Any] = {}
    teardowns: list[Iterator] = []
    for parameter, value in function_signature.parameters.items():
        default = value.default
        if default is inspect.Parameter.empty:
            raise RuntimeError(f"Unable to resolve {parameter = } for '{f.__name__}'")

        if not isinstance(default, _Depends):
            resolved_parameters[parameter] = default
            continue

        if default.use_cache and default.dependency in cache:
            resolved_value = cache[default.dependency]
        else:
            resolved_value, teardowns_ = _resolve(default.dependency, cache)
            teardowns.extend(teardowns_)
            cache[default.dependency] = resolved_value
        resolved_parameters[parameter] = resolved_value

    result_generator = f(**resolved_parameters)
    if isinstance(result_generator, Iterator):
        resolved_value = next(result_generator)
        teardowns.append(result_generator)
    else:
        resolved_value = result_generator

    return resolved_value, teardowns
