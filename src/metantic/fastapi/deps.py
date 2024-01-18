from typing import TypeVar, Annotated, Callable
from fastapi import Depends

T = TypeVar('T', bound=Annotated)
U = TypeVar('U')
def depmap(Dep: type[T], NewDep: type[U], f: Callable[[T], U]) -> type[U]:
    """Return a new dependency resulting of applying `f` to `Dep`
    - `Dep`: dependency (an `Annotated` type)
    - `f`: mapper function
    - `NewDep`: type of resulting dependency
    """
    def mapped(d: Dep):
        return f(d)
    return Annotated[NewDep or U, Depends(mapped)]