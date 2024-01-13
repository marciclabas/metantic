from typing import Literal, TypeVar
from pydantic import BaseModel

Model = TypeVar('Model', bound=BaseModel)

def Fields(model: type[Model]) -> Literal:
    fields = tuple(model.model_fields.keys())
    return Literal[fields]