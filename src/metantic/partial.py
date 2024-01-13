from typing import TypeVar
from pydantic import BaseModel, create_model

Model = TypeVar('Model', bound=BaseModel)

def Partial(model: type[Model]) -> type[Model]:
    """`model` but with all fields optional"""
    fields = {
        f: (t | None, None)
        for f, t in model.__annotations__.items()
    }
    return create_model(f'Partial{model.__name__}', __base__=model, **fields)