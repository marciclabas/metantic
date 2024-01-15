from typing import TypeVar
from pydantic import BaseModel, create_model

Model = TypeVar('Model', bound=BaseModel)

def Partial(model: type[Model], name: str | None = None) -> type[Model]:
    """`model` but with all fields optional"""
    fields = {
        f: (a.annotation | None, None)
        for f, a in model.model_fields.items()
    }
    name = name or f'Partial{model.__name__}'
    return create_model(name, __config__=model.model_config, **fields)