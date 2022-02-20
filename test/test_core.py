from dataclasses import dataclass
from typing import Iterator, List

import pytest

from di import Depends, resolve


def test_core() -> None:
    def get_a() -> int:
        return 1

    def get_b(a: int = Depends(get_a)) -> int:
        return 1 + a

    assert resolve(get_b) == 2


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

    with pytest.raises(RuntimeError, match="Unable to resolve parameter = 'unresolved' for 'entrypoint'"):
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
