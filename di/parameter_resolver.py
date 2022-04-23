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
    def _resolve_overrides(_: str, parameter: inspect.Parameter) -> Optional[Key]:
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

    return _resolve_overrides


def resolve_depends(_: str, parameter: inspect.Parameter) -> Optional[Key]:
    default = parameter.default
    if not isinstance(default, _Depends):
        return None

    return Key(
        resolver=default.dependency,
        use_cache=default.use_cache,
    )


class ParamResolver:
    def __init__(self, resolvers: Sequence[ParamResolverT]):
        self._resolvers: Sequence[ParamResolverT] = resolvers

    def __call__(self, name: str, parameter: inspect.Parameter) -> Optional[Key]:
        for param_resolver in self._resolvers:
            key = param_resolver(name, parameter)
            if key is not None:
                return key

        return None
