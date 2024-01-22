from typing import TypeVar, Annotated, Callable
from fastapi import Depends, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError

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

Model = TypeVar('Model', bound=BaseModel)
def form_json(model: type[Model], name: str):
    """`Model` as json in FormData `name`
    
    Usage:
    >>> class ParamsT(BaseModel): ...
    >>> Params = form_json(ParamsT, 'params')
    >>> @app.post("...")
    >>> def route(params: Params):
    >>>     ...
    """
    async def dep(req: Request) -> Model:
        form = await req.form()
        file = form.get(name)
        if file is None:
            raise RequestValidationError([f"Missing Form '{name}'"])
        data = file if isinstance(file, str) else await file.read()
        try:
            return model.model_validate_json(data)
        except ValidationError as e:
            raise RequestValidationError(e.errors()) from e
    return Annotated[Model, Depends(dep)]