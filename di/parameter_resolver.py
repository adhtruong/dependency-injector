import inspect
from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from di.depends import _Depends


@dataclass(frozen=True)
class Key:
    resolver: Callable
    use_cache: bool


ParamResolverT = Callable[[str, inspect.Parameter], Optional[Key]]


def get_overrides(overrides: dict[Callable, Callable]) -> ParamResolverT:
    def inner(_: str, parameter: inspect.Parameter) -> Optional[Key]:
        default = parameter.default
        if not isinstance(default, _Depends):
            return None

        dependency = default.dependency
        if dependency not in overrides:
            return None

        return Key(
            resolver=overrides[default.dependency],
            use_cache=default.use_cache,
        )

    return inner


def get_name_resolver(names_resolvers: dict[str, Callable]) -> ParamResolverT:
    def inner(name: str, _: inspect.Parameter) -> Optional[Key]:
        if name not in names_resolvers:
            return None

        return Key(
            resolver=names_resolvers[name],
            use_cache=True,
        )

    return inner


def resolve_depends(_: str, parameter: inspect.Parameter) -> Optional[Key]:
    default = parameter.default
    if not isinstance(default, _Depends):
        return None

    return Key(
        resolver=default.dependency,
        use_cache=default.use_cache,
    )


class ParamResolver:
    def __init__(self, *resolvers: ParamResolverT):
        self._resolvers: Sequence[ParamResolverT] = resolvers

    def __call__(self, name: str, parameter: inspect.Parameter) -> Optional[Key]:
        for param_resolver in self._resolvers:
            key = param_resolver(name, parameter)
            if key is not None:
                return key

        return None


def get_parameter_resolve(
    overrides: dict[Callable, Callable] = None,
    name_resolvers: dict[str, Callable] = None,
) -> ParamResolver:
    if overrides is None:
        overrides = {}

    if name_resolvers is None:
        name_resolvers = {}

    return ParamResolver(
        get_overrides(overrides),
        resolve_depends,
        get_name_resolver(name_resolvers),
    )
