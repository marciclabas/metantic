from __future__ import annotations
from types import UnionType, NoneType
from typing import TypeVar, get_origin, get_args, Callable, get_type_hints, Literal, Union
from inspect import isclass
from dataclasses import dataclass
from pydantic import BaseModel
import ramda as R

@dataclass
class PathBuilder:
    path: list[str | int]
    type: type
    
    @property
    def str_path(self) -> str:
        return '/' + '/'.join(str(p) for p in self.path)

@dataclass
class ListBuilder(PathBuilder):
    _children: Callable[[int], PathBuilder]
    def __getitem__(self, idx: int) -> PathBuilder:
        return self._children(idx)
    def __repr__(self) -> str:
        return f'ListBuilder(path={self.path}, keys=int)'
    
@dataclass
class DictBuilder(PathBuilder):
    _children: Callable[[str], PathBuilder]
    def __getitem__(self, key: str | int) -> PathBuilder:
        return self._children(key)
    def __repr__(self) -> str:
        return f'DictBuilder(path={self.path}, keys=str | int)'
    
@dataclass
class TupleBuilder(PathBuilder):
    _children: tuple[PathBuilder, ...]
    def __getitem__(self, idx: int) -> PathBuilder:
        if 0 <= idx < len(self._children):
            return self._children[idx]
        else:
            raise ValueError(f"Invalid index '{idx}' after path '{self.path}'. Valid indices are {list(range(len(self._children)))}")
    def __repr__(self) -> str:
        return f'TupleBuilder(path={self.path}, keys={list(range(len(self._children)))})'
    
@dataclass
class TypedBuilder(PathBuilder):
    _children: dict[str, PathBuilder]
    def __getitem__(self, name: str) -> PathBuilder:
        if name in self._children:
            return self._children[name]
        else:
            raise ValueError(f"Invalid key '{name}' after path '{self.path}'. Valid keys are {list(self._children.keys())}")
    def __repr__(self) -> str:
        return f'TypedBuilder(path={self.path}, keys={list(self._children.keys())})'
    
T = TypeVar('T')

    
def builder(cls: type[T], path = []) -> PathBuilder:
    """
    Returns a `PathBuilder` to generate valid paths of `cls`
    - Does not support unions (paths stop recursion upon finding a union)
    
    e.g:
    
    ```
    class FullName(TypedDict):
        first: str; middle: str; family: str

    class User:
        id: str
        full_name: FullName
        friends: list[str]
        
    ps = paths(User)
    ps['id'].path # ['id']
    ps['full_name']['first'].path # ['full_name', 'first']
    ps['friends'][69].path # ['friends', 69]
    
    ps['full_name']['second'].path # ERROR
    ```
    """
    Base = get_origin(cls)
    if Base is tuple:
        children = tuple(builder(x, path+[i]) for i, x in enumerate(get_args(cls)))
        return TupleBuilder(path=path, type=cls, _children=children)
    elif Base is list:
        [U] = get_args(cls)
        return ListBuilder(path=path, type=cls, _children=lambda i: builder(U, path+[i]))
    elif Base is dict:
        [K, V] = get_args(cls)
        if K is Literal:
            return TypedBuilder(path=path, type=cls, _children={
                k: builder(V, path+[k])
                for k in K.__args__
            })
        elif K is str or K is int:
            return DictBuilder(path=path, type=cls, _children=lambda k: builder(V, path+[k])) 
        else:
            return PathBuilder(path=path, type=cls)
    elif Base is UnionType or Base is Union:
        non_none = R.filter(lambda a: a is not NoneType, get_args(cls))
        if len(non_none) == 1:
            return builder(non_none[0], path=path)
        else:
            return PathBuilder(path=path, type=cls)
    elif isclass(cls) and issubclass(cls, BaseModel):
        return TypedBuilder(path=path, type=cls, _children={
            field: builder(info.annotation, path+[field])
            for field, info in cls.model_fields.items()
        })
    elif (annotations := get_type_hints(cls)) != {}:
        return TypedBuilder(path=path, type=cls, _children={
            field: builder(ann, path+[field])
            for field, ann in annotations.items()
        })
    else:
        return PathBuilder(path=path, type=cls)
