import inspect
from contextlib import suppress
from typing import Any, Callable, Final, Iterator, Optional, TypeVar, Union

from di.parameter_resolver import get_parameter_resolve
from di.types import FactoryType, RType

DecoratedFunc = TypeVar("DecoratedFunc", bound=Callable)

_DEPENDENCIES_ATTRIBUTE: Final[str] = "__dependencies__"


def auto_use(*dependency: FactoryType) -> Callable[[DecoratedFunc], DecoratedFunc]:
    def inner(f: DecoratedFunc) -> DecoratedFunc:
        current = getattr(f, _DEPENDENCIES_ATTRIBUTE, ())
        setattr(f, _DEPENDENCIES_ATTRIBUTE, current + dependency)
        return f

    return inner


class Resolver:
    def __init__(
        self,
        overrides: dict[FactoryType, FactoryType] = None,
        name_resolvers: dict[str, FactoryType] = None,
    ) -> None:
        self._cache: dict[FactoryType, Any] = {}
        self._param_resolver = get_parameter_resolve(overrides, name_resolvers)

    def __call__(self, f: FactoryType[RType], *, use_cache: bool = True) -> RType:
        result, teardowns = self._resolve(f, use_cache, [])
        for teardown in reversed(teardowns):
            with suppress(StopIteration):
                next(teardown)

        return result

    def _resolve(
        self,
        f: FactoryType[RType],
        use_cache: bool,
        teardowns: list[Iterator],
    ) -> tuple[RType, list[Iterator]]:
        if use_cache and f in self._cache:
            return self._cache[f], teardowns

        for autouse in getattr(f, _DEPENDENCIES_ATTRIBUTE, ()):
            _, teardowns = self._resolve(
                autouse,
                True,
                teardowns,
            )

        resolved_parameters: dict[str, Any] = {}
        for name, parameter in inspect.signature(f).parameters.items():
            key = self._param_resolver(name, parameter)
            if key is None:
                continue

            resolved_value, teardowns = self._resolve(key.resolver, key.use_cache, teardowns)
            resolved_parameters[name] = resolved_value

        result_generator = f(**resolved_parameters)
        resolved_value, teardown = _resolve_generator(result_generator)
        if teardown is not None:
            teardowns.append(teardown)

        self._cache[f] = resolved_value
        return resolved_value, teardowns


def _resolve_generator(result_generator: Union[Iterator[RType], RType]) -> tuple[RType, Optional[Iterator]]:
    if isinstance(result_generator, Iterator):
        resolved_value = next(result_generator)
        return resolved_value, result_generator

    return result_generator, None


def resolve(
    f: FactoryType[RType],
    /,
    *,
    overrides: dict[Callable, Callable] = None,
    name_resolvers: dict[str, Callable] = None,
) -> RType:
    resolver = Resolver(overrides=overrides, name_resolvers=name_resolvers)
    return resolver(f)


def inject(f: FactoryType[RType], /) -> Callable[..., RType]:
    return lambda: Resolver()(f)
