from __future__ import annotations
from typing import get_args, get_origin, Union, _UnionGenericAlias, GenericAlias
from types import UnionType
from pydantic import BaseModel
import ramda as R

@R.curry
def At(cls: type, path: list[str|int]) -> type | None:
    """Get the type at a given path
    - Supports paths across `BaseModel`, `list`, `tuple` and `dict`
    """
    if path == []:
        return cls
    
    [key, *keys] = path
    if isinstance(cls, UnionType) or isinstance(cls, _UnionGenericAlias):
        args = get_args(cls)
        types = tuple(R.map(At(path=path), args))
        return Union[types]
    elif isinstance(cls, GenericAlias):
        base = get_origin(cls)
        args = get_args(cls)
        if base is list and str(key).isdecimal():
            return At(args[0], keys)
        elif base is tuple and str(key).isdecimal() and int(key) < len(args):
            return At(args[int(key)], keys)
        elif base is dict and isinstance(key, str):
            return At(args[1], keys)
    elif issubclass(cls, BaseModel):
        if key in cls.model_fields:
            return At(cls.model_fields[key].annotation, keys)
    