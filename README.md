# Dependency Injector

<p align="center">
    <a href="https://codecov.io/gh/adhtruong/dependency-injector">
        <img src="https://codecov.io/gh/adhtruong/dependency-injector/main/graph/badge.svg?token=4I7OINJKAO"
        style="max-width:100%;" />
    </a>
    <a href="https://github.com/psf/black">
        <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"
        style="max-width:100%;" />
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit" style="max-width:100%;" />
    </a>
</p>

---

**Documentation**: <a href="https://adhtruong.github.io/dependency-injector" target="_blank">https://adhtruong.github.io/dependency-injector</a>

**Source Code**: <a href="https://github.com/adhtruong/dependency-injector" target="_blank">https://github.com/adhtruong/dependency-injector</a>

---

Framework for dependency injection.

## Quick start

```python
from di import Depends, resolve


def get_my_number() -> int:
    return 2


def square(my_number: int = Depends(get_my_number)) -> int:
    return my_number * my_number


print(resolve(square))  # print 4

```

## Development Set Up

```bash
    pip install -r requirements-dev.txt
    pre-commit install
```

## TODO

- [ ] Add docs
- [ ] Add async support
