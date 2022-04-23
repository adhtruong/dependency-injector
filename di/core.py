import inspect
from contextlib import suppress
from typing import Any, Callable, Iterator, Optional, TypeVar, Union

from di.parameter_resolver import get_parameter_resolve

_RType = TypeVar("_RType")


class Resolver:
    def __init__(
        self,
        overrides: dict[Callable, Callable] = None,
        name_resolvers: dict[str, Callable] = None,
    ) -> None:
        self._cache: dict[Callable, Any] = {}
        self._teardowns: list[Iterator] = []
        self._param_resolver = get_parameter_resolve(overrides, name_resolvers)

    def __call__(self, f: Callable[..., _RType]) -> _RType:
        result = self._resolve(f)
        for teardown in reversed(self._teardowns):
            with suppress(StopIteration):
                next(teardown)

        self._teardowns = []

        return result

    def _resolve(self, f: Callable[..., _RType]) -> _RType:
        resolved_parameters: dict[str, Any] = {}
        for name, parameter in inspect.signature(f).parameters.items():
            key = self._param_resolver(name, parameter)
            if key is None:
                continue

            if key.use_cache and key.resolver in self._cache:
                resolved_value = self._cache[key.resolver]
            else:
                resolved_value = self._resolve(key.resolver)
                self._cache[key.resolver] = resolved_value
            resolved_parameters[name] = resolved_value

        result_generator = f(**resolved_parameters)
        resolved_value, teardown = _resolve_generator(result_generator)
        if teardown is not None:
            self._teardowns.append(teardown)

        return resolved_value


def _resolve_generator(result_generator: Union[Iterator[_RType], _RType]) -> tuple[_RType, Optional[Iterator]]:
    if isinstance(result_generator, Iterator):
        resolved_value = next(result_generator)
        return resolved_value, result_generator

    return result_generator, None


def resolve(
    f: Callable[..., _RType],
    /,
    *,
    overrides: dict[Callable, Callable] = None,
    name_resolvers: dict[str, Callable] = None,
) -> _RType:
    resolver = Resolver(overrides=overrides, name_resolvers=name_resolvers)
    return resolver(f)


def inject(f: Callable[..., _RType], /) -> Callable[..., _RType]:
    return lambda: Resolver()(f)
