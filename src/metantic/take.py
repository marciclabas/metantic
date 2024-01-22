from typing import TypeVar, Any, get_args, get_origin
from pydantic import BaseModel, ConfigDict, create_model
import ramda as R
from . import model_type

Model = TypeVar('Model', bound=BaseModel)
def Take(model: type[Model], fields: list[str | tuple[str, list]]) -> type[Model]:
    """`model` with `fields` only
    - if `fields[i]` is a `str`, takes only that field
    - if `fields[i]` is a `tuple[str, list]`, takes that subfields recursively
    
    Example:
    ```
    class FullName(BaseModel):
        first: str; middle: str; family: str

    class User(BaseModel):
        id: str
        full_name: FullName
        friends: list[str]
        
    UserInfo = Take(User, ['id', ('full_name': ['first', 'family'])])
    
    UserInfo.model_validate({
        'id': userId,
        'full_name': {'first': first, 'family': family}
    })
    ```
    """
    model_t = model_type(model)
    assert model_t is not None, f"Invalid model '{model}' in subtype hierarchy"
    def field(selector: str | tuple[str, list]) -> tuple[str, tuple[type, Any]]:
        match selector:
            case str(fld):
                f = model_t.model_fields[fld]
                return fld, (f.annotation, f.default)
            case str(fld), list(subflds):
                f = model_t.model_fields[fld]
                return fld, (Take(f.annotation, subflds), f.default)
            case _:
                raise ValueError(f"Unexpected field selector '{selector}' (of type ({type(selector)})) (expected `str | tuple[str, list]`)")
            
    keep_fields = dict(field(s) for s in fields)
    name = f'Take{model_t.__name__}'
    config = ConfigDict(extra="forbid")
    return create_model(name, __config__=config, **keep_fields)