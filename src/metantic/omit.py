from typing import Literal, TypeVar
from pydantic import BaseModel, create_model, ConfigDict

Model = TypeVar('Model', bound=BaseModel)

def Omit(model: type[Model], fields: list[str], name: str | None = None) -> type[Model]:
    """`model` without `fields`"""
    keep_fields = {
        f: (a.annotation, a.default)
        for f, a in model.model_fields.items()
            if f not in fields
    }
    name = name or f'Omit{model.__name__}'
    config = ConfigDict(extra="forbid")
    return create_model(name, __config__=config, **keep_fields)
