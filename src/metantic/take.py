from typing import GenericAlias, TypeVar, Any, get_args, get_origin, Union, _UnionGenericAlias
from types import UnionType
from pydantic import BaseModel, create_model, ConfigDict
import ramda as R

Model = TypeVar('Model', bound=BaseModel)
@R.curry
def Take(cls: type[Any], fields: list[str | tuple[str, list]]) -> type[Model]:
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
    if isinstance(cls, UnionType) or isinstance(cls, _UnionGenericAlias):
        args = get_args(cls)
        mapped_args = tuple(R.map(Take(fields=fields), args))
        return Union[mapped_args]
    elif isinstance(cls, GenericAlias):
        base = get_origin(cls)
        args = get_args(cls)
        mapped_args = tuple(R.map(Take(fields=fields), args))
        return base[mapped_args]
    elif issubclass(cls, BaseModel):
        def field(selector: str | tuple[str, list]) -> tuple[str, tuple[type, Any]]:
            match selector:
                case str(fld):
                    f = cls.model_fields[fld]
                    return fld, (f.annotation, f.default)
                case str(fld), list(subflds):
                    f = cls.model_fields[fld]
                    return fld, (Take(f.annotation, subflds), f.default)
                case _:
                    raise ValueError(f"Unexpected field selector '{selector}' (of type ({type(selector)})) (expected `str | tuple[str, list]`)")

        keep_fields = dict(field(s) for s in fields)
        name = f'Take{cls.__name__}'
        config = ConfigDict(extra="forbid")
        return create_model(name, __config__=config, **keep_fields)
    else:
        return cls