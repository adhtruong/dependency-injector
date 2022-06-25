from dataclasses import dataclass
from typing import Iterator, List

import pytest

from di import Depends, resolve
from di.core import auto_use, inject


def test_core() -> None:
    def get_a() -> int:
        return 1

    def get_b(a: int = Depends(get_a), b: int = Depends(lambda: 0)) -> int:
        return 1 + a + b

    assert resolve(get_b) == 2


def test_inject() -> None:
    @inject
    def my_func(my_list: list = Depends(list)) -> list:
        return my_list

    results = [my_func(), my_func(), my_func()]
    assert all(result == [] for result in results)
    assert results[0] is not results[1]


def test_generator() -> None:
    teardown = False

    def my_generator() -> Iterator[int]:
        yield 1
        nonlocal teardown
        teardown = True

    def entry(a: int = Depends(my_generator)) -> int:
        return a

    assert resolve(entry) == 1
    assert teardown


def test_nested() -> None:
    calls = 0

    def my_function() -> int:
        nonlocal calls
        calls += 1
        return 1

    def my_other_function(a: int = Depends(my_function)) -> int:
        return a

    def entrypoint(a: int = Depends(my_function), b: int = Depends(my_other_function)) -> int:
        return a + b

    assert resolve(entrypoint) == 2
    assert calls == 1


def test_cache() -> None:
    calls = 0

    def my_function() -> int:
        nonlocal calls
        calls += 1
        return 1

    def entrypoint(a: int = Depends(my_function), b: int = Depends(my_function)) -> int:
        return a + b

    assert resolve(entrypoint) == 2
    assert calls == 1


def test_no_cache() -> None:
    calls = 0

    def my_function() -> int:
        nonlocal calls
        calls += 1
        return 1

    def entrypoint(a: int = Depends(my_function), b: int = Depends(my_function, use_cache=False)) -> int:
        return a + b

    assert resolve(entrypoint) == 2
    assert calls == 2


def test_exception() -> None:
    def entrypoint(unresolved: int) -> None:
        return None

    with pytest.raises(TypeError, match=r"entrypoint\(\) missing 1 required positional argument: 'unresolved'"):
        resolve(entrypoint)


def test_default_value() -> None:
    def my_function(parameter: int = 1) -> int:
        return parameter

    def entrypoint(parameter: int = Depends(my_function)) -> int:
        return parameter

    assert resolve(my_function) == 1
    assert resolve(entrypoint) == 1


def test_list_return() -> None:
    def my_function() -> List[int]:
        return [1, 2]

    def entry(param: list[int] = Depends(my_function)) -> list[int]:
        return param

    assert resolve(entry) == [1, 2]


def test_overrides() -> None:
    def my_function() -> List[int]:
        return [1, 2]

    def entry(param: list[int] = Depends(my_function)) -> list[int]:
        return param

    assert resolve(entry, overrides={my_function: lambda: [1]}) == [1]


def test_name_resolver() -> None:
    def entry(param: list[int]) -> list[int]:
        return param

    assert resolve(entry, name_resolvers={"param": lambda: [1]}) == [1]


def test_class() -> None:
    def get_str() -> str:
        return "Hello World"

    @dataclass
    class MyClass:
        a: int = 1
        b: str = Depends(get_str)

    def entry(my_class: MyClass = Depends(MyClass)) -> MyClass:
        return my_class

    assert resolve(entry) == MyClass(a=1, b="Hello World")


def test_auto_use() -> None:
    is_called: list[int] = []

    def my_dependency() -> None:
        nonlocal is_called
        is_called.append(2)

    def generator() -> Iterator[None]:
        nonlocal is_called
        is_called.append(1)
        yield
        is_called.append(3)

    @auto_use(generator, my_dependency)
    def my_function() -> None:
        return None

    resolve(my_function)
    assert is_called == [1, 2, 3]
