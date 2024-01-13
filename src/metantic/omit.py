from typing import Literal, TypeVar
from pydantic import BaseModel, create_model

Model = TypeVar('Model', bound=BaseModel)

def Omit(model: Model, fields: list[str]) -> type[Model]:
    """`model` without `fields`"""
    keep_fields = {
        f: (a.annotation, a.default)
        for f, a in model.model_fields.items()
            if f not in fields
    }
    return create_model(f'Omit{model.__name__}', **keep_fields)
