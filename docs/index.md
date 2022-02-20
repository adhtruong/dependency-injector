# Dependency Injector

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
